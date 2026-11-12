#!/usr/bin/env bash
# Local pre-flight build of one package: rpmbuild in the tooling container,
# gated on rpmlint errors (mirrors what OBS would reject). Runs INSIDE the
# tooling container (repo at /app).
set -euo pipefail
# shellcheck source=lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
repo="$(repo_root 2>/dev/null || pwd)"

[ $# -ge 1 ] || { echo "usage: build.sh <pkg-dir-relative-to-repo>" >&2; exit 2; }
dir="$repo/$1"
name="$(pkg_name "$1")"
cd "$repo"

[ -f "$dir"/*.spec ] || { echo "no .spec in $1" >&2; exit 1; }
[ -x "$dir/fetch.sh" ] && "$dir/fetch.sh" || true

# Package-specific BuildRequires are not baked into the image: install on
# demand (network is available at build time by design).
reqs="$(grep -h '^BuildRequires:' "$dir"/*.spec | sed 's/BuildRequires:[[:space:]]*//; s/[[:space:]]*$//' | tr '\n' ' ' || true)"
if [ -n "$reqs" ]; then
  zypper --non-interactive install --no-recommends $reqs >/dev/null
fi

out="$repo/.build/$name"
rm -rf "$out"; mkdir -p "$out"

rpmbuild -bb \
  -D "_topdir /tmp/rpmbuild" \
  -D "_sourcedir $dir" \
  -D "_rpmdir $out" \
  -D "debug_package %{nil}" \
  "$dir"/*.spec

echo "--- rpmlint ---"
rpmlint_flags=()
for f in "$dir"/*.rpmlintrc; do [ -f "$f" ] && rpmlint_flags+=(-r "$f"); done
rpmlint_flags+=(-r "$repo/tools/rpmlintrc")
rpmlint "${rpmlint_flags[@]}" "$out"/*/*.rpm 2>&1 | tee /tmp/rpmlint.out

# Re-derive the verdict from the output (rpmlint's exit code is unreliable
# across configs). unused-rpmlintrc-filter only fails for PER-PACKAGE filters
# (the tools/rpmlintrc mirror matches just some packages by design — see
# docs/packaging/general.md).
per_pkg_filters=""
for f in "$dir"/*.rpmlintrc; do
  [ -f "$f" ] && per_pkg_filters+="$(sed -n 's/^addFilter("\(.*\)")$/\1/p' "$f")"$'\n'
done
fail=0
while IFS= read -r line; do
  [ -z "$line" ] && continue
  pat="$(printf '%s' "$line" | sed -n 's/.*unused-rpmlintrc-filter "\([^"]*\)".*/\1/p')"
  if [ -n "$pat" ]; then
    if grep -Fxq "$pat" <<<"$per_pkg_filters"; then
      fail=1; echo "stale per-package rpmlintrc filter: $pat"
    fi
  else
    fail=1; echo "$line"
  fi
done <<<"$(grep -E ': E: ' /tmp/rpmlint.out || true)"

[ "$fail" = 0 ] || { echo "rpmlint ERRORS -> fix before push" >&2; exit 1; }
echo "RPMs -> $out"
