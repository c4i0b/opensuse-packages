#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
curl -fL "https://github.com/derv82/wifit3/archive/refs/tags/v${ver}.tar.gz" -o "$dir/wifit3-${ver}.tar.gz"
echo "fetched wifit3 ${ver}"
