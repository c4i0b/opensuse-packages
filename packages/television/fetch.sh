#!/usr/bin/env bash
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ver="$(awk '/^Version:/{print $2}' "$dir"/*.spec | head -1)"
crate="television"
curl -fL "https://static.crates.io/crates/${crate}/${crate}-${ver}.crate" -o "$dir/${crate}-${ver}.tar.gz"
rm -f "$dir/vendor.tar.zst"
docker run --rm -e HOME=/tmp -v "$dir:/work" opensuse-packaging:dev bash -lc "
  set -e
  rm -rf /work/vendor /work/${crate}-${ver}
  tar xzf /work/${crate}-${ver}.tar.gz -C /work
  cd /work/${crate}-${ver}
  cargo vendor vendor/ >/dev/null
  tar --zstd -cf /work/vendor.tar.zst vendor
  rm -rf /work/vendor /work/${crate}-${ver}
"
printf '[source.crates-io]\nreplace-with = "vendored-sources"\n\n[source.vendored-sources]\ndirectory = "vendor"\n' > "$dir/cargo_config"
curl -fL "https://github.com/alexpasmantier/television/releases/download/${ver}/tv-${ver}-x86_64-unknown-linux-gnu.tar.gz" -o "/tmp/tv-${ver}.tar.gz"
rm -rf "/tmp/tvrel"
mkdir -p "/tmp/tvrel"
tar xzf "/tmp/tv-${ver}.tar.gz" -C "/tmp/tvrel"
cp /tmp/tvrel/*/doc/tv.1 "$dir/tv.1"
rm -rf "/tmp/tvrel" "/tmp/tv-${ver}.tar.gz"
echo "fetched television ${ver} + vendor + tv.1"
