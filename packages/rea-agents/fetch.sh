#!/usr/bin/env bash
# Fetch sources for the local pre-flight build (OBS fetches via _service).
# Modes:
#   ./fetch.sh                fetch Source0 + expand node_modules.obscpio
#   ./fetch.sh --vendor       regenerate package-lock.json, node_modules.obscpio
#                             and node_modules.spec.inc
#                             (needs nodejs24, npm-default, obs-service-node_modules, cpio)
# OBS package sources are FLAT (no directories): node_modules.spec.inc
# lists every dependency tarball as a Source10000+ registry URL with a
# flat rename (`url#/<flat-name>.tgz`, the cockpit shape — SRPM
# provenance only). The real transport is node_modules.obscpio, which
# the OBS worker auto-unpacks flat into %{_sourcedir}; it is uploaded
# per-bump by a local `just push` and protected by the obs-rsync.sh P
# filter on CI pushes. The obscpio doubles as the LOCAL cache for the
# pre-flight build (expanded flat so `local-npm-registry
# %{_sourcedir}` serves it); keep all three files in sync with Source0
# on bumps.
set -euo pipefail
cd "$(dirname "$0")"
version="$(sed -n 's/^Version:[[:space:]]*//p' rea-agents.spec)"
mode="${1:-}"

# cached: just build runs fetch.sh every time; skip the re-download
[ -s "rea-agents-$version.tgz" ] || \
curl -sL "https://registry.npmjs.org/rea-agents/-/rea-agents-$version.tgz" \
    -o "rea-agents-$version.tgz"

if [ "$mode" = "--vendor" ]; then
    tmp="$(mktemp -d)"
    trap 'rm -rf "$tmp"' EXIT
    mkdir -p "$tmp/package" "$tmp/modules"
    tar zxf "rea-agents-$version.tgz" -C "$tmp/package" --strip-components=1
    # The npm tarball ships an npm-shrinkwrap.json: that IS the lockfile (npm
    # never writes a package-lock.json next to one), so reuse it directly
    cp "$tmp/package/npm-shrinkwrap.json" package-lock.json
    /usr/lib/obs/service/node_modules -i package-lock.json \
        --node-dir "$tmp/modules" --download

    # Bundled dependencies (lock "inBundle": true, or unpublished) ship
    # inside the npm tarball's node_modules/ and have no registry tarball for
    # the service to download — npm-pack them from the bundled tree into the
    # module set.
    python3 - package-lock.json "$tmp/package" "$tmp/modules" > "$tmp/bundled.txt" <<'PY'
import json, os, sys
lock = json.load(open(sys.argv[1]))
pkgroot, moddir = sys.argv[2], sys.argv[3]
for path, entry in lock.get("packages", {}).items():
    if not path.startswith("node_modules/") or "/" in path[len("node_modules/"):]:
        continue
    name = path[len("node_modules/"):]
    expected = name.replace("/", "-") + "-" + entry["version"] + ".tgz"
    if not os.path.exists(os.path.join(moddir, expected)):
        bundled = os.path.join(pkgroot, path)
        if os.path.isdir(bundled):
            print(bundled)
PY
    while read -r bundled; do
        [ -n "$bundled" ] || continue
        echo "packing bundled dep: ${bundled#"$tmp"/}"
        (cd "$bundled" && npm pack --pack-destination "$tmp/modules" \
            --ignore-scripts) >/dev/null
    done < "$tmp/bundled.txt"

    # spec.inc lists EVERY tarball as a registry URL Source (cockpit model:
    # OBS download_files fetches them server-side), verifying every
    # top-level lock entry has a tarball (drift fails loud instead of an
    # OBS-side "Serving 0 packages")
    python3 - package-lock.json "$tmp/modules" > node_modules.spec.inc <<'PY'
import json, os, sys, tarfile
lock = json.load(open(sys.argv[1]))
moddir = sys.argv[2]
have = sorted(f for f in os.listdir(moddir) if f.endswith(".tgz"))

# registry URL per (name, version) from the lock's `resolved` entries
urls = {}
for path, e in lock.get("packages", {}).items():
    if not e.get("resolved"):
        continue
    segs = path.split("/")
    name = segs[-1]
    if len(segs) >= 2 and segs[-2].startswith("@"):
        name = segs[-2] + "/" + name
    urls[(name, e["version"])] = e["resolved"]

missing = []
bundled = []
lines = []
for i, f in enumerate(have, 10000):
    with tarfile.open(os.path.join(moddir, f)) as tf:
        pj = json.load(tf.extractfile("package/package.json"))
    url = urls.get((pj["name"], pj["version"]))
    if url:
        lines.append("Source%d:\t%s#/%s" % (i, url, f))
    else:
        # inBundle: packed from the Source0 tree, no registry URL — a local
        # file uploaded through the obs-rsync.sh P filter
        bundled.append(f)
        lines.append("Source%d:\t%s" % (i, f))
for path, entry in lock.get("packages", {}).items():
    if not path.startswith("node_modules/") or "/" in path[len("node_modules/"):]:
        continue  # nested/scoped entries: tarball name is not derivable from the path
    name = path[len("node_modules/"):]
    expected = name.replace("/", "-") + "-" + entry["version"] + ".tgz"
    if expected not in have:
        missing.append(expected)
if missing:
    sys.exit("missing tarballs for lock entries: %s" % ", ".join(missing[:5]))
print("\n".join(lines))
if bundled:
    sys.stderr.write("bundled (local-file) sources: %s\n" % ", ".join(bundled))
PY

    (cd "$tmp/modules" && find . -maxdepth 1 -name '*.tgz' -printf '%f\n' \
        | cpio -o -H newc --quiet > "$OLDPWD/node_modules.obscpio")

    # refresh the flat expansion for the local pre-flight build (keep Source0)
    find . -maxdepth 1 -name '*.tgz' ! -name "rea-agents-$version.tgz" -delete
    cpio -i --make-directories --quiet < node_modules.obscpio
else
    # local build: expand the container flat into the package dir (the spec
    # installs through local-npm-registry %{_sourcedir})
    if [ -f node_modules.obscpio ]; then
        cpio -i --make-directories --quiet < node_modules.obscpio
    fi
fi
