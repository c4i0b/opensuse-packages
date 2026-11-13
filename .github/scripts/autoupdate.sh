#!/usr/bin/env bash
# Ported from the fedora-packages autoupdate model (Renovate was rejected
# there; see docs/autoupdate.md for the local reds that motivated this).
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
get() {
  local pkg="$1" url="$2" body headers code attempt wait src t0 t1 elapsed
  shift 2
  body="$tmp/.body.$$"; headers="$tmp/.hdr.$$"
  for attempt in 1 2 3 4 5; do
    t0="$(date +%s%N)"
    code="$(curl -s -o "$body" -D "$headers" -w '%{http_code}' "$@" "$url")" || true
    t1="$(date +%s%N)"
    elapsed=$(( (t1 - t0) / 1000000 ))
    rlrem="$(tr -d '\r' < "$headers" | awk 'tolower($1)=="x-ratelimit-remaining:"{print $2}' | head -1)"
    printf 'REQ\t%s\t%s\t%s\t%s\n' "$pkg" "$code" "$attempt" "${rlrem:--}" >> "$stats"
    if [ "$code" = 200 ]; then
      sleep "$SUCCESS_DELAY"
      cat "$body"
      return 0
    fi
    if [ "$code" = 403 ] || [ "$code" = 429 ]; then
      wait="$(tr -d '\r' < "$headers" | awk 'tolower($1)=="retry-after:"{print $2}' | head -1)"
      if [ -n "$wait" ]; then
        src=retry-after
      else
        src=computed
        wait=$(( RETRY_BASE * (1 << (attempt - 1)) + RANDOM % 2 ))
      fi
      echo >&2 "::notice::[rate] pkg=$pkg attempt=$attempt status=$code wait=$wait wait_src=$src elapsed=${elapsed}ms rlrem=${rlrem:--}"
      sleep "$wait"
    else
      return 1
    fi
  done
  return 1
}

resolve() {
  upstream_file="$1"
  pkg="$(basename "$(dirname "$upstream_file")")"
  source="$(cat "$upstream_file")"

  auth=()
  [ -n "${GITHUB_TOKEN:-}" ] && auth=(-H "Authorization: Bearer $GITHUB_TOKEN")
  if [[ "$source" == tags:* ]]; then
    # tags-only repos: ls-remote is forge-agnostic and costs no API quota
    local repo_url="${source#tags:}"
    case "$repo_url" in
      gitlab:*) repo_url="https://gitlab.com/${repo_url#gitlab:}" ;;
      codeberg:*) repo_url="https://codeberg.org/${repo_url#codeberg:}" ;;
      *) repo_url="https://github.com/$repo_url" ;;
    esac
    latest="$(git ls-remote --tags --sort=-v:refname "$repo_url" 2>/dev/null \
      | awk '!/\^\{\}/ {sub(/^refs\/tags\//, "", $2); print $2}' \
      | while IFS= read -r t; do
          # strict pass first: plain v<version> tags only. Component tags
          # (anomalyco/opencode's vscode-v1.0.0) pollute the prefix-stripped
          # pass and resolve as downgrades.
          [[ "${t#v}" =~ ^[0-9][A-Za-z0-9._+~-]*$ ]] && { printf '%s\n' "${t#v}"; break; }
        done | head -1)"
    if [ -z "$latest" ]; then
      # fallback for prefixed tags (openai/codex's rust-v0.163.0): strip
      # the prefix, keep the version part
      latest="$(git ls-remote --tags --sort=-v:refname "$repo_url" 2>/dev/null \
        | awk '!/\^\{\}/ {sub(/^refs\/tags\//, "", $2); print $2}' \
        | while IFS= read -r t; do
            t="$(sed -E 's/^.+-v([0-9])/\1/' <<<"$t")"
            [[ "${t#v}" =~ ^[0-9][A-Za-z0-9._+~-]*$ ]] && { printf '%s\n' "${t#v}"; break; }
          done | head -1)"
    fi
  elif [[ "$source" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
    body="$(get "$pkg" "https://api.github.com/repos/${source}/releases/latest" "${auth[@]}")" || true
    latest="$(grep -oE '"tag_name": ?"[^"]*"' <<<"$body" | head -1 | cut -d'"' -f4)" || true
    latest="${latest#v}"
  elif [[ "$source" == npm:* ]]; then
    npm_pkg="${source#npm:}"
    npm_slug="$(echo "$npm_pkg" | sed 's|/|%2f|')"
    body="$(get "$pkg" "https://registry.npmjs.org/${npm_slug}/latest")" || true
    latest="$(grep -oE '"version": ?"[^"]*"' <<<"$body" | head -1 | cut -d'"' -f4)" || true
  fi
  if [ -z "$latest" ] && [[ "$source" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
    # Tag-only repos (no GitHub Releases): fall back to the latest tag
    body="$(get "$pkg" "https://api.github.com/repos/${source}/tags?per_page=1" "${auth[@]}")" || true
    latest="$(grep -oE '"name": ?"[^"]*"' <<<"$body" | head -1 | cut -d'"' -f4)" || true
    latest="${latest#v}"
  fi

  if [ -z "$latest" ]; then
    echo "::warning::$pkg: could not resolve latest release of $source"
    return 0
  fi
  latest="$(sed -E 's/^.+-v([0-9])/\1/' <<<"$latest")"
  printf 'latest\t%s\t%s\n' "$pkg" "$latest" > "$resolved/$pkg"
}

find "$root/packages" -name upstream -maxdepth 2 \
  | xargs -P 8 -I{} bash -c "$(declare -f get resolve); resolve \"{}\""

packages="$(mktemp)"
bumped=0
bumped_pkgs=()
for f in "$resolved"/*; do
  [ -f "$f" ] || continue
  cat "$f"
done | sort > "$packages"

while IFS=$'\t' read -r _ pkg latest; do
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
    printf 'pkgs=%s\n' "${bumped_pkgs[*]}"
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
  } >> "$GITHUB_STEP_SUMMARY"
fi
