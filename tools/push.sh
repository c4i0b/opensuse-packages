#!/usr/bin/env bash
# Sync one package to OBS: lint gate, ensure the OBS package exists, rsync the
# sources (dev files excluded) into the osc checkout, osc addremove + commit.
set -euo pipefail
# shellcheck source=lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
repo="$(repo_root 2>/dev/null || pwd)"

[ $# -ge 2 ] || { echo 'usage: push.sh <pkg-dir> "commit message"' >&2; exit 2; }
pkg="$1"; msg="$2"
name="$(pkg_name "$pkg")"
project="home:${OBS_USER:?OBS_USER unset}"
src="$repo/$pkg"
dest="$(osc_work)/$project/$name"

python3 "$repo/opensuse-lint.py" "$src"/*.spec \
  || { echo "lint FAILED — fix before push" >&2; exit 1; }

[ -d "$dest/.osc" ] || bash "$repo/tools/new-pkg.sh" "$pkg"

# refresh the spec version in generated files (e.g. .changes version bumps),
# then sync: dev files and local archives never reach OBS (_service fetches
# the real sources server-side)
[ -x "$src/bump.sh" ] && "$src/bump.sh" "$(spec_version "$src"/*.spec)" || true
# Rust vendor archives are generated client-side (cargo_vendor is not in
# the OBS service allowlist) and live outside git. --filter=P uploads them
# when present locally but protects them from --delete when a checkout
# lacks them (a CI checkout never has one) — plain --exclude would never
# upload and a bare transfer would wipe them server-side.
ex=(--exclude='.osc' --exclude='fetch.sh' --exclude='bump.sh' --exclude='BIN'
    --exclude='*.tar.gz' --exclude='*.zip' --filter='P *.tar.zst')
[ -f "$src/.obsignore" ] && ex+=(--exclude-from="$src/.obsignore")
rsync -a --delete "${ex[@]}" "$src/" "$dest/"

(cd "$dest" && osc_cmd addremove && osc_cmd st)

if [ "${CI:-}" != true ] && [ "${PUSH_YES:-}" != 1 ]; then
  [ -t 0 ] || { echo "not a tty: re-run with PUSH_YES=1 to confirm" >&2; exit 1; }
  read -r -p "Commit $name to $project? [y/N] " ok
  [ "$ok" = y ] || { echo aborted; exit 1; }
fi
(cd "$dest" && osc_cmd ci -m "$msg")
echo "pushed $name -> $project"
