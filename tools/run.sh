#!/usr/bin/env bash
# Smoke-test a built package: install its RPMs into the (ephemeral, Tumbleweed)
# tooling container and exec the binary. Runs INSIDE the container.
set -euo pipefail
repo="$(repo_root 2>/dev/null || pwd)"
# shellcheck source=lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[ $# -ge 1 ] || { echo "usage: run.sh <pkg-dir> [args...]" >&2; exit 2; }
pkg="$1"; shift
dir="$repo/$pkg"
name="$(pkg_name "$pkg")"
bin="$name"
[ -f "$dir/BIN" ] && bin="$(cat "$dir/BIN")"

out="$repo/.build/$name"
rpm="$(ls "$out"/*/*.rpm 2>/dev/null | head -1 || true)"
[ -n "$rpm" ] || { echo "no RPM in $out -- run 'just build $pkg' first" >&2; exit 1; }

rpm -Uvh --nodeps "$out"/*/*.rpm
exec "$bin" "$@"
