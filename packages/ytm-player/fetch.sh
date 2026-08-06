#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
curl -fL "https://github.com/peternaame-boop/ytm-player/releases/download/v${ver}/ytm_player-${ver}.tar.gz" -o "$dir/ytm_player-${ver}.tar.gz"
echo "fetched ytm-player ${ver}"
