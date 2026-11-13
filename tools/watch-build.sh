#!/usr/bin/env bash
# Watch in-flight OBS builds until every package reaches a terminal state,
# then report and exit non-zero if anything failed (the fedora-packages
# watch contract). Uses `osc results --watch` for the waiting and the CSV
# output for the verdict.
set -euo pipefail

project="home:${OBS_USER:-caiobruno}"
interval="${1:-90}"

echo "watching ${project} (polling every ${interval}s)..."
osc -A "${OBS_API:-https://api.opensuse.org}" results "$project" --watch

# verdict from the final state
mapfile -t rows < <(osc -A "${OBS_API:-https://api.opensuse.org}" \
    results "$project" --csv --show-excluded)

bad=0
for row in "${rows[@]}"; do
    state="$(awk -F'|' '{print $4}' <<<"$row")"
    pkg="$(awk -F'|' '{print $3}' <<<"$row")"
    case "$state" in
        failed|broken|unresolvable)
            echo "FAILED: $pkg ($state)"
            bad=$((bad + 1))
            ;;
    esac
done

if [ "$bad" -gt 0 ]; then
    echo "${bad} package(s) failed"
    exit 1
fi
echo "all builds terminal, none failed"
