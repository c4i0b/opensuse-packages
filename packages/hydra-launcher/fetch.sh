#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
curl -fL "https://github.com/hydralauncher/hydra/releases/download/v${ver}/hydralauncher-${ver}.x86_64.rpm" -o "$dir/hydralauncher-${ver}.x86_64.rpm"
curl -fL "https://raw.githubusercontent.com/hydralauncher/hydra/v${ver}/LICENSE" -o "$dir/LICENSE"
echo "fetched hydra-launcher ${ver}"
