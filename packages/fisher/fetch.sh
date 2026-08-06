#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
curl -fL "https://github.com/jorgebucaran/fisher/archive/${ver}.tar.gz" -o "$dir/fisher-${ver}.tar.gz"
echo "fetched fisher ${ver}"
