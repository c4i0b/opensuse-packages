#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
curl -fL "https://github.com/yorukot/superfile/releases/download/v${ver}/superfile-linux-v${ver}-amd64.tar.gz" -o "$dir/superfile-linux-v${ver}-amd64.tar.gz"
echo "fetched superfile ${ver}"
