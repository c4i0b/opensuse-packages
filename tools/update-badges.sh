#!/usr/bin/env bash
# Refresh OBS status artifacts (port of the fedora-packages badges model):
#   badges/*.json — shields.io endpoint JSON (per-repo semaphores, packages count,
#                   per-package build state at the repo's current version)
#   README.md     — the marked badge blocks
# Data source: the OBS /build/<project>/_result endpoint (basic auth).
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
project="${OBS_PROJECT:-home:caiobruno}"
api="${OBS_API:-https://api.opensuse.org}"

python3 - "$root" "$project" "$api" <<'PY'
import os, re, sys, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

root, project, api = sys.argv[1:4]
# CI passes OBS_USER/OBS_PASSWORD; locally the tooling container mounts the
# host's ~/.oscrc instead — fall back to it so `bash tools/update-badges.sh`
# runs without exporting anything
if "OBS_USER" in os.environ and "OBS_PASSWORD" in os.environ:
    user = os.environ["OBS_USER"]
    password = os.environ["OBS_PASSWORD"]
else:
    import configparser
    cp = configparser.ConfigParser()
    cp.read(os.path.expanduser("~/.oscrc"))
    user = cp.get(api, "user")
    password = cp.get(api, "pass")

BADGE_REV = 2  # kept for format stability; the content hash below is the
               # real cache-buster — BADGE_REV alone no longer needs bumping

def badge_rev(payload):
    # cheap state component for the ?v= cache-buster: a badge JSON change
    # without a version change (color flip failed→passing at the same
    # version) changes the hash, so GitHub camo re-fetches the URL
    import hashlib
    return hashlib.sha256(payload.encode()).hexdigest()[:8]

def get(url, tries=3):
    # OBS API hiccups must not fail the whole refresh (fedora-packages
    # pattern: retry with growing backoff)
    import time
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url)
            import base64
            tok = base64.b64encode(f"{user}:{password}".encode()).decode()
            req.add_header("Authorization", f"Basic {tok}")
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(2 * (attempt + 1))

tree = ET.fromstring(get(f"{api}/build/{project}/_result"))

# repo/arch -> package -> status code
cells = {}
for result in tree.findall("result"):
    repo = result.get("repository")
    arch = result.get("arch")
    for status in result.findall("status"):
        cells.setdefault((repo, arch), {})[status.get("package")] = status.get("code")

BAD = {"failed", "broken"}
INFLIGHT = {"scheduled", "building", "sign", "dispatching", "blocked", "waiting"}

badges = Path(root) / "badges"
badges.mkdir(exist_ok=True)

def write_badge(fname, label, message, color):
    import json
    payload = json.dumps({"schemaVersion": 1, "label": label,
                          "message": message, "color": color}) + "\n"
    with open(badges / f"{fname}.json", "w") as f:
        f.write(payload)
    return badge_rev(payload)

# ---- repo semaphores (fedora-packages chroot-badge model) -----------------
# arch joins the file name/label only when a repo builds more than one arch
arches_by_repo = {}
for (repo, arch) in cells:
    arches_by_repo.setdefault(repo, set()).add(arch)

def bname(repo, arch):
    return f"{repo.replace('_', '-')}-{arch}" if len(arches_by_repo[repo]) > 1 \
        else repo.replace('_', '-').removeprefix('opensuse-')

def blabel(repo, arch):
    txt = repo.replace('_', ' ').replace('opensuse tumbleweed', 'tumbleweed') \
              .replace('opensuse slowroll', 'slowroll')
    return f"{txt} {arch}" if len(arches_by_repo[repo]) > 1 else txt

repo_lines = []
for (repo, arch), pkgs in sorted(cells.items()):
    ok = sum(c not in BAD and c not in INFLIGHT for c in pkgs.values())
    bad = sum(c in BAD for c in pkgs.values())
    inflight = sum(c in INFLIGHT for c in pkgs.values())
    color = "red" if bad else ("yellow" if inflight else "brightgreen")
    # ok alone: the packages badge below carries the totals; the color is
    # the failure/in-flight signal
    fname, label = bname(repo, arch), blabel(repo, arch)
    rev = write_badge(fname, label, str(ok), color)
    repo_lines.append(
        f'[![{label}](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com'
        f'%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2F{fname}.json%3Fv%3D{rev}r{BADGE_REV})]'
        f'(https://build.opensuse.org/project/monitor?project={project.replace(":", "%3A")})')

# packages count badge opens the block (fedora-packages model)
all_pkgs = {p for pkgs in cells.values() for p in pkgs}
rev = write_badge("packages", "packages", str(len(all_pkgs)), "blue")
repo_lines.insert(0,
    f'[![packages](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com'
    f'%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpackages.json%3Fv%3D{rev}r{BADGE_REV})]'
    f'(https://build.opensuse.org/project/monitor?project={project.replace(":", "%3A")})')

