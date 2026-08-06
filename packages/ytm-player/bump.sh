#!/usr/bin/env bash
set -euo pipefail
ver="${1:?usage: bump.sh <version>}"
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
spec="$(ls "$dir"/*.spec | head -1)"
old="$(awk '/^Version:/{print $2}' "$spec")"
sed -i "s|/v${old}/|/v${ver}/|g; s|ytm_player-${old}\.tar\.gz|ytm_player-${ver}.tar.gz|g" "$dir/_service"
sed -i "s|^Version:.*|Version:        ${ver}|" "$spec"
echo "bumped ytm-player ${old} -> ${ver} -> add a .changes entry"
