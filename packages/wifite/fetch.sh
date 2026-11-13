#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
curl -fL "https://github.com/derv82/wifite2/archive/refs/tags/${ver}.tar.gz" -o "$dir/wifite-${ver}.tar.gz"
echo "fetched wifite ${ver}"
