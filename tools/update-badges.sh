#!/usr/bin/env bash
# Refresh OBS status artifacts (port of the fedora-packages badges model):
#   badges/*.json — shields.io endpoint JSON (per repo-arch semaphores,
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
user = os.environ["OBS_USER"]
password = os.environ["OBS_PASSWORD"]

BADGE_REV = 2  # bump to force GitHub camo to re-fetch every badge URL

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
    with open(badges / f"{fname}.json", "w") as f:
        json.dump({"schemaVersion": 1, "label": label,
                   "message": message, "color": color}, f)
        f.write("\n")

# ---- repo-arch semaphores --------------------------------------------------
repo_lines = []
for (repo, arch), pkgs in sorted(cells.items()):
    ok = sum(c not in BAD and c not in INFLIGHT for c in pkgs.values())
    bad = sum(c in BAD for c in pkgs.values())
    inflight = sum(c in INFLIGHT for c in pkgs.values())
    color = "red" if bad else ("yellow" if inflight else "brightgreen")
    state = "failed" if bad else ("building" if inflight else "passing")
    fname = f"{repo.replace('_', '-')}-{arch}"
    label = f"{repo.replace('_', ' ').replace('opensuse tumbleweed', 'tumbleweed')} {arch}"
    write_badge(fname, label, f"{ok}/{len(pkgs)} {state}", color)
    repo_lines.append(
        f'[![{label}](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com'
        f'%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2F{fname}.json%3Fv%3D{ok}r{BADGE_REV})]'
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
    write_badge(pkg_dir.name, pkg_dir.name, msg, color)
    written.add(pkg_dir.name)
    link = upstream_link(pkg_dir)
    pkg_lines.append(
        f'[![{pkg_dir.name}](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com'
        f'%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2F{pkg_dir.name}.json%3Fv%3D{ver}r{BADGE_REV})]({link})')

# prune badges of packages that no longer exist (kept one refresh after a
# package is removed, the next run drops the stale json)
for old in badges.glob("*.json"):
    if old.stem not in written and not old.stem.startswith("opensuse-tumbleweed"):
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
readme.write_text(text)
print(f"badges refreshed: {len(repo_lines)} repo-arch, {len(pkg_lines)} packages")
PY
