#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
curl -fL "https://github.com/anomalyco/opencode/releases/download/v${ver}/opencode-linux-x64.tar.gz" -o "$dir/opencode-linux-x64.tar.gz"
echo "fetched opencode ${ver}"
