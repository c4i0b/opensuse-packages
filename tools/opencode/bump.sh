#!/usr/bin/env bash
set -euo pipefail
ver="${1:?usage: bump.sh <version>}"
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
printf '%s\n' "$ver" > "$dir/VERSION"
sed -i "s|/v[^/]*/opencode-linux-x64|/v${ver}/opencode-linux-x64|" "$dir/_service"
sed -i "s|^Version:.*|Version:        ${ver}|" "$dir/opencode.spec"
echo "bumped opencode to ${ver} -> add a .changes entry"
