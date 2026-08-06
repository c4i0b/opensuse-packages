#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
repo="anomalyco/opencode"
curl -fL "https://github.com/${repo}/archive/refs/tags/v${ver}.tar.gz" -o "$dir/${repo##*/}-${ver}.tar.gz"
pm="$(tar -xzOf "$dir/${repo##*/}-${ver}.tar.gz" "${repo##*/}-${ver}/package.json" | sed -n 's/.*"packageManager": *"[^"]*@\([^"]*\)".*/\1/p' | head -1)"
curl -fL "https://github.com/oven-sh/bun/releases/download/bun-v${pm}/bun-linux-x64.zip" -o "$dir/bun-linux-x64.zip"
curl -fL "https://models.dev/api.json" -o "$dir/models-api.json"
echo "fetched opencode ${ver} (bun ${pm}) + models snapshot"
echo "if deps changed since the last vendor: regenerate vendor-node_modules.tar.zst (see AGENTS.md, Bun section)"
