#!/usr/bin/env bash
# sync the sources (dev files excluded) into the osc checkout, osc addremove
# + commit. The exclude/protect list has a single definition in
# tools/obs-rsync.sh (also used by the push-to-obs workflow).
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
mapfile -t ex < <(bash "$repo/tools/obs-rsync.sh" --list)
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
