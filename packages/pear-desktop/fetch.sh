#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
base="https://github.com/pear-devs/pear-desktop/releases/download/v${ver}"
curl -fL "$base/youtube-music-${ver}.x86_64.rpm"  -o "$dir/youtube-music-${ver}.x86_64.rpm"
curl -fL "$base/youtube-music-${ver}.aarch64.rpm" -o "$dir/youtube-music-${ver}.aarch64.rpm"
curl -fL "https://raw.githubusercontent.com/pear-devs/pear-desktop/v${ver}/license" -o "$dir/license"
echo "fetched pear-desktop ${ver}"
