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
# npm-bundle packages ship their dependency closure as ONE
# node_modules.obscpio (the cockpit legacy-container model: the OBS worker
# auto-unpacks any *.obscpio source flat into %{_sourcedir}). The
# container is regenerated client-side by fetch.sh --vendor and uploaded
# by a LOCAL `just push` (like the rust vendor.tar.zst); the P filter
# also protects it from --delete on CI pushes, whose checkouts never have
# one — a bump without a local push would build against the stale set.
# node_modules.spec.inc lists the tarballs as Source10000+ registry URLs
# (flat rename) purely for SRPM provenance — no server-side download
# (download_files is disabled on api.opensuse.org; the obscpio IS the
# transport). The .tgz exclusion stays ANCHORED at the package root: it
# covers Source0 and the flat pre-flight expansion of the local
# node_modules cache (red: openclaw's first push shipped an empty
# node_modules and the build died on "Serving 0 packages").
if [ "${1:-}" = "--list" ]; then
    obs_rsync_excludes() {
        printf '%s\n' \
            --exclude=.osc --exclude=fetch.sh --exclude=bump.sh --exclude=BIN \
            --exclude='*.tar.gz' --exclude='/*.tgz' --exclude='*.zip' \
            --filter='P *.tar.zst' \
            --filter='P node_modules.obscpio'
    }
    obs_rsync_excludes
    exit 0
fi
echo "usage: obs-rsync.sh --list" >&2
exit 2
