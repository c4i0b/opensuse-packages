#!/usr/bin/env bash
# Bot model (Renovate was rejected repo-family-wide
# after three real failures; see docs/autoupdate.md for the local reds
# that motivated this).
# Resolves latest upstream versions in parallel, bumps serially, commits
# on a dated bump/ branch (never directly on main). The workflow gates the
# branch (validate-packages.py) and ff-merges the exact gated SHA; commits
# made with GITHUB_TOKEN fire no push events, so push-to-obs picks the
# merge up via workflow_run instead.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
job_start="$(date +%s)"

git config --global --add safe.directory "$root"
git -C "$root" config user.name "github-actions[bot]"
git -C "$root" config user.email "41898282+github-actions[bot]@users.noreply.github.com"

# bumps must pass the gate before reaching main: work on a side branch,
# the workflow merges the exact gated SHA (gh-actions-conventions rule 11)
branch="bump/$(date -u +%Y%m%d-%H%M)"
git -C "$root" checkout -b "$branch"

# fetches are network-bound: resolve all latest versions in parallel, then
# apply bumps serially so git commits never race
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
resolved="$tmp/resolved"; mkdir "$resolved"
stats="$tmp/stats"; : > "$stats"
bumps="$tmp/bumps"; : > "$bumps"
export resolved tmp stats root

SUCCESS_DELAY=0.3
RETRY_BASE=3
export SUCCESS_DELAY RETRY_BASE

# GitHub throttles bursts with 403/429 even when authenticated; stats lines
# are single appends, safe across the xargs workers


