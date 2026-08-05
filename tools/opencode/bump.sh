#!/usr/bin/env bash
set -euo pipefail
ver="${1:?usage: bump.sh <version>}"
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
old="$(cat "$dir/VERSION")"
printf '%s\n' "$ver" > "$dir/VERSION"
sed -i "s|/v${old}/|/v${ver}/|g" "$dir/_service"
sed -i "s|^Version:.*|Version:        ${ver}|" "$dir/opencode.spec"
echo "bumped opencode ${old} -> ${ver} -> add a .changes entry"
