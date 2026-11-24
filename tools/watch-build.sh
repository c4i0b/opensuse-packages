#!/usr/bin/env bash
# Watch OBS until every package reaches a fresh terminal state, then report
# and exit non-zero if anything failed. Uses `osc results --xml`, not --csv:
# the CSV row keeps the old `failed` code even when the result is marked
# dirty="true" (outdated), so a stale result used to look like a fresh
# failure. Dirty results count as pending, never as failures.
set -euo pipefail

project="home:${OBS_USER:-caiobruno}"
interval="${1:-90}"
deadline="${2:-7200}"  # seconds; 0 disables the timeout
api="${OBS_API:-https://api.opensuse.org}"
helper="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/obs_results.py"
xml="$(mktemp)"
trap 'rm -f "$xml"' EXIT

fetch() {
    osc -A "$api" results "$project" --xml >"$xml" 2>/dev/null || : >"$xml"
}
classify() { python3 "$helper" <"$xml"; }

echo "watching ${project} (poll ${interval}s, timeout ${deadline}s)..."
empty=0
while :; do
    fetch
    mapfile -t rows < <(classify)
    # A transient osc failure (oscrc mount race, API hiccup) yields no XML:
    # treating that as "nothing pending" would report a false green.
    if [ "${rows[0]:-}" = "EMPTY" ]; then
        empty=$((empty + 1))
        if [ "$empty" -ge 3 ]; then
            echo "error: osc results returned no rows 3x; aborting watch (no verdict)" >&2
            exit 2
        fi
    else
        empty=0
        pending=0
        for row in "${rows[@]}"; do
            case "$row" in PENDING*) pending=$((pending + 1));; esac
        done
        [ "$pending" -eq 0 ] && break
        echo "  ${pending} build(s) still in flight..."
    fi
    # An outdated result waits for the scheduler to dispatch a rebuild;
    # without a deadline that could hang forever (seen in practice).
    if [ "$deadline" -gt 0 ] && [ "$SECONDS" -ge "$deadline" ]; then
        echo "error: builds still pending after ${deadline}s; if OBS left them outdated, run 'just osc rebuild ${project}'" >&2
        exit 2
    fi
    sleep "$interval"
done

# fresh verdict: do not reuse a snapshot that may have changed while sleeping
fetch
mapfile -t rows < <(classify)
if [ "${rows[0]:-}" = "EMPTY" ]; then
    echo "error: osc results returned no rows at verdict time (no verdict)" >&2
    exit 2
fi

bad=0
for row in "${rows[@]}"; do
    IFS='|' read -r kind pkg target state <<<"$row"
    [ "$kind" = "BAD" ] || continue
    echo "FAILED: ${pkg} (${target}: ${state})"
    bad=$((bad + 1))
done

if [ "$bad" -gt 0 ]; then
    echo "${bad} package(s) failed"
    exit 1
fi
echo "all builds fresh and terminal, none failed"
