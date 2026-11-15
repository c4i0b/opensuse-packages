#!/usr/bin/env bash
# FF-merges the exact gated bump SHA into main. Called by autoupdate.yml
# after validate-packages.py passed on the bump branch. Never rebases and
# never merges anything but the validated SHA: if main moved during the
# gate, fail loudly and let the next scheduled run redo the bump.
set -euo pipefail

sha="${1:?usage: autoupdate-merge.sh <gated-sha>}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

git config --global --add safe.directory "$root"
git -C "$root" config user.name "github-actions[bot]"
git -C "$root" config user.email "41898282+github-actions[bot]@users.noreply.github.com"

git -C "$root" fetch origin main

if ! git -C "$root" merge-base --is-ancestor origin/main "$sha"; then
  echo "::error::origin/main advanced past the base of gated SHA $sha during the gate; refusing to merge an ungated rebase. The bump branch stays for inspection; the next run re-bumps." >&2
  exit 1
fi

git -C "$root" checkout -f main
git -C "$root" merge --ff-only "$sha"

# retry once on a transient network failure; a non-fast-forward rejection
# here means main moved in the race window — that must fail, not rebase
if ! git -C "$root" push origin main; then
  sleep 15
  git -C "$root" push origin main
fi
echo "merged $sha into main"
