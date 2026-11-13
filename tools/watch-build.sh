#!/usr/bin/env bash
# Watch in-flight OBS builds until every package reaches a terminal state,
# then report and exit non-zero if anything failed (the fedora-packages
# watch contract). Uses `osc results --watch` for the waiting and the CSV
# output for the verdict.
set -euo pipefail

project="home:${OBS_USER:-caiobruno}"
interval="${1:-90}"

echo "watching ${project} (polling every ${interval}s)..."
# poll --csv until every package is terminal: the container's osc rejects
# `prjresults --watch` without --xml ("Please implement support...").
# CSV shape: "<pkg>;<state>;<state>..." — semicolon-separated, one state per
# repo/arch column (header row starts with "_"). Split on ';' (NOT '|') and
# inspect every state field, not a fixed column index.
INFLIGHT='scheduled|building|dispatching|sign|blocked|waiting'
while :; do
    mapfile -t rows < <(osc -A "${OBS_API:-https://api.opensuse.org}" \
        results "$project" --csv 2>/dev/null || true)
    pending=0
    for row in "${rows[@]}"; do
        pkg="${row%%;*}"
        [ "$pkg" = "_" ] && continue
        while IFS= read -r state; do
            grep -qxE "$INFLIGHT" <<<"$state" && pending=$((pending + 1))
        done < <(tr ';' '\n' <<<"$row" | tail -n +2)
    done
    [ "$pending" -eq 0 ] && break
    echo "  ${pending} build(s) still in flight..."
    sleep "$interval"
done

# verdict from the final state
mapfile -t rows < <(osc -A "${OBS_API:-https://api.opensuse.org}" \
    results "$project" --csv)

bad=0
for row in "${rows[@]}"; do
    pkg="${row%%;*}"
    [ "$pkg" = "_" ] && continue
    while IFS= read -r state; do
        case "$state" in
            failed|broken|unresolvable)
                echo "FAILED: $pkg ($state)"
                bad=$((bad + 1))
                ;;
        esac
    done < <(tr ';' '\n' <<<"$row" | tail -n +2)
done

if [ "$bad" -gt 0 ]; then
    echo "${bad} package(s) failed"
    exit 1
fi
echo "all builds terminal, none failed"
