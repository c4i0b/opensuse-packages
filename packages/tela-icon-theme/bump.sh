#!/usr/bin/env bash
# Date-tagged upstream: delegates to the shared bump (tag + Version +
# _service + .changes in one place).
set -euo pipefail
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$(cd "$dir/../.." && pwd)/tools/bump-date-tag.sh" "$(basename "$dir")" "$@"
