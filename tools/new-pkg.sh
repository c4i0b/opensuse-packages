#!/usr/bin/env bash
# Create the OBS package metadata (title/description) from the spec, then
# check out a working copy into the osc workspace.
set -euo pipefail
repo="$(repo_root 2>/dev/null || pwd)"
# shellcheck source=lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[ $# -ge 1 ] || { echo "usage: new-pkg.sh <pkg-dir>" >&2; exit 2; }
pkg="$1"
name="$(pkg_name "$pkg")"
project="home:${OBS_USER:?OBS_USER unset}"
spec="$(ls "$repo/$pkg"/*.spec | head -1)"

summary="$(awk '/^Summary:/ {sub(/^Summary:[ \t]*/,""); print; exit}' "$spec")"
desc="$(awk '/^%description/{f=1;next}/^%/{f=0}f&&NF{print}' "$spec" | head -8)"
esc() { sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'; }
tmp="$(mktemp)"
{
  echo "<package name=\"$name\" project=\"$project\">"
  printf '  <title>%s</title>\n' "$(printf '%s' "$summary" | esc)"
  printf '  <description>%s</description>\n' "$(printf '%s' "$desc" | esc)"
  echo "</package>"
} > "$tmp"
osc_cmd meta pkg -F "$tmp" "$project" "$name"
rm -f "$tmp"

bash "$repo/tools/checkout.sh" "$pkg"