# ---- per-package state at the repo's current version ----------------------
# only git-tracked packages: untracked WIP has never reached OBS and would
# render a misleading green badge
tracked = set(
    os.popen("git -C \"" + root + "\" ls-files -- packages")
      .read().split())
tracked_pkgs = {p.split("/")[1] for p in tracked if p.count("/") >= 2}

def spec_version(spec):
    for line in spec.read_text().splitlines():
        m = re.match(r"^Version:\s+(\S+)", line)
        if m:
            return m.group(1)
    return "?"

def upstream_link(pkg_dir):
    up = pkg_dir / "upstream"
    if up.exists():
        src = up.read_text().strip()
        src = re.sub(r"^tags:", "", src)
        if not src.startswith(("npm:", "http")) and "/" in src:
            return f"https://github.com/{src}/"
    for spec in pkg_dir.glob("*.spec"):
        for line in spec.read_text().splitlines():
            m = re.match(r"^URL:\s+(\S+)", line)
            if m:
                return m.group(1)
    return f"https://build.opensuse.org/package/show/{project}/{pkg_dir.name}"

pkg_lines = []
written = set()
for pkg_dir in sorted(Path(root, "packages").iterdir()):
    if not pkg_dir.is_dir() or not list(pkg_dir.glob("*.spec")):
        continue
    if pkg_dir.name not in tracked_pkgs:
        continue
    states = [c for pkgs in cells.values() for p, c in pkgs.items() if p == pkg_dir.name]
    ver = spec_version(next(pkg_dir.glob("*.spec")))
    if any(s in BAD for s in states):
        color, msg = "red", "failed"
    elif any(s in INFLIGHT for s in states):
        color, msg = "yellow", "building"
    else:
        color, msg = "brightgreen", f"v{ver}"
    rev = write_badge(pkg_dir.name, pkg_dir.name, msg, color)
    written.add(pkg_dir.name)
    link = upstream_link(pkg_dir)
    pkg_lines.append(
        f'[![{pkg_dir.name}](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com'
        f'%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2F{pkg_dir.name}.json%3Fv%3D{rev}r{BADGE_REV})]({link})')

# prune stale badges in one sweep: anything not written this run (repo,
# packages or per-package) is gone from OBS and must not linger (red: the
# aarch64 repo badge had to be deleted by hand after the arch drop)
expected = {"packages"} | {bname(r, a) for (r, a) in cells} | written
for old in badges.glob("*.json"):
    if old.stem not in expected:
        old.unlink()

# ---- README blocks ---------------------------------------------------------
readme = Path(root, "README.md")
text = readme.read_text()

def replace_block(text, marker, lines):
    begin, end = f"<!-- {marker} begin -->", f"<!-- {marker} end -->"
    if begin not in text or end not in text:
        sys.exit(f"README.md is missing the {begin}...{end} block")
    pre, rest = text.split(begin, 1)
    _, post = rest.split(end, 1)
    return pre + begin + "\n" + "\n".join(lines) + "\n" + end + post

text = replace_block(text, "repo-badges", repo_lines)
text = replace_block(text, "package-badges", pkg_lines)

# build-status: failures table + an Updated timestamp that only moves when
# the status itself changed (last-STATE-CHANGE, the fedora-packages model).
# The essence compare drops the WHOLE timestamp line: a bare text sub
# leaves stray '*' making every refresh look like a state change.
from datetime import datetime, timezone

obs_pkg = f"https://build.opensuse.org/package/show/{project}"
failing = {}
for (repo, arch), pkgs in cells.items():
    for p, code in pkgs.items():
        if code in BAD and p in tracked_pkgs:
            failing.setdefault(p, []).append((repo, arch, code))

rows = []
for p in sorted(failing):
    archs = "<br>".join(
        f"{repo.replace('_', ' ').replace('opensuse tumbleweed', 'tumbleweed')}"
        f" {arch}: {code}"
        for repo, arch, code in sorted(failing[p]))
    rows.append(f"| {p} | {archs} | [package]({obs_pkg}/{p}) |")
body = (("### :x: build failures\n\n"
         "| package | repos | OBS |\n|---|---|---|\n" + "\n".join(rows) + "\n")
        if rows else "")

def essence(t):
    t = re.sub(r"^.*Updated [0-9-]+ [0-9:]+ UTC.*$", "", t, flags=re.M)
    return "\n".join(l for l in t.split("\n") if l.strip()).strip()

begin, end = "<!-- build-status begin -->", "<!-- build-status end -->"
if begin not in text or end not in text:
    sys.exit(f"README.md is missing the {begin}...{end} block")
pre, rest = text.split(begin, 1)
current, post = rest.split(end, 1)
if essence(current) == essence(body):
    block = current.strip("\n")  # unchanged status keeps its timestamp
else:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    block = (body.rstrip() + "\n" if body else "") + f"\n*Updated {ts} UTC*"
text = pre + begin + "\n" + block + "\n" + end + post

readme.write_text(text)
print(f"badges refreshed: {len(repo_lines)} repo-arch, {len(pkg_lines)} packages, "
      f"{len(failing)} failing")
PY
