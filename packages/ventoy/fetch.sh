#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
curl -fL "https://github.com/ventoy/Ventoy/releases/download/v${ver}/ventoy-${ver}-linux.tar.gz" -o "$dir/ventoy-${ver}-linux.tar.gz"
curl -fL "https://raw.githubusercontent.com/ventoy/Ventoy/v${ver}/COPYING" -o "$dir/COPYING"
echo "fetched ventoy ${ver}"
