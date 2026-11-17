#!/usr/bin/env bash
# Regenerate a package's client-side vendor artifacts in CI. Called by the
# autoupdate bot after bumping a package (validates the package is
# revendorable BEFORE merge) and by push-to-obs before rsync (produces the
# artifact in the runner so the obs-rsync P filter uploads it).
#
# Models, in dispatch order (mirrors docs/packaging/rust.md and the
# templates):
#   1. fetch.sh + *.obscpio (npm-bundle): fetch.sh --vendor inside a
#      tumbleweed container (needs nodejs24, npm-default,
#      obs-service-node_modules, cpio — runner images have none of them)
#   2. fetch.sh alone (python-venv-wheels): fetch.sh --vendor on the
#      runner (hermes-agent self-installs uv)
#   3. go build -mod=vendor (go-source client-side): git clone the tag,
#      go mod vendor, tar --zstd (the templates/rust-source.spec.tpl
#      comment prescribes exactly this command pair)
#   4. %{cargo_build} (rust-source/rust-gui): the canonical
#      obs-service-cargo_vendor inside a tumbleweed container — plain
#      `cargo vendor` is NOT equivalent (the service packs .cargo/config
#      + Cargo.lock into the archive; %cargo_build reads that layout)
#
# Output artifacts (*.tar.zst, *.obscpio) are gitignored on purpose: they
# are regenerated, never committed.
set -euo pipefail

usage="usage: revendor.sh <package>"
pkg="${1:?$usage}"

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dir="$root/packages/$pkg"
spec="$(ls "$dir"/*.spec 2>/dev/null | head -1 || true)"
[ -n "$spec" ] || { echo "revendor.sh: no spec in packages/$pkg" >&2; exit 1; }
ver="$(awk '/^Version:/{print $2; exit}' "$spec")"

container() {
  # docker on the GitHub runner, podman on dev hosts
  if command -v docker >/dev/null 2>&1; then echo docker
  elif command -v podman >/dev/null 2>&1; then echo podman
  else echo ""; fi
}

tw_image="registry.opensuse.org/opensuse/tumbleweed:latest"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

service_params() {
  # url + revision from _service (bump.sh already rewrote the revision to
  # the new version)
  local svc="$dir/_service"
  [ -f "$svc" ] || { echo "revendor.sh: $pkg has no _service" >&2; exit 1; }
  url="$(sed -n 's/.*<param name="url">\([^<]*\)<\/param>.*/\1/p' "$svc" | head -1)"
  rev="$(sed -n 's/.*<param name="revision">\([^<]*\)<\/param>.*/\1/p' "$svc" | head -1)"
  [ -n "$url" ] && [ -n "$rev" ] || { echo "revendor.sh: $pkg _service lacks url/revision" >&2; exit 1; }
}

# 1. npm-bundle: whole fetch.sh --vendor in the container (the obs
# node_modules service binary only exists on openSUSE)
if [ -f "$dir/fetch.sh" ] && grep -q 'obscpio' "$spec"; then
  ctr="$(container)"
  [ -n "$ctr" ] || { echo "revendor.sh: $pkg needs a container runtime" >&2; exit 1; }
  "$ctr" run --rm -v "$dir:/work:Z" "$tw_image" bash -c '
    set -euo pipefail
    zypper -qn in --no-recommends nodejs24 npm-default obs-service-node_modules cpio findutils tar
    cd /work && bash fetch.sh --vendor
  '
  echo "revendored $pkg (npm-bundle) in tumbleweed container"
  exit 0
fi

# 2. self-contained fetch.sh (python-venv-wheels)
if [ -f "$dir/fetch.sh" ]; then
  (cd "$dir" && bash fetch.sh --vendor)
  echo "revendored $pkg (fetch.sh) on the runner"
  exit 0
fi

# 3. Go client-vendored (server-side go_modules packages need nothing
# here — OBS regenerates vendor.tar.gz on its side). Match the service
# element: specs mention go_modules in comments (nexttrace explains why
# it CANNOT use it).
if grep -q 'go build -mod=vendor' "$spec" && grep -q 'service name="go_modules"' "$dir/_service" 2>/dev/null; then
  echo "revendor.sh: $pkg vendors server-side (go_modules), nothing to do"
  exit 0
fi
if grep -q 'go build -mod=vendor' "$spec"; then
  if command -v go >/dev/null 2>&1 && command -v zstd >/dev/null 2>&1; then
    service_params
    git clone -q --depth 1 --branch "$rev" "$url" "$tmp/src"
    (cd "$tmp/src" && go mod vendor)
    tar -C "$tmp/src" --zstd -cf "$dir/vendor.tar.zst" vendor
  else
    # no go on the host (dev hosts carry only just+podman; runner images
    # change): vendor inside the tumbleweed container instead
    ctr="$(container)"
    [ -n "$ctr" ] || { echo "revendor.sh: $pkg needs go or a container runtime" >&2; exit 1; }
    service_params
    "$ctr" run --rm -v "$tmp:/work:Z" "$tw_image" bash -c '
      set -euo pipefail
      zypper -qn in --no-recommends go git zstd
      git clone -q --depth 1 --branch "'"$rev"'" "'"$url"'" /work/src
      cd /work/src && go mod vendor
      tar -C /work/src --zstd -cf /work/vendor.tar.zst vendor
    '
    mv "$tmp/vendor.tar.zst" "$dir/vendor.tar.zst"
  fi
  echo "revendored $pkg (go) -> vendor.tar.zst"
  exit 0
fi

# 4. Rust (canonical cargo_vendor service in a container)
if grep -q 'cargo_build' "$spec"; then
  ctr="$(container)"
  [ -n "$ctr" ] || { echo "revendor.sh: $pkg needs a container runtime" >&2; exit 1; }
  service_params
  git clone -q --depth 1 --branch "$rev" "$url" "$tmp/work-tree"
  mkdir -p "$tmp/work"
  mv "$tmp/work-tree" "$tmp/work/$pkg-$ver"
  # flags from templates/rust-source.spec.tpl (2026-11 mise/oxker/atac/
  # ludusavi fleet): respect the lockfile, never update, zst compression
  "$ctr" run --rm -v "$tmp/work:/work:Z" "$tw_image" bash -c '
    set -euo pipefail
    zypper -qn in --no-recommends obs-service-cargo_vendor
    /usr/lib/obs/service/cargo_vendor --src "/work/'"$pkg"'-'"$ver"'" \
      --outdir /work --compression zst --respect-lockfile true --update false
  '
  [ -f "$tmp/work/vendor.tar.zst" ] || { echo "revendor.sh: cargo_vendor produced no vendor.tar.zst for $pkg" >&2; exit 1; }
  mv "$tmp/work/vendor.tar.zst" "$dir/vendor.tar.zst"
  echo "revendored $pkg (rust, cargo_vendor) -> vendor.tar.zst"
  exit 0
fi

echo "revendor.sh: no vendor model matches $pkg" >&2
exit 1
