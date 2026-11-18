#!/usr/bin/env python3
"""Upstream version resolver for the autoupdate bot.

Reads `packages/<name>/upstream` file paths on stdin (one per line),
resolves each source's latest version, and writes one file per package
into the directory given as argv[1] with the exact TSV contract the
autoupdate orchestration consumes:

    latest\t<pkg>\t<version>[\t<sha>]

The trailing sha field only appears for commit:-tracked packages. GitHub
Actions annotations (::warning / ::notice) go to stdout.

Source forms, parsed by parse_source() into (kind, forge, ident):

    owner/repo            (github) releases, tags fallback
    gitlab:o/r            GitLab releases, tags fallback
    codeberg:o/r          Codeberg (Gitea API) releases, tags fallback
    forgejo:o/r           Forgejo at FORGEJO_API, same as codeberg
    tags:<[forge:]o/r>    newest version-shaped git tag (ls-remote,
                          forge-agnostic, zero API quota)
    commit:<[forge:]o/r>  HEAD commit date as version (YYYY.MM.DD) plus
                          the sha, for upstreams with no releases and no
                          tags; bump also rewrites the _service sha pin
    npm:<package>         npm dist-tag latest

Forge knowledge lives ONLY in the FORGES registry: adding a forge is one
entry, not edits scattered through the dispatch. All parsing lives in
pure functions (unit-tested without network); only the registry's
resolvers and resolve() perform I/O.
"""
import os
import re
import subprocess
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor

FORGEJO_HOME = os.environ.get("FORGEJO_HOME", "https://codeberg.org")
FORGEJO_API = os.environ.get("FORGEJO_API", "https://codeberg.org/api/v1")

# a resolvable release must be version-shaped once sanitized; RPM forbids
# '-' in Version (the bump stage replaces [- ] with '.')
TAG_SHAPE = re.compile(r"^[0-9][A-Za-z0-9._+~-]*$")
PREFIXED = re.compile(r"^.+-v([0-9])")
BARE_SOURCE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


# ---- pure helpers ---------------------------------------------------------

def normalize(tag):
    """Strip a leading v and keep the version part of component-prefixed
    tags (openai/codex's rust-v0.163.0)."""
    tag = tag.lstrip("v")
    m = PREFIXED.match(tag)
    return m.group(1) + tag[m.end():] if m else tag


def first_version_tag(tags):
    """tags: pass — strict first, prefix-stripped second.

    Strict pass: plain v<version> tags only. Component tags
    (anomalyco/opencode's vscode-v1.0.0) pollute the prefix-stripped
    pass and resolve as downgrades, so they only apply when no plain tag
    exists anywhere in the (version-sorted) list."""
    for t in tags:
        v = t.lstrip("v")
        if TAG_SHAPE.match(v):
            return v
    for t in tags:
        v = PREFIXED.sub(r"\1", t)
        if TAG_SHAPE.match(v):
            return v
    return ""


def json_field(body, pattern):
    """Extract the first JSON string field matching a compact-JSON regex
    (single-line responses; never per-line awk-style parsing)."""
    m = re.search(pattern, body)
    return m.group(1) if m else ""


def parse_source(source):
    """: (kind, forge, ident) with kind in
    {releases, tags, commit, npm, unknown}. The bare owner/repo form is
    GitHub; forge-prefixed forms carry their forge through."""
    for prefix in ("tags:", "commit:", "npm:"):
        if source.startswith(prefix):
            rest = source[len(prefix):]
            if prefix != "npm:":
                forge, ident = split_forge(rest)
                return prefix[:-1], forge, ident
            return "npm", "npm", rest
    if source.startswith(("gitlab:", "codeberg:", "forgejo:")):
        forge, ident = split_forge(source)
        return "releases", forge, ident
    if BARE_SOURCE.match(source):
        return "releases", "github", source
    return "unknown", "", source


def split_forge(rest):
    """: (forge, ident) from an optionally forge-prefixed rest, GitHub
    being the default."""
    for f in ("gitlab", "codeberg", "forgejo"):
        if rest.startswith(f + ":"):
            return f, rest[len(f) + 1:]
    return "github", rest


def date_to_version(date):
    """: YYYY.MM.DD from ISO-8601's leading date, '' otherwise."""
    m = re.match(r"^([0-9]{4}-[0-9]{2}-[0-9]{2})", date or "")
    return m.group(1).replace("-", ".") if m else ""


