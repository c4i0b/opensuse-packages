#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(cat "$dir/VERSION")"
curl -fL "https://github.com/alexpasmantier/television/releases/download/${ver}/tv-${ver}-x86_64-unknown-linux-gnu.tar.gz" -o "$dir/tv-${ver}-x86_64-unknown-linux-gnu.tar.gz"
echo "fetched television ${ver}"
