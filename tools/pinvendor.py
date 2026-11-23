#!/usr/bin/env python3
"""Client-side vendoring for craft-family apps (dup-pinned overlay).

- cargo vendor --locked into vendor-deps/
- on duplicate git crate+version (the same crate reachable from one git
  repo at two revs — cargo's registry mode tolerates it, the vendored
  source does not): rewrite every reference to the older rev into the
  newer one across the tree's Cargo.toml + Cargo.lock (URL ?rev=
  identity included) and retry. Alternatives that do NOT work:
  a [patch] path entry (cargo >= 1.99 refuses to resolve the patched
  crate's nested workspace inheritance; virtual workspace roots are
  rejected outright) and a [patch] git entry ("patches must point to
  different sources"). red: effectcraft 0.25.1, pdfcraft 0.22.0.
- drop [patch.crates-io] git entries whose crate is not in the graph
  (cargo validates every patch entry offline and would abort)
Output overlay root: vendor-deps/, .cargo/config.toml, patched
Cargo.toml, Cargo.lock — packed as vendor.tar.zst by the caller.
"""
import re
import subprocess
import sys
from pathlib import Path

WS = Path(sys.argv[1])


def log(m):
    print(f"pinvendor: {m}", file=sys.stderr, flush=True)


def vendor(locked):
    cmd = ["cargo", "vendor"] + (["--locked"] if locked else []) + ["vendor-deps"]
    return subprocess.run(cmd, cwd=WS, capture_output=True, text=True)


def dup_sources(stderr_text):
    m = re.search(
        r"found duplicate version of package `([A-Za-z0-9_.-]+ v\S+)` "
        r"vendored from two sources:\s*\n\s*source 1: (\S+?)\?rev=([0-9a-f]+)#\S*\s*\n"
        r"\s*source 2: (\S+?)\?rev=([0-9a-f]+)#\S*", stderr_text)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)


def dedup_lock(text):
    """After the rev rewrite, two [[package]] blocks can collide on
    name+version+source (cargo refuses to parse such a lock)."""
    blocks = re.split(r"(?m)(?=^\[\[package\]\])", text)
    seen, out = set(), []
    for b in blocks:
        m = re.search(r'^name = "(.+)"\s*\n^version = "(.+)"\s*\n^source = "(.+)"',
                      b, re.M)
        if m:
            key = tuple(m.groups())
            if key in seen:
                continue
            seen.add(key)
        out.append(b)
    return "".join(out)


def collect_files():
    files = {}
    candidates = [p for p in WS.rglob("Cargo.toml")
                  if not any(s.startswith(("vendor", "dup-pinned", "target"))
                             for s in p.relative_to(WS).parts[:-1])]
    lock = WS / "Cargo.lock"
    if lock.is_file():
        candidates.append(lock)
    for p in candidates:
        files[p] = p.read_text()
    return files


def repo_rev_usage(repo):
    """All revs the tree pins `repo` at, with usage counts. Revs appear
    in manifests as `git = "<repo>" ... rev = "<4-40 hex>"` (field order
    varies, short prefixes are legal) and in the lock as ?rev=X#Y."""
    usage = {}

    def bump(rev):
        usage[rev] = usage.get(rev, 0) + 1

    for path, text in collect_files().items():
        if path.name == "Cargo.toml":
            for line in text.splitlines():
                if f'git = "{repo}"' in line:
                    m = re.search(r'rev = "([0-9a-f]{4,40})"', line)
                    if m:
                        bump(m.group(1))
        else:
            for m in re.finditer(rf"{re.escape(repo)}\?rev=([0-9a-f]{{4,40}})#", text):
                bump(m.group(1))
    return usage


def retarget_repo(repo, target):
    """Point EVERY pin of `repo` (manifest line rewrite + lock URL
    rewrite) at `target`, dedup the lock."""
    lock_re = re.compile(rf"({re.escape(repo)}\?rev=)[0-9a-f]{4,40}(#[0-9a-f]{4,40})")
    for path, text in collect_files().items():
        if path.name == "Cargo.toml":
            out = []
            for line in text.splitlines(keepends=True):
                if f'git = "{repo}"' in line:
                    line = re.sub(r'(rev = ")[0-9a-f]{4,40}(")',
                                  rf"\g<1>{target}\g<2>", line)
                out.append(line)
            text = "".join(out)
        else:
            text = lock_re.sub(rf"\g<1>{target}\g<2>{target}", text)
            text = dedup_lock(text)
        path.write_text(text)


