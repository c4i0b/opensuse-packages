#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
base="https://github.com/team-spotube/Spotube/releases/download/v${ver}"
curl -fL "$base/Spotube-linux-x86_64.rpm" -o "$dir/Spotube-linux-x86_64.rpm"
curl -fL "https://raw.githubusercontent.com/team-spotube/Spotube/v${ver}/LICENSE" -o "$dir/LICENSE"
echo "fetched spotube ${ver}"