def parse_github_commit(body):
    """: (sha, version) from a GitHub commit payload, else ("", "")."""
    sha = json_field(body, r'"sha": ?"([0-9a-f]{40})"')
    return sha, date_to_version(json_field(body, r'"([0-9]{4}-[0-9]{2}-[0-9]{2})T'))


def parse_commit_list(body):
    """: (sha, version) from the FIRST element of a commit-list payload
    (GitLab /repository/commits and Gitea /repos/../commits both return
    newest-first arrays), else ("", ""). GitLab's list names the sha
    "id"; Gitea's names it "sha"."""
    sha = json_field(body, r'"(?:sha|id)": ?"([0-9a-f]{40})"')
    date = (json_field(body, r'"committed_date": ?"([^"]*)"')
            or json_field(body, r'"created_at": ?"([^"]*)"')
            or json_field(body, r'"created": ?"([^"]*)"')
            or json_field(body, r'"date": ?"([^"]*)"'))
    return sha, date_to_version(date)


# ---- I/O ------------------------------------------------------------------

def ls_remote_tags(repo_url):
    """Newest-first tag names from git ls-remote (server-side version
    sort; annotated-tag deref ^{} lines skipped)."""
    try:
        out = subprocess.run(
            ["git", "ls-remote", "--tags", "--sort=-v:refname", repo_url],
            capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return []
    return [l.split("refs/tags/", 1)[1] for l in out.splitlines()
            if "refs/tags/" in l and "^{}" not in l]


class Http:
    """GET with the resolver's auth/retry conventions (hiccups must not
    fail the whole run; growing backoff). REQ stats go to the file named
    by RESOLVER_STATS (same TSV the bash rate-summary reads)."""

    def __init__(self):
        self.headers = {
            "github": (("Authorization", "Bearer " + os.environ["GITHUB_TOKEN"]),)
            if os.environ.get("GITHUB_TOKEN") else (),
            "gitlab": (("PRIVATE-TOKEN", os.environ["GITLAB_TOKEN"]),)
            if os.environ.get("GITLAB_TOKEN") else (),
        }

    def _stat(self, pkg, code, attempt, rlrem):
        path = os.environ.get("RESOLVER_STATS")
        if path:
            with open(path, "a") as fh:
                fh.write(f"REQ\t{pkg}\t{code}\t{attempt}\t{rlrem}\n")

    def get(self, url, headers=(), tries=3, pkg="-"):
        last = None
        for attempt in range(1, tries + 1):
            try:
                req = urllib.request.Request(url)
                for k, v in headers:
                    req.add_header(k, v)
                try:
                    with urllib.request.urlopen(req, timeout=60) as r:
                        self._stat(pkg, r.status, attempt,
                                   r.headers.get("x-ratelimit-remaining", "-"))
                        return r.read().decode(errors="replace")
                except urllib.error.HTTPError as e:
                    self._stat(pkg, e.code, attempt,
                               e.headers.get("x-ratelimit-remaining", "-"))
                    raise
            except Exception as e:
                last = e
        raise last


# ---- forge registry -------------------------------------------------------
# Every entry: clone base for tags:, release/tag/commit endpoints for the
# bare forms. Adding a forge = adding one entry here.

FORGES = {
    "github": {
        "base": "https://github.com/{}",
        "auth": lambda h: h.headers["github"],
        "releases": "https://api.github.com/repos/{i}/releases/latest",
        "releases_field": r'"tag_name": ?"([^"]*)"',
        "tags": "https://api.github.com/repos/{i}/tags?per_page=1",
        "tags_field": r'"name": ?"([^"]*)"',
        "commit": "https://api.github.com/repos/{i}/commits/HEAD",
        "parse_commit": parse_github_commit,
    },
    "gitlab": {
        "base": "https://gitlab.com/{}",
        "auth": lambda h: h.headers["gitlab"],
        "releases": "https://gitlab.com/api/v4/projects/{e}/releases",
        "releases_field": r'"tag_name": ?"([^"]*)"',
        "tags": "https://gitlab.com/api/v4/projects/{e}"
                "/repository/tags?per_page=1",
        "tags_field": r'"name": ?"([^"]*)"',
        "commit": "https://gitlab.com/api/v4/projects/{e}"
                  "/repository/commits?per_page=1",
        "parse_commit": parse_commit_list,
    },
    "codeberg": {
        "base": "https://codeberg.org/{}",
        "auth": lambda h: (),
        "releases": "https://codeberg.org/api/v1/repos/{i}/releases?limit=1",
        "releases_field": r'"tag_name": ?"([^"]*)"',
        "tags": "https://codeberg.org/api/v1/repos/{i}/tags?limit=1",
        "tags_field": r'"name": ?"([^"]*)"',
        "commit": "https://codeberg.org/api/v1/repos/{i}/commits?limit=1",
        "parse_commit": parse_commit_list,
    },
    "forgejo": {
        "base": FORGEJO_HOME + "/{}",
        "auth": lambda h: (),
        "releases": FORGEJO_API + "/repos/{i}/releases?limit=1",
        "releases_field": r'"tag_name": ?"([^"]*)"',
        "tags": FORGEJO_API + "/repos/{i}/tags?limit=1",
        "tags_field": r'"name": ?"([^"]*)"',
        "commit": FORGEJO_API + "/repos/{i}/commits?limit=1",
        "parse_commit": parse_commit_list,
    },
}

# URL templates with {i} take the plain ident; {e} takes the forge's
# URL-encoded form (GitLab project paths escape every '/')
ENCODERS = {
    "gitlab": lambda i: i.replace("/", "%2f"),
    "github": lambda i: i,
    "codeberg": lambda i: i,
    "forgejo": lambda i: i,
}


def forge_releases(forge, ident, pkg, http):
    f = FORGES[forge]
    enc = ENCODERS[forge](ident)
    version = json_field(http.get(
        f["releases"].format(i=ident, e=enc), f["auth"](http), pkg=pkg),
        f["releases_field"]).lstrip("v")
    if not version:
        version = json_field(http.get(
            f["tags"].format(i=ident, e=enc), f["auth"](http), pkg=pkg),
            f["tags_field"]).lstrip("v")
        if version and forge == "github":
            print(f"::notice::[tags-fallback] pkg={pkg} source={forge}:{ident} "
                  f"resolved={version} (no releases; the releases endpoint "
                  f"is re-checked every run)")
    return normalize(version) if version else ""


def forge_commit(forge, ident, pkg, http):
    f = FORGES[forge]
    enc = ENCODERS[forge](ident)
    try:
        sha, version = f["parse_commit"](http.get(
            f["commit"].format(i=ident, e=enc), f["auth"](http), pkg=pkg))
    except Exception:
        return "", ""
    return (version, sha) if sha and version else ("", "")


# ---- dispatch -------------------------------------------------------------

def resolve(upstream_file, http):
    pkg = os.path.basename(os.path.dirname(upstream_file))
    source = open(upstream_file).read().strip()
    kind, forge, ident = parse_source(source)

    def w(msg):
        print(f"::warning::{pkg}: {msg}")

    if kind == "unknown":
        w(f"unrecognized upstream source: {source}")
        return None

    if kind == "tags":
        version = first_version_tag(
            ls_remote_tags(FORGES[forge]["base"].format(ident)))
        if not version:
            w(f"could not resolve latest tag of {source}")
            return None
        return version, ""

    if kind == "commit":
        version, sha = forge_commit(forge, ident, pkg, http)
        if not sha:
            w(f"could not resolve HEAD commit of {forge}:{ident}")
            return None
        return version, sha

    if kind == "npm":
        slug = ident.replace("/", "%2f")
        version = json_field(http.get(
            f"https://registry.npmjs.org/{slug}/latest", pkg=pkg),
            r'"version": ?"([^"]*)"')
        if version:
            return version, ""
        w(f"could not resolve latest release of {source}")
        return None

    # releases
    version = forge_releases(forge, ident, pkg, http)
    if version:
        return version, ""
    w(f"could not resolve latest release of {source}")
    return None


def main():
    resolved_dir = sys.argv[1]
    files = [l.strip() for l in sys.stdin if l.strip()]
    http = Http()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda f: (f, resolve(f, http)), files))
    for f, r in results:
        if r is None:
            continue
        pkg = os.path.basename(os.path.dirname(f))
        version, sha = r
        line = f"latest\t{pkg}\t{version}"
        if sha:
            line += f"\t{sha}"
        with open(os.path.join(resolved_dir, pkg), "w") as fh:
            fh.write(line + "\n")


if __name__ == "__main__":
    main()
