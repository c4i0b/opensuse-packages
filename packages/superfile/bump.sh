#!/usr/bin/env bash
set -euo pipefail
ver="${1:?usage: bump.sh <version>}"
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
old="$(cat "$dir/VERSION")"
printf '%s\n' "$ver" > "$dir/VERSION"
sed -i "s|/v${old}/|/v${ver}/|g" "$dir/_service"
spec="$(ls "$dir"/*.spec | head -1)"
sed -i "s|^Version:.*|Version:        ${ver}|" "$spec"
echo "bumped superfile ${old} -> ${ver} -> run fetch.sh (regenerates vendor.tar.gz) and add a .changes entry"
