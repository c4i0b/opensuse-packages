#!/usr/bin/env bash
# Shared helpers for the opensuse-packages recipes.
set -euo pipefail

repo_root() { git rev-parse --show-toplevel; }

# osc checkout workspace: work/ inside the repo (gitignored, persists via the
# repo bind mount). Override with OSC_WORK for a different location.
osc_work() { echo "${OSC_WORK:-$(repo_root)/work}"; }

# tools/checkout.sh, new-pkg.sh and push.sh all split "category/name" into an
# OBS package name (the second path component).
pkg_name() { printf '%s' "$1" | cut -d/ -f2; }

spec_version() { awk '/^Version:/{print $2; exit}' "$1"; }

osc_cmd() { osc -A "${OBS_API:-https://api.opensuse.org}" "$@" </dev/null; }
