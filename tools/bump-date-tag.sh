#!/usr/bin/env bash
# Central bump for date-tagged upstreams (vinceliuice icon themes): RPM
# forbids '-' in Version, so the spec keeps the raw date tag in
# "%global tag" and the dot-sanitized form in Version; _service carries
# both (tag in the download path, version in the filename param). Called
# by each package's bump.sh (the bot prefers per-package bump.sh).
set -euo pipefail

usage="usage: bump-date-tag.sh <package> <rpm-version>"
pkg="${1:?$usage}"
ver="${2:?$usage}"

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dir="$root/packages/$pkg"
spec="$(ls "$dir"/*.spec | head -1)"
old="$(awk '/^Version:/{print $2; exit}' "$spec")"
oldtag="$(awk '/^%global tag/{print $3; exit}' "$spec")"
if [[ -z "$oldtag" ]]; then
  echo "$pkg: no '%global tag' in $spec — not a date-tagged package?" >&2
  exit 1
fi
tag="$(printf '%s' "$ver" | sed 's/\./-/g')"

# Escape the dots: the version patterns are regexes in sed, and an unescaped
# "2026.08.10" also matches the dashed tag in the download path, rewriting it
# to the dot form that 404s server-side (red: the vinceliuice theme fleet).
esc() { printf '%s' "$1" | sed 's/[.]/\\./g'; }
sed -i "s|^Version:.*|Version:        ${ver}|; s|^%global tag .*|%global tag    ${tag}|" "$spec"
sed -i "s|$(esc "$oldtag")|${tag}|g; s|$(esc "$old")|${ver}|g" "$dir/_service"

# grep guards: a silent no-op sed here freezes _service at the old tag and
# the next OBS fetch 404s (conventions.md "Seds carry a grep guard")
grep -q "^Version:        ${ver}\$" "$spec"
grep -q "^%global tag    ${tag}\$" "$spec"
grep -q "${tag}" "$dir/_service"
grep -q "${ver}" "$dir/_service"

# .changes entry (OBS merges it into %changelog at build time)
changes="$dir/$pkg.changes"
if [ -f "$changes" ]; then
  ts="$(date -u +"%a %b %e %H:%M:%S UTC %Y")"
  tmp="$(mktemp)"
  {
    printf -- "-------------------------------------------------------------------\n"
    printf -- "%s - %s <%s>\n\n" "$ts" "${OBS_NAME:-Caio Bruno}" "${OBS_EMAIL:-cbrunofb@gmail.com}"
    printf -- "- Update to %s\n\n" "$ver"
    cat "$changes"
  } > "$tmp"
  mv "$tmp" "$changes"
fi

echo "bumped $pkg ${old} (${oldtag}) -> ${ver} (${tag})"
