#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
base="https://github.com/ersinkoc/phonebox/releases/download/v${ver}"
curl -fL "$base/PhoneBoxAgent-${ver}-linux-x64.zip" -o "$dir/PhoneBoxAgent-${ver}-linux-x64.zip"
curl -fL "https://raw.githubusercontent.com/ersinkoc/phonebox/v${ver}/LICENSE" -o "$dir/LICENSE"
echo "fetched phonebox ${ver}"
