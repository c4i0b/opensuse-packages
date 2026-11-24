#!/usr/bin/env python3
"""Classify `osc results PROJECT --xml` rows for tools/watch-build.sh.

`osc results --csv` drops the result-level `dirty` flag: the row still shows
the old `failed` code (only the header column says `outdated`), so watching
the CSV reports stale results as fresh failures. Here a dirty result stays
PENDING — it is awaiting a rebuild that OBS has not dispatched yet — and
never becomes BAD.

Output (one row per status): PENDING|pkg|repo/arch|state or
BAD|pkg|repo/arch|state. EMPTY marks a transient/unparseable fetch.
"""
import sys
import xml.etree.ElementTree as ET

INFLIGHT = {"scheduled", "building", "dispatching", "sign", "blocked",
            "waiting", "uploading"}
BAD = {"failed", "broken", "unresolvable", "expansion error"}


def classify(text):
    """Return the actionable rows of an `osc results --xml` document."""
    root = ET.fromstring(text)
    rows = []
    for result in root.findall("result"):
        target = f"{result.get('repository')}/{result.get('arch')}"
        stale = result.get("dirty") == "true"
        statuses = result.findall("status")
        if stale and not statuses:
            rows.append(("PENDING", "*", target, "outdated"))
        for status in statuses:
            pkg = status.get("package") or "*"
            code = status.get("code") or ""
            if stale:
                rows.append(("PENDING", pkg, target,
                             f"outdated (was: {code})"))
            elif code in INFLIGHT:
                rows.append(("PENDING", pkg, target, code))
            elif code in BAD:
                rows.append(("BAD", pkg, target, code))
    return rows


def main():
    text = sys.stdin.read()
    try:
        rows = classify(text)
    except ET.ParseError:
        print("EMPTY")
        return
    if not rows:
        return
    for row in rows:
        print("|".join(row))


if __name__ == "__main__":
    main()
