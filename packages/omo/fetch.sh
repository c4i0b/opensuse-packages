#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
base="https://github.com/code-yeongyu/oh-my-openagent/releases/download/v${ver}"
curl -fL "$base/omo-linux-x64"  -o "$dir/omo-linux-x64"
curl -fL "$base/omo-linux-arm64" -o "$dir/omo-linux-arm64"
curl -fL "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/v${ver}/LICENSE.md" -o "$dir/LICENSE.md"
echo "fetched omo ${ver}"
