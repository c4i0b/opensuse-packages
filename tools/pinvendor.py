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
import io
import os
import re
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

WS = Path(sys.argv[1])

# manifests rewritten by the retarget (path crates inside the source
# tree): they must ship in the overlay or OBS's Source0 copy still pins
# the old revs and diverges from the rewritten lock (effectcraft red)
MODIFIED = set()


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
                    # rename deps (package = "...") deliberately pair a
                    # second name with a SECOND source — rewriting their
                    # rev collapses both names onto one source and the
                    # feature resolver rejects it ("multiple times with
                    # different names", effectcraft OBS red)
                    if 'package = "' in line:
                        out.append(line)
                        continue
                    line = re.sub(r'(rev = ")[0-9a-f]{4,40}(")',
                                  rf"\g<1>{target}\g<2>", line)
                out.append(line)
            text = "".join(out)
        else:
            text = lock_re.sub(rf"\g<1>{target}\g<2>{target}", text)
            text = dedup_lock(text)
        if text != path.read_text():
            MODIFIED.add(path)
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


TRIED = {}


def package_name(manifest):
    text = manifest.read_text()
    if "[package]" not in text:
        return None
    m = re.search(r'^name\s*=\s*"([A-Za-z0-9_.-]+)"', text, re.M)
    return m.group(1) if m else None


def find_crate_dir(root, crate):
    for cm in sorted(root.rglob("Cargo.toml")):
        if package_name(cm) == crate:
            return cm.parent
    return None


DEP_KEYS_KEEP = ("package", "features", "default-features", "optional")


def exclude_dup_pinned():
    """Nested workspaces are not supported: without an exclude, the
    outer workspace claims the whole tree and path deps into dup-pinned/
    fail their workspace inheritance (effectcraft red)."""
    root = WS / "Cargo.toml"
    text = root.read_text()
    if 'exclude' in text and 'dup-pinned' in text.split("exclude", 1)[1][:200]:
        return
    m = re.search(r"(?m)^exclude\s*=\s*\[([^\]]*)\]", text)
    if m:
        inner = m.group(1).strip()
        new = f'exclude = [{inner}{", " if inner else ""}"dup-pinned"]'
        text = text[:m.start()] + new + text[m.end():]
    else:
        text = text.replace("[workspace]\n", '[workspace]\nexclude = ["dup-pinned"]\n', 1)
    root.write_text(text)
    MODIFIED.add(root)


def divert_to_path(repo, rev):
    """Rewrite our manifest deps pinned to repo@rev into path deps on a
    full checkout extracted under dup-pinned/. A regular path dep
    resolves its nested workspace by walking up (the extracted tree
    keeps its root manifest), unlike a [patch] path entry which cargo
    1.99 refuses to inherit through (effectcraft red). Returns False
    when the rev is only referenced from inside other git checkouts —
    nothing in our tree to rewrite."""
    lines_hit = 0
    dupdir = WS / "dup-pinned" / rev[:8]
    for path, text in collect_files().items():
        if path.name != "Cargo.toml":
            continue
        out = []
        for line in text.splitlines(keepends=True):
            if f'git = "{repo}"' in line and f'rev = "{rev}"' in line:
                if not dupdir.is_dir():
                    dupdir.parent.mkdir(parents=True, exist_ok=True)
                    url = f"{repo}/archive/{rev}.tar.gz"
                    log(f"diverting {repo}@{rev[:8]}: fetching {url}")
                    data = io.BytesIO(urllib.request.urlopen(url, timeout=600).read())
                    with tarfile.open(fileobj=data, mode="r:gz") as tf:
                        members = [m for m in tf.getmembers()
                                   if len(m.name.split("/")) > 1]
                        for m in members:
                            m.name = "/".join(m.name.split("/")[1:])
                        tf.extractall(dupdir, members=members)
                    # the extracted workspace's [patch.crates-io] points
                    # at vendor/ dirs that git archives do not carry;
                    # strip them so crates.io versions apply
                    root_man = dupdir / "Cargo.toml"
                    if root_man.is_file():
                        t = root_man.read_text()
                        t = re.sub(r"(?ms)^\[patch\.[^\]]*\]\n.*?(?=^\[|\Z)", "", t)
                        root_man.write_text(t)
                exclude_dup_pinned()
                m = re.match(r'\s*([A-Za-z0-9_-]+)\s*=\s*\{(.*)\}\s*$', line.rstrip())
                if not m:
                    continue
                alias, body = m.groups()
                pkg = re.search(r'package\s*=\s*"([^"]+)"', body)
                pkg = pkg.group(1) if pkg else alias
                cdir = find_crate_dir(dupdir, pkg)
                if cdir is None:
                    log(f"no Cargo.toml declares {pkg} under {dupdir}")
                    continue
                # relative to the manifest being rewritten, not the
                # workspace root (deps live in crates/* submanifests)
                rel = os.path.relpath(cdir, path.parent).replace(os.sep, "/")
                kept = [f"{k} = {v.strip()}" for k, v in
                        re.findall(r'([\w-]+)\s*=\s*("[^"]*"|\[[^\]]*\]|[^,}]+)', body)
                        if k in DEP_KEYS_KEEP]
                fields = ", ".join(kept + [f'path = "{rel}"'])
                line = f'{alias} = {{ {fields} }}\n'
                MODIFIED.add(path)
                lines_hit += 1
            out.append(line)
        new = "".join(out)
        if new != text:
            path.write_text(new)
    if lines_hit:
        log(f"diverted {lines_hit} dep line(s) onto {dupdir.relative_to(WS)}")
    return lines_hit > 0


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
    key = (repo, frozenset((rev1, rev2)))
    tried = TRIED.setdefault(key, set())
    candidates = [rv for rv in
                  sorted(revs, key=lambda rv: (len(rv) < 40, -usage.get(rv, 0)))
                  if rv not in tried]
    for target in candidates:
        tried.add(target)
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


