set shell := ["bash", "-cu"]

repo          := justfile_directory()
OBS_NAME      := "Caio Bruno"
OBS_EMAIL     := "cbrunofb@gmail.com"
OBS_ARCH      := "x86_64"

export OBS_USER := "caiobruno"
export OBS_API  := "https://api.opensuse.org"
export OBS_REPO := "opensuse_tumbleweed"

# Recipes run inside the ephemeral tooling container (compose.yml); CI and
# hosts with a full toolchain set OPENSUSE_PACKAGES_DIRECT=1
runner := `[ "${OPENSUSE_PACKAGES_DIRECT:-}" = 1 ] || printf 'podman compose run --rm tooling'`

@default:
    just --list --unsorted

# Build (or rebuild) the tooling container image; also points git at the
# versioned hooks (idempotent). Re-run after Containerfile changes.
image:
    #!/usr/bin/env sh
    set -eu
    podman compose build tooling
    git config core.hooksPath .githooks

# Interactive bash in the tooling container (repo bind-mounted at /app)
shell:
    {{runner}} bash

# Lint changed spec files (catches CI-only mistakes locally; run before push)
lint:
    {{runner}} python3 opensuse-lint.py

# Lint every spec under packages/
lint-all:
    {{runner}} python3 opensuse-lint.py --all

# Local pre-flight RPM build of one package, gated on rpmlint errors
build pkg:
    {{runner}} tools/build.sh {{pkg}}

# Smoke-test a built package: install the RPMs in the ephemeral container
run pkg +args:
    {{runner}} tools/run.sh {{pkg}} {{args}}

# Sync one package to OBS (lint gate runs first; confirm before commit)
push pkg msg:
    {{runner}} tools/push.sh {{pkg}} "{{msg}}"

# Fetch the current sources of one package (fetch.sh)
fetch pkg:
    {{runner}} "{{repo}}/{{pkg}}/fetch.sh"

# Bump a package version (runs its bump.sh)
bump pkg version:
    {{runner}} "{{repo}}/{{pkg}}/bump.sh" "{{version}}"

# Create (or re-apply) the OBS project from _project.meta.xml (force=1)
create-project force="0":
    {{runner}} tools/setup-obs.sh {{force}}

# Create the OBS package metadata from the spec, then check it out
new-pkg pkg:
    {{runner}} tools/new-pkg.sh {{pkg}}

# Ensure an up-to-date osc working copy of one package
checkout pkg:
    {{runner}} tools/checkout.sh {{pkg}}

# Raw osc inside the tooling container
osc +args:
    {{runner}} osc -A {{OBS_API}} {{args}}

# Show OBS build results of one package
results pkg:
    {{runner}} osc -A {{OBS_API}} results "home:{{OBS_USER}}" "$(basename {{pkg}})"

# Whole-project build status snapshot (all packages, both arches)
status:
    {{runner}} osc -A {{OBS_API}} results "home:{{OBS_USER}}"

# Watch in-flight builds until all finish; non-zero if any failed
watch interval="90":
    {{runner}} tools/watch-build.sh {{interval}}

# Show the OBS buildlog of one package (opensuse_tumbleweed x86_64)
log pkg:
    {{runner}} osc -A {{OBS_API}} buildlog "home:{{OBS_USER}}" "$(basename {{pkg}})" {{OBS_REPO}} {{OBS_ARCH}}

# Prepend a dated entry to <pkg>/<name>.changes (host-side: opens $EDITOR)
vc pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    name="$(echo {{pkg}} | cut -d/ -f2)"
    f="{{repo}}/{{pkg}}/${name}.changes"
    ts="$(date -u +"%a %b %e %H:%M:%S UTC %Y")"
    tmp="$(mktemp)"
    {
      printf -- "-------------------------------------------------------------------\n"
      printf -- "%s - %s <%s>\n\n" "$ts" "{{OBS_NAME}}" "{{OBS_EMAIL}}"
      printf -- "- \n\n"
      cat "$f"
    } > "$tmp"
    mv "$tmp" "$f"
    "${EDITOR:-vi}" "$f"