def try_lock_precise(repo, crate_v, rev1, rev2):
    """Duplicates from git-deps-of-git-deps (pins live inside the git
    checkouts, not in our tree) can only be unified at the lockfile:
    cargo update --precise moves one entry onto the other's rev."""
    crate, ver = crate_v.rsplit(" v", 1)
    for target in (rev2, rev1):
        spec = f"git+{repo}?rev={rev1}#{crate}@{ver}"
        u = subprocess.run(["cargo", "update", "-p", spec, "--precise", target],
                           cwd=WS, capture_output=True, text=True)
        if u.returncode == 0:
            log(f"moved {crate_v} {rev1[:8]} -> {target[:8]} via cargo update")
            return vendor(False)
        log(f"cargo update --precise {target[:8]} failed:\n{u.stderr.strip()[-300:]}")
    return None


def dup_key(crate_v, repo, rev1, rev2):
    return (crate_v, repo, frozenset((rev1, rev2)))


def try_retarget(repo, crate_v, rev1, rev2, skip_lock=False):
    """Unify every pin of `repo` onto one rev. Lock-level first (nested
    git deps), then a full manifest retarget; the lock move alone often
    reverts on the next vendor because the manifests re-pin the old revs
    (pdfcraft red), so an unchanged duplicate escalates to the rewrite.
    Candidates are tried by (full-length first, then usage): the
    dominant pin is the one the root manifest intends, and full revs
    are the well-groomed ones. A vendor result that fails on a NEW
    duplicate is progress: trees can chain several stale revs
    (pdfcraft 0.22.0 carries eight)."""
    if not skip_lock:
        r = try_lock_precise(repo, crate_v, rev1, rev2)
        if r is not None:
            d = dup_sources(r.stderr)
            if r.returncode == 0 or (
                    d and dup_key(d[0], d[1], d[2], d[4])
                    != dup_key(crate_v, repo, rev1, rev2)):
                return r
    usage = repo_rev_usage(repo)
    # revs from the error too: the second source can live inside a git
    # checkout (cargo's cache), invisible to our tree scan
    revs = set(usage) | {rev1, rev2}
    candidates = sorted(revs, key=lambda rv: (len(rv) < 40, -usage.get(rv, 0)))
    for target in candidates:
        snapshot = collect_files()
        retarget_repo(repo, target)
        r = vendor(False)
        if r.returncode == 0 or dup_sources(r.stderr):
            log(f"unified {repo} pins onto {target[:8]}")
            return r
        log(f"rewiring to {target[:8]} failed:\n{r.stderr.strip()[-400:]}")
        for p, t in snapshot.items():
            p.write_text(t)
    sys.exit("pinvendor: rewiring duplicate git sources failed")


r = vendor(True)
seen_keys = set()
for _ in range(20):
    if r.returncode == 0:
        break
    dup = dup_sources(r.stderr)
    if not dup:
        sys.stderr.write(r.stderr)
        sys.exit("cargo vendor failed (not a duplicate-source error)")
    key = dup_key(dup[0], dup[1], dup[2], dup[4])
    r = try_retarget(dup[1], dup[0], dup[2], dup[4], skip_lock=key in seen_keys)
    seen_keys.add(key)
if r.returncode != 0:
    sys.stderr.write(r.stderr)
    sys.exit("cargo vendor failed after unification retries")


def drop_unvendored_git_patches():
    dropped = False
    for cm in WS.rglob("Cargo.toml"):
        if any(p.startswith("vendor") for p in cm.relative_to(WS).parts[:-1]):
            continue
        text = cm.read_text()
        if "\n[patch.crates-io]" not in text and not text.startswith("[patch.crates-io]"):
            continue
        lines = text.splitlines(keepends=True)
        out, inpatch = [], False
        for line in lines:
            if line.startswith("[patch.crates-io]"):
                inpatch = True
            elif line.startswith("["):
                inpatch = False
            if inpatch:
                m = re.match(r"([A-Za-z0-9_-]+)\s*=\s*\{\s*git", line)
                if m:
                    crate = m.group(1)
                    vendored = (WS / "vendor-deps" / crate).is_dir() or \
                        bool(list((WS / "vendor-deps").glob(crate + "-[0-9]*")))
                    if not vendored:
                        log(f"dropping unvendored git patch entry: {crate} ({cm})")
                        dropped = True
                        continue
            out.append(line)
        new = "".join(out)
        if new != text:
            cm.write_text(new)
    return dropped


if drop_unvendored_git_patches():
    r = vendor(False)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit("cargo vendor failed after patch drop")

cfgdir = WS / ".cargo"
cfgdir.mkdir(exist_ok=True)
(cfgdir / "config.toml").write_text(r.stdout)
(WS.parent / "vendor_config.toml").write_text(r.stdout)
log("vendored OK; config written to .cargo/config.toml")
