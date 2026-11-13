#!/usr/bin/env bash
# Create (or re-apply) the OBS project meta rendered by tools/project-meta.sh.
set -euo pipefail
# shellcheck source=lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

project="home:${OBS_USER:?OBS_USER unset}"
force="${1:-0}"
if osc_cmd meta prj "$project" >/dev/null 2>&1 && [ "$force" != 1 ]; then
  echo "project $project already exists (force=1 to re-apply the project meta)"
  exit 0
fi
tmp="$(mktemp)"
"$(dirname "${BASH_SOURCE[0]}")/project-meta.sh" > "$tmp"
osc_cmd meta prj -F "$tmp" "$project"
rm -f "$tmp"
echo "project ready: $project"
