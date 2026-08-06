#!/usr/bin/env bash
set -euo pipefail
ver="${1:?usage: bump.sh <version>}"
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
old="$(cat "$dir/VERSION")"
printf '%s\n' "$ver" > "$dir/VERSION"
sed -i "s|/${old}/|/${ver}/|g; s|tv-${old}-x86_64|tv-${ver}-x86_64|g" "$dir/_service"
spec="$(ls "$dir"/*.spec | head -1)"
sed -i "s|^Version:.*|Version:        ${ver}|" "$spec"
sed -i "s|tv-${old}-x86_64|tv-${ver}-x86_64|g" "$spec"
echo "bumped television ${old} -> ${ver} -> add a .changes entry"
