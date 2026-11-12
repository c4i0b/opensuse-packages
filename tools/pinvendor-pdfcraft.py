#!/usr/bin/env python3
"""Client-side vendoring for craft apps (pdfcraft/photocraft).

Replicates fedora-packages tools/vendor-sources.py cargo branch:
- cargo vendor --locked into vendor-deps/
- on duplicate git crate+version: pin source-1 rev in dup-pinned/ via a
  [patch."<repo>"] path entry, retry unlocked
- drop [patch.crates-io] git entries whose crate is not in the graph
  (cargo validates every patch entry offline and would abort)
Output overlay root: vendor-deps/, dup-pinned/, .cargo/config.toml,
Cargo.toml, Cargo.lock — packed as vendor.tar.zst by the caller.
"""
import io
import re
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path

WS = Path(sys.argv[1])


def log(m):
    print(f"pinvendor: {m}", file=sys.stderr, flush=True)


def vendor(locked):
    cmd = ["cargo", "vendor"] + (["--locked"] if locked else []) + ["vendor-deps"]
    r = subprocess.run(cmd, cwd=WS, capture_output=True, text=True)
    return r


def pin_duplicate(stderr_text):
    m = re.search(
        r"found duplicate version of package `([A-Za-z0-9_.-]+ v\S+)` "
        r"vendored from two sources:\s*\n\s*source 1: (\S+?rev=([0-9a-f]+))#",
        stderr_text)
    if not m:
        return False
    crate_v, src1, rev = m.group(1), m.group(2), m.group(3)
    crate = crate_v.rsplit(" v", 1)[0]
    repo = re.sub(r"\?rev=[0-9a-f]+$", "", src1)
    log(f"duplicate git sources for {crate_v}; pinning to {rev[:8]} via path patch")
    pindir = WS / "dup-pinned" / crate
    if not pindir.is_dir():
        pindir.parent.mkdir(parents=True, exist_ok=True)
        url = f"{repo}/archive/{rev}.tar.gz"
        log(f"fetching {url}")
        data = io.BytesIO(urllib.request.urlopen(url, timeout=600).read())
        with tarfile.open(fileobj=data, mode="r:gz") as tf:
            members = [m2 for m2 in tf.getmembers() if len(m2.name.split("/")) > 1]
            for m2 in members:
                m2.name = "/".join(m2.name.split("/")[1:])
            tf.extractall(pindir, members=members)
    with (WS / "Cargo.toml").open("a") as f:
        f.write(f'\n[patch."{repo}"]\n{crate} = {{ path = "dup-pinned/{crate}" }}\n')
    return True


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


r = vendor(True)
if r.returncode != 0 and pin_duplicate(r.stderr):
    r = vendor(False)
if r.returncode != 0:
    sys.stderr.write(r.stderr)
    sys.exit("cargo vendor failed after pin retry")
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
