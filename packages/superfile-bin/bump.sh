#!/usr/bin/env bash
set -euo pipefail
ver="${1:?usage: bump.sh <version>}"
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
old="$(cat "$dir/VERSION")"
printf '%s\n' "$ver" > "$dir/VERSION"
sed -i "s|/v${old}/|/v${ver}/|g; s|v${old}-amd64|v${ver}-amd64|g" "$dir/_service"
spec="$(ls "$dir"/*.spec | head -1)"
sed -i "s|^Version:.*|Version:        ${ver}|" "$spec"
sed -i "s|v${old}-amd64|v${ver}-amd64|g" "$spec"
echo "bumped superfile ${old} -> ${ver} -> add a .changes entry"
