#!/usr/bin/env bash
# Create (or re-apply) the OBS project from _project.meta.xml.
set -euo pipefail
repo="$(repo_root 2>/dev/null || pwd)"
# shellcheck source=lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

project="home:${OBS_USER:?OBS_USER unset}"
force="${1:-0}"
if osc_cmd meta prj "$project" >/dev/null 2>&1 && [ "$force" != 1 ]; then
  echo "project $project already exists (force=1 to re-apply _project.meta.xml)"
  exit 0
fi
arches=""
for a in ${OBS_ARCHES:-x86_64 aarch64}; do
  [ -n "$arches" ] && arches+=$'\n'
  arches+="    <arch>$a</arch>"
done
tmp="$(mktemp)"
sed -e "s|@@PROJECT@@|$project|g" \
    -e "s|@@REPO@@|${OBS_REPO:-opensuse_tumbleweed}|g" \
    -e "s|@@ARCHES@@|$arches|g" \
    "$repo/_project.meta.xml" > "$tmp"
osc_cmd meta prj -F "$tmp" "$project"
rm -f "$tmp"
echo "project ready: $project"
