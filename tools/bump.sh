#!/usr/bin/env bash
# Central version bump: spec Version:, every old-version occurrence in
# _service (path AND asset filename), and a .changes entry. Used by the
# autoupdate bot; a package's own bump.sh (if executable) wins over this
# for special cases.
set -euo pipefail

usage="usage: bump.sh <package> <version>"
pkg="${1:?$usage}"
ver="${2:?$usage}"

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dir="$root/packages/$pkg"
spec="$(ls "$dir"/*.spec | head -1)"
old="$(awk '/^Version:/{print $2; exit}' "$spec")"

# spec
sed -i "s|^Version:.*|Version:        ${ver}|" "$spec"

# _service: replace EVERY occurrence of the old version token (download
# directory, asset filename, filename param). Red: the Renovate regex
# manager bumped only the first match, freezing ytm-player's asset name
# at 2.0.0 while the directory said v2.2.0 (404 since the 2.1.0 bump).
if [ -f "$dir/_service" ]; then
  sed -i "s|${old}|${ver}|g" "$dir/_service"
fi

# .changes entry (OBS merges it into %changelog at build time)
changes="$dir/$pkg.changes"
if [ -f "$changes" ]; then
  ts="$(date -u +"%a %b %e %H:%M:%S UTC %Y")"
  tmp="$(mktemp)"
  {
    printf -- "-------------------------------------------------------------------\n"
    printf -- "%s - %s <%s>\n\n" "$ts" "${OBS_NAME:-Caio Bruno}" "${OBS_EMAIL:-cbrunofb@gmail.com}"
    printf -- "- Update to %s\n\n" "$ver"
    cat "$changes"
  } > "$tmp"
  mv "$tmp" "$changes"
fi

echo "bumped $pkg ${old} -> ${ver}"
