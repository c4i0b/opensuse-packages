#!/usr/bin/env bash
set -euo pipefail
ver="${1:?usage: bump.sh <version>}"
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
old="$(cat "$dir/VERSION")"
printf '%s\n' "$ver" > "$dir/VERSION"
sed -i "s|television-${old}|television-${ver}|g; s|tv-${old}|tv-${ver}|g; s|releases/download/${old}|releases/download/${ver}|g" "$dir/_service"
spec="$(ls "$dir"/*.spec | head -1)"
sed -i "s|^Version:.*|Version:        ${ver}|" "$spec"
echo "bumped television ${old} -> ${ver} -> run fetch.sh (regenerates vendor.tar.zst, cargo_config, tv.1) and add a .changes entry"
