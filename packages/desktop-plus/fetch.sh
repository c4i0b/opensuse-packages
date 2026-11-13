#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
base="https://github.com/desktop-plus/desktop-plus/releases/download/v${ver}"
curl -fL "$base/DesktopPlus-v${ver}-linux-x86_64.rpm" -o "$dir/DesktopPlus-v${ver}-linux-x86_64.rpm"
curl -fL "$base/DesktopPlus-v${ver}-linux-arm64.rpm" -o "$dir/DesktopPlus-v${ver}-linux-arm64.rpm"
echo "fetched desktop-plus ${ver}"
