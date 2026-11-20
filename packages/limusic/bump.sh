#!/usr/bin/env bash
set -euo pipefail
ver="${1:?usage: bump.sh <version>}"
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
spec="$(ls "$dir"/*.spec | head -1)"
old="$(awk '/^Version:/{print $2}' "$spec")"
sed -i "s|/v${old}/|/v${ver}/|g; s|limusic-${old}-1|limusic-${ver}-1|g" "$dir/_service"
sed -i "s|^Version:.*|Version:        ${ver}|" "$spec"
sed -i "s|limusic-${old}-1|limusic-${ver}-1|g" "$spec"
# grep guard: every URL must carry the new version (red: silent freeze)
grep -q "v${ver}/limusic-${ver}-1.x86_64.rpm" "$dir/_service" "$spec" || {
    echo "bump to ${ver} did not take everywhere" >&2
    exit 1
}
echo "bumped limusic ${old} -> ${ver} -> add a .changes entry"
