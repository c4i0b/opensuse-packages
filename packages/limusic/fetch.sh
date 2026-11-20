#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
base="https://github.com/SimoHypers/limusic/releases/download/v${ver}"
curl -fL "$base/limusic-${ver}-1.x86_64.rpm" -o "$dir/limusic-${ver}-1.x86_64.rpm"
curl -fL "https://raw.githubusercontent.com/SimoHypers/limusic/v${ver}/LICENSE" -o "$dir/LICENSE"
curl -fL "https://raw.githubusercontent.com/SimoHypers/limusic/v${ver}/THIRD-PARTY-NOTICES.md" -o "$dir/THIRD-PARTY-NOTICES.md"
echo "fetched limusic ${ver}"
