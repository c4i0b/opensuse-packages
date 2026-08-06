#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(cat "$dir/VERSION")"
curl -fL "https://github.com/yorukot/superfile/archive/refs/tags/v${ver}.tar.gz" -o "$dir/superfile-${ver}.tar.gz"
rm -f "$dir/vendor.tar.gz"
docker run --rm -e HOME=/tmp -v "$dir:/work" opensuse-packaging:dev bash -lc "
  set -e
  rm -rf /work/vendor /work/superfile-${ver}
  tar xzf /work/superfile-${ver}.tar.gz -C /work
  cd /work/superfile-${ver}
  go mod vendor
  tar -czf /work/vendor.tar.gz vendor
  rm -rf /work/vendor /work/superfile-${ver}
"
echo "fetched superfile ${ver} + vendor"