# spec-bearing packages without an `upstream` file are invisible to the
# bot; say so once per run instead of resolving silently (aggregated over 5)
# `if` (not &&-chains): a false last body leaves the while loop nonzero, and
# with pipefail + set -e that kills the script depending on directory order
no_upstream="$(find "$root/packages" -mindepth 1 -maxdepth 1 -type d | while IFS= read -r d; do
  if ls "$d"/*.spec >/dev/null 2>&1 && [ ! -f "$d/upstream" ]; then basename "$d"; fi
done | sort)"
if [ -n "$no_upstream" ]; then
  n_no_upstream="$(wc -l <<<"$no_upstream")"
  if [ "$n_no_upstream" -gt 5 ]; then
    echo "::warning::$n_no_upstream packages have no upstream file, not auto-updated: $(paste -sd, - <<<"$no_upstream")"
  else
    while IFS= read -r p; do
      echo "::warning::$p: no upstream file, not auto-updated"
    done <<<"$no_upstream"
  fi
fi

# resolution lives in tools/upstream_resolver.py (pure, unit-tested in
# tests/): same TSV contract as the old bash resolver, threads instead
# of xargs -P, identical annotation vocabulary
find "$root/packages" -name upstream -maxdepth 2 \
  | RESOLVER_STATS="$stats" python3 "$root/tools/upstream_resolver.py" "$resolved"

packages="$(mktemp)"
bumped=0
bumped_pkgs=()
for f in "$resolved"/*; do
  [ -f "$f" ] || continue
  cat "$f"
done | sort > "$packages"

while IFS=$'\t' read -r _ pkg latest csha; do
  # Manual pin: a commit message "autoupdate: override <version>" on the
  # package dir keeps the bot from re-bumping to an unwanted release
  if git -C "$root" log -1 --format=%B -- "packages/$pkg" \
    | grep -qiE "^autoupdate: override .*$latest"; then
    echo "$pkg: $latest manually overridden, skipping"
    continue
  fi
  # RPM forbids '-' in Version; sanitize and reject non-version shapes
  latest_rpm="$(printf '%s' "$latest" | sed 's/[- ]/./g')"
  if ! [[ "$latest_rpm" =~ ^[0-9][A-Za-z0-9._+]+$ ]]; then
    echo "::warning::$pkg: latest tag '$latest' has non-version characters, skipping"
    continue
  fi
  spec="$(ls "$root/packages/$pkg/"*.spec 2>/dev/null | head -1 || true)"
  if [ -z "$spec" ]; then
    echo "::warning::$pkg: no spec, skipping"
    continue
  fi
  current="$(awk '/^Version:/{print $2; exit}' "$spec")"
  if [ "$latest_rpm" = "$current" ]; then
    echo "$pkg: up to date ($current)"
    continue
  fi
  # Downgrade guard: GitHub's releases/latest is by publish date, not
  # version — a repo mixing component tags (anomalyco/opencode once
  # resolved 1.19.5 while 2.2.7 was current) must never roll the package
  # back. Switch the package's `upstream` to tags: to track the newest
  # version tag instead.
  if [ "$(printf '%s\n%s\n' "$current" "$latest_rpm" | sort -V | head -1)" = "$latest_rpm" ]; then
    echo "::warning::$pkg: resolved $latest_rpm <= current $current (releases/latest quirk?), skipping"
    continue
  fi

  echo "$pkg: $current -> $latest_rpm"
  # a per-package bump.sh wins when a package needs special handling;
  # one broken package must not abort the whole run
  if [ -x "$root/packages/$pkg/bump.sh" ]; then
    bump_cmd=("$root/packages/$pkg/bump.sh")
  else
    bump_cmd=("$root/tools/bump.sh" "$pkg")
  fi
  if ! "${bump_cmd[@]}" "$latest_rpm"; then
    echo "::warning::$pkg: bump to $latest_rpm failed, skipping"
    continue
  fi
  # commit:-tracked packages: the _service pins the source by sha, so a
  # bump must also move it (both the archive path and any sha-named
  # filename; GitHub serves short and full-sha archive URLs alike)
  if [ -n "${csha:-}" ]; then
    old_sha="$(grep -oE 'archive/[0-9a-f]{7,40}' "$root/packages/$pkg/_service" 2>/dev/null | head -1 | cut -d/ -f2)"
    if [ -n "$old_sha" ] && [ "$old_sha" != "$csha" ]; then
      sed -i "s|${old_sha}|${csha}|g" "$root/packages/$pkg/_service"
    fi
  fi
  # Vendored packages: regenerate the client-side artifacts and tracked
  # side files (requirements.txt, node_modules.spec.inc, ...) BEFORE
  # committing — a bump that cannot re-vendor ships a stale archive and
  # breaks the OBS build offline (red: solidcraft 0.43.0 with a 0.40.1
  # Cargo.lock). Reverting the worktree drops just this package's bump.
  # fetch.sh must actually SUPPORT --vendor: omo's is a bare local
  # pre-flight fetcher (no vendor mode) and would download a 246 MB
  # upstream binary into the package dir on every bump.
  if { [ -f "$root/packages/$pkg/fetch.sh" ] \
       && grep -q -- '--vendor' "$root/packages/$pkg/fetch.sh"; } \
     || grep -q 'vendor-deps' "$spec" \
     || grep -Eq 'go build -mod=vendor|cargo_build|__cargo' "$spec"; then
    # one retry for transient upstream hiccups (red: hermes-agent 0.23.2 —
    # codeload served a non-gzip body for a freshly-generated tag tarball)
    if ! bash "$root/tools/revendor.sh" "$pkg"; then
      sleep 20
      if ! bash "$root/tools/revendor.sh" "$pkg"; then
        echo "::warning::$pkg: revendor to $latest_rpm failed, reverting bump"
        git -C "$root" checkout -- "packages/$pkg"
        continue
      fi
    fi
  fi
  # Oversized artifacts must never enter the bump branch: GitHub
  # rejects the push and EVERY bump of the run is lost (red: omo's
  # pre-flight fetcher dropped a 246 MB binary; dnscontrol's and mise's
  # bumps died with it). Revert and skip just the offender.
  bigfile="$(git -C "$root" ls-files --others --exclude-standard "packages/$pkg" \
    | while IFS= read -r f; do [ "$(stat -c%s "$root/$f" 2>/dev/null || echo 0)" -gt 20000000 ] && echo "$f" && break; done)"
  if [ -n "$bigfile" ]; then
    echo "::warning::$pkg: $bigfile exceeds 20 MB, not committable — reverting bump"
    git -C "$root" checkout -- "packages/$pkg"
    git -C "$root" clean -qf -- "packages/$pkg"
    continue
  fi
  git -C "$root" add "packages/$pkg"
  git -C "$root" commit -m "chore($pkg): update to $latest_rpm"
  bumped=$((bumped + 1))
  bumped_pkgs+=("$pkg")
  printf '| %s | %s | %s |\n' "$pkg" "$current" "$latest_rpm" >> "$bumps"
done < "$packages"

# Keepalive: GitHub disables scheduled workflows after 60 idle days; an
# empty commit counts as activity and pushes nothing to OBS (no files
# changed -> push-to-obs resolves zero packages). It rides the bump branch
# like any other commit.
keepalive=0
last_commit="$(git -C "$root" log -1 --format=%ct)"
now="$(date +%s)"
if [ $((now - last_commit)) -gt $((45 * 86400)) ]; then
  git -C "$root" commit --allow-empty -qm "chore: keepalive"
  keepalive=1
fi

# REQ/RETRY stats were collected but never surfaced (the fedora
# rate-summary was half-ported): aggregate the stats file into one notice
packages_total="$(find "$root/packages" -name upstream -maxdepth 2 | wc -l)"
total_req="$(grep -c '^REQ' "$stats" || true)"
read -r c200 c403 c429 c404 minrl <<< "$(awk -F'\t' '$1=="REQ"{c[$3]++; if($5+0>0 && (m==0||$5+0<m)) m=$5+0} END{print c[200]+0, c[403]+0, c[429]+0, c[404]+0, m+0}' "$stats")"
cother=$(( total_req - c200 - c403 - c429 - c404 ))
# this port writes no RETRY lines: a retry is any REQ with attempt > 1
retries="$(awk -F'\t' '$1=="REQ" && $4>1' "$stats" | wc -l)"
final_fail=$(( packages_total - $(find "$resolved" -type f | wc -l) ))
wall=$(( $(date +%s) - job_start ))
# a 404 on releases/latest is expected for tags-only repos (the fallback
# resolves them), so it gets its own bucket instead of polluting "other"
summary="packages=$packages_total bumped=$bumped requests=$total_req ok200=$c200 throttled403=$c403 throttled429=$c429 fallback404=$c404 other=$cother retries=$retries final_failures=$final_fail min_rlrem=$minrl wall=${wall}s"
echo "::notice::[rate-summary] $summary"

count=$((bumped + keepalive))
if [ "$count" -gt 0 ]; then
  # transient network only: the branch name is unique, no race to lose
  git -C "$root" push origin "$branch" \
    || (sleep 15; git -C "$root" push origin "$branch")
fi

if [ -n "${GITHUB_OUTPUT:-}" ]; then
  {
    printf 'branch=%s\n' "$branch"
    printf 'sha=%s\n' "$(git -C "$root" rev-parse HEAD)"
    # packages/ prefix: validate-packages.py (and validate.yml's detector)
    # address package dirs as packages/<name> — a bare name globs nothing
    # and the gate fails with a bogus "no spec" (red: pear-desktop 3.12.1)
    printf 'pkgs=%s\n' "${bumped_pkgs[*]/#/packages/}"
    printf 'count=%s\n' "$count"
  } >> "$GITHUB_OUTPUT"
fi

if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo "## autoupdate"
    echo
    if [ -s "$bumps" ]; then
      echo "| package | from | to |"
      echo "|---|---|---|"
      cat "$bumps"
    else
      echo "no updates this run"
    fi
    echo
    echo '```'
    echo "$summary"
    echo '```'
  } >> "$GITHUB_STEP_SUMMARY"
fi
