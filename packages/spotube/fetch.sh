#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
base="https://github.com/team-spotube/Spotube/releases/download/v${ver}"
for arch in x86_64 aarch64; do
    curl -fL "$base/Spotube-linux-${arch}.rpm" -o "$dir/Spotube-linux-${arch}.rpm"
done
curl -fL "https://raw.githubusercontent.com/team-spotube/Spotube/v${ver}/LICENSE" -o "$dir/LICENSE"
echo "fetched spotube ${ver}"
