#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
curl -fL "https://github.com/rafatosta/zapzap/archive/refs/tags/${ver}.tar.gz" -o "$dir/zapzap-${ver}.tar.gz"
echo "fetched zapzap ${ver}"
