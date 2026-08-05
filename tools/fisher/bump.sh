#!/usr/bin/env bash
set -euo pipefail
ver="${1:?usage: bump.sh <version>}"
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
old="$(cat "$dir/VERSION")"
printf '%s\n' "$ver" > "$dir/VERSION"
sed -i "s|/fisher/archive/${old}\.tar\.gz|/fisher/archive/${ver}.tar.gz|g; s|fisher-${old}\.tar\.gz|fisher-${ver}.tar.gz|g" "$dir/_service"
spec="$(ls "$dir"/*.spec | head -1)"
sed -i "s|^Version:.*|Version:        ${ver}|" "$spec"
echo "bumped fisher ${old} -> ${ver} -> add a .changes entry"
