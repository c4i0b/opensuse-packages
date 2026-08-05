#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(cat "$dir/VERSION")"
curl -fL "https://github.com/pear-devs/pear-desktop/releases/download/v${ver}/youtube-music-${ver}.tar.gz" -o "$dir/youtube-music-${ver}.tar.gz"
echo "fetched pear-desktop ${ver}"
