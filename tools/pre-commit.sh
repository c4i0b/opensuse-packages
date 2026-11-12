#!/usr/bin/env bash
# Pre-commit gate: lint the specs of every staged package.
set -euo pipefail
repo="$(repo_root 2>/dev/null || pwd)"
# shellcheck source=lib.sh
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"

fail=0
pkgs=""
while IFS= read -r file; do
  case "$file" in
    packages/*)
      pkg="${file#packages/}"; pkg="${pkg%%/*}"
      case " $pkgs " in *" $pkg "*) ;; *) pkgs="$pkgs $pkg" ;; esac
      ;;
  esac
done < <(git diff --cached --name-only --diff-filter=ACMR)

[ -z "$pkgs" ] && exit 0
specs=""
for pkg in $pkgs; do
  dir="$repo/packages/$pkg"
  [ -d "$dir" ] || continue
  for spec in "$dir"/*.spec; do
    [ -f "$spec" ] && specs="$specs $spec"
  done
done
[ -z "$specs" ] && exit 0

python3 "$repo/opensuse-lint.py" $specs || fail=1
exit "$fail"
