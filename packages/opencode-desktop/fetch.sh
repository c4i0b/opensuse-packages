#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
base="https://github.com/anomalyco/opencode/releases/download/v${ver}"
curl -fL "$base/opencode-desktop-linux-x86_64.rpm"  -o "$dir/opencode-desktop-linux-x86_64.rpm"
curl -fL "https://raw.githubusercontent.com/anomalyco/opencode/v${ver}/LICENSE" -o "$dir/LICENSE"
echo "fetched opencode-desktop ${ver}"
