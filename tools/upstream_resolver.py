#!/usr/bin/env python3
"""Upstream version resolver for the autoupdate bot.

Reads `packages/<name>/upstream` file paths on stdin (one per line),
resolves each source's latest version, and writes one file per package
into the directory given as argv[1] with the exact TSV contract the
autoupdate orchestration consumes:

    latest\t<pkg>\t<version>[\t<sha>]

The trailing sha field only appears for commit:-tracked packages. GitHub
Actions annotations (::warning / ::notice) go to stdout, mirroring the
bash resolver's vocabulary.

Source forms (semantics inherited verbatim from the bash resolver):
    owner/repo          GitHub releases/latest, falling back to the newest
                        tag when the repo has no Releases
    tags:owner/repo     newest version-shaped git tag (ls-remote, forge-
                        agnostic; gitlab:/codeberg:/forgejo: subprefixes)
    commit:owner/repo   HEAD commit of the default branch; version is the
                        commit date YYYY.MM.DD, plus the sha for the bump
                        to rewrite the _service pin
    npm:<package>       npm dist-tag latest
    gitlab:o/r          GitLab releases, falling back to tags
    codeberg:/forgejo:  Codeberg (or FORGEJO_HOME) releases, falling back
                        to tags

All parsing lives in pure functions (unit-tested without network); only
resolve() performs I/O.
"""
import json
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


def normalize(tag):
    """Final normalization shared by every resolver path: strip a leading
    v and keep the version part of component-prefixed tags
    (openai/codex's rust-v0.163.0)."""
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


def json_field(body, pattern):
    """Extract the first JSON string field matching a compact-JSON regex
    (single-line responses; never per-line awk-style parsing)."""
    m = re.search(pattern, body)
    return m.group(1) if m else ""


def parse_commit(body):
    """: (sha, YYYY.MM.DD) from a GitHub commit payload, else ("", "")."""
    sha = json_field(body, r'"sha": ?"([0-9a-f]{40})"')
    date = json_field(body, r'"([0-9]{4}-[0-9]{2}-[0-9]{2})T')
    return sha, date.replace("-", ".") if date else ""


class Http:
    """GET with the resolver's auth/retry conventions (hiccups must not
    fail the whole run; growing backoff). REQ/RETRY stats go to the file
    named by RESOLVER_STATS (same TSV the bash rate-summary reads)."""

    def __init__(self):
        self.github_auth = ()
        if os.environ.get("GITHUB_TOKEN"):
            self.github_auth = (("Authorization",
                                 "Bearer " + os.environ["GITHUB_TOKEN"]),)

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


def resolve(upstream_file, http):
    pkg = os.path.basename(os.path.dirname(upstream_file))
    source = open(upstream_file).read().strip()

    def get(url, headers=()):
        return http.get(url, headers, pkg=pkg)


    def w(msg):
        print(f"::warning::{pkg}: {msg}")

    def out(version, sha=""):
        return version, sha

    if source.startswith("tags:"):
        repo_url = source[len("tags:"):]
        if repo_url.startswith("gitlab:"):
            repo_url = "https://gitlab.com/" + repo_url[len("gitlab:"):]
        elif repo_url.startswith("codeberg:"):
            repo_url = "https://codeberg.org/" + repo_url[len("codeberg:"):]
        elif repo_url.startswith("forgejo:"):
            repo_url = FORGEJO_HOME + "/" + repo_url[len("forgejo:"):]
        else:
            repo_url = "https://github.com/" + repo_url
        version = first_version_tag(ls_remote_tags(repo_url))
        if not version:
            w(f"could not resolve latest tag of {source}")
            return None
        return out(version)

    if source.startswith("commit:"):
        repo = source[len("commit:"):]
        body = get(f"https://api.github.com/repos/{repo}/commits/HEAD",
                        http.github_auth)
        sha, version = parse_commit(body)
        if sha and version:
            return out(version, sha)
        w(f"could not resolve HEAD commit of {repo}")
        return None

    if source.startswith("npm:"):
        slug = source[len("npm:"):].replace("/", "%2f")
        version = json_field(get(
            f"https://registry.npmjs.org/{slug}/latest"),
            r'"version": ?"([^"]*)"')
        if version:
            return out(version)
        w(f"could not resolve latest release of {source}")
        return None

    if source.startswith("gitlab:"):
        proj = source[len("gitlab:"):].replace("/", "%2f")
        headers = (("PRIVATE-TOKEN", os.environ["GITLAB_TOKEN"]),) \
            if os.environ.get("GITLAB_TOKEN") else ()
        version = json_field(get(
            f"https://gitlab.com/api/v4/projects/{proj}/releases", headers),
            r'"tag_name": ?"([^"]*)"').lstrip("v")
        if not version:
            version = json_field(get(
                f"https://gitlab.com/api/v4/projects/{proj}"
                f"/repository/tags?per_page=1", headers),
                r'"name": ?"([^"]*)"').lstrip("v")
        if version:
            return out(normalize(version))
        w(f"could not resolve latest release of {source}")
        return None

    if source.startswith(("codeberg:", "forgejo:")):
        src = source.split(":", 1)[1]
        base = FORGEJO_API if source.startswith("forgejo:") \
            else "https://codeberg.org/api/v1"
        version = json_field(get(
            f"{base}/repos/{src}/releases?limit=1", gh),
            r'"tag_name": ?"([^"]*)"').lstrip("v")
        if not version:
            version = json_field(get(
                f"{base}/repos/{src}/tags?limit=1", gh),
                r'"name": ?"([^"]*)"').lstrip("v")
        if version:
            return out(normalize(version))
        w(f"could not resolve latest release of {source}")
        return None

    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source):
        version = json_field(get(
            f"https://api.github.com/repos/{source}/releases/latest", gh),
            r'"tag_name": ?"([^"]*)"').lstrip("v")
        if not version:
            # tag-only repos (no GitHub Releases): newest tag fallback
            version = json_field(get(
                f"https://api.github.com/repos/{source}/tags?per_page=1", gh),
                r'"name": ?"([^"]*)"').lstrip("v")
            if version:
                print(f"::notice::[tags-fallback] pkg={pkg} source={source} "
                      f"resolved={version} (no GitHub Releases; "
                      f"releases/latest is re-checked every run)")
        if version:
            return out(normalize(version))
        w(f"could not resolve latest release of {source}")
        return None

    w(f"unrecognized upstream source: {source}")
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
