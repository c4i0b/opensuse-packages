#!/usr/bin/env bash
# Single definition of the rsync exclude/protect list for syncing a package
# dir to OBS. Sourced via --list by tools/push.sh and the push-to-obs
# workflow so the two can never drift.
#
# Dev-only files never reach OBS (_service fetches the real sources
# server-side). Client-side vendor archives (rust vendor.tar.zst) live
# outside git: --filter=P uploads them when present locally but protects
# them from --delete when a checkout lacks them (a CI checkout never has
# one) — plain --exclude would never upload and a bare transfer would
# wipe them server-side.
#
# npm-bundle packages need no tarball upload at all: node_modules.spec.inc
# lists the dependency tarballs as Source10000+ registry URLs that the
# download_files _service fetches server-side (cockpit model). The ONE
# exception is an npm-packed bundled dep (no registry URL — openclaw's
# chrome-devtools-mcp): it travels as a bare local-file Source, so it gets
# its own P filter. The .tgz exclusion stays ANCHORED at the package root:
# it covers Source0 and the flat pre-flight expansion of the local
# node_modules cache (red: openclaw's first push shipped an empty
# node_modules and the build died on "Serving 0 packages").
if [ "${1:-}" = "--list" ]; then
    obs_rsync_excludes() {
        printf '%s\n' \
            --exclude=.osc --exclude=fetch.sh --exclude=bump.sh --exclude=BIN \
            --exclude='*.tar.gz' --exclude='/*.tgz' --exclude='*.zip' \
            --filter='P *.tar.zst' \
            --filter='P chrome-devtools-mcp-*.tgz'
    }
    obs_rsync_excludes
    exit 0
fi
echo "usage: obs-rsync.sh --list" >&2
exit 2