def count_refs(repo, rev):
    n = 0
    for path, text in collect_files().items():
        if path.name == "Cargo.toml":
            for line in text.splitlines():
                if f'git = "{repo}"' in line and f'rev = "{rev}"' in line:
                    n += 1
    return n


def revert_divert(snapshot, rev):
    for p, t in snapshot.items():
        p.write_text(t)
    dupdir = WS / "dup-pinned" / rev[:8]
    subprocess.run(["rm", "-rf", str(dupdir)], check=False)


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
    # path-divert first (keeps the upstream mixed-rev intent, e.g. the
    # craft-audio-markers rename dep); minority rev first — the dominant
    # pin is the one the rest of the tree expects. A diverted rev can be
    # unresolvable standalone (craft-xml left workspace.dependencies at
    # craft-libs 33be3562), so a hard failure reverts and tries the
    # other rev before falling back to rev unification
    handled = False
    for rev in sorted((dup[2], dup[4]), key=lambda rv: count_refs(dup[1], rv)):
        snapshot = collect_files()
        if divert_to_path(dup[1], rev):
            r2 = vendor(False)
            if r2.returncode == 0 or dup_sources(r2.stderr):
                r = r2
                handled = True
                break
            log(f"divert to {rev[:8]} broke resolution, reverting:\n"
                f"{r2.stderr.strip()[-500:]}")
            revert_divert(snapshot, rev)
    if not handled:
        r = try_retarget(dup[1], dup[0], dup[2], dup[4],
                         skip_lock=key in seen_keys)
    seen_keys.add(key)
if r.returncode != 0:
    sys.stderr.write(r.stderr)
    sys.exit("cargo vendor failed after unification retries")


def validate_resolution():
    """cargo vendor resolves without feature unification; the build's
    resolver additionally rejects one crate reachable under two dep
    names from a single source. metadata runs the full resolution
    offline without compiling."""
    return subprocess.run(
        ["cargo", "metadata", "--offline", "--format-version", "1"],
        cwd=WS, capture_output=True, text=True)


def divert_rename_dep(crate):
    """On a 'different names' validation failure, divert the rename dep
    (alias != crate) onto a path checkout so the two names come from
    two sources, as upstream intended."""
    for path, text in collect_files().items():
        if path.name != "Cargo.toml":
            continue
        for line in text.splitlines():
            if 'package = "' in line and f'package = "{crate}"' in line:
                m = re.search(r'git = "([^"]+)"', line)
                rv = re.search(r'rev = "([0-9a-f]{4,40})"', line)
                if m and rv:
                    return divert_to_path(m.group(1), rv.group(1))
    return False


for _ in range(5):
    v = validate_resolution()
    if v.returncode == 0:
        break
    if "multiple times with different names" not in v.stderr:
        sys.stderr.write(v.stderr)
        sys.exit("cargo metadata failed after vendoring")
    crate = re.search(r"crate `([A-Za-z0-9_.-]+) v", v.stderr).group(1)
    log(f"resolution conflict on {crate}: diverting its rename dep")
    if not divert_rename_dep(crate):
        sys.exit(f"pinvendor: no rename dep found to divert for {crate}")
    r = vendor(False)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit("cargo vendor failed during rename-divert retry")
else:
    sys.exit("pinvendor: rename-divert retries exhausted")


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
            MODIFIED.add(cm)
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
# rewritten path-crate manifests for the overlay (root Cargo.toml and
# Cargo.lock are packed unconditionally by the caller)
extra = sorted({p.relative_to(WS).as_posix() for p in MODIFIED
                if p.name == "Cargo.toml" and p != WS / "Cargo.toml"})
(WS.parent / "overlay_extra.txt").write_text("\n".join(extra) + "\n")
log("vendored OK; config written to .cargo/config.toml")
