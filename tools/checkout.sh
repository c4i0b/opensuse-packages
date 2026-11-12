#!/usr/bin/env bash
# Ensure an up-to-date osc working copy of one OBS package.
set -euo pipefail
repo="$(repo_root 2>/dev/null || pwd)"
# shellcheck source=lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

[ $# -ge 1 ] || { echo "usage: checkout.sh <pkg-dir>" >&2; exit 2; }
name="$(pkg_name "$1")"
project="home:${OBS_USER:?OBS_USER unset}"
dest="$(osc_work)/$project/$name"

if [ -d "$dest/.osc" ]; then
  (cd "$dest" && osc_cmd up)
else
  mkdir -p "$(osc_work)/$project"
  osc_cmd co "$project" "$name" -o "$dest"
fi
echo "working copy: $dest"
