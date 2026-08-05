# opensuse-packages

Personal packaging monorepo for [OBS](https://build.opensuse.org).

## Install (openSUSE Tumbleweed)

    zypper ar -f https://download.opensuse.org/repositories/home:/caiobruno/openSUSE_Tumbleweed/home:caiobruno.repo
    zypper ref
    zypper in <package>

## Commands

`just --list` for all. Key ones:

- `just build packages/<name>` — RPM build in a container
- `just push packages/<name> "msg"` — sync to OBS
- `just lint` — catch CI mistakes
- `just bump packages/<name> <ver>` — bump version

## Add a package

1. Create `packages/<name>/` with a `.spec` — use `packages/opencode-bin/` as a template.
2. `just create-project`
3. `just push packages/<name> "initial package"`

Track upstream releases via `renovate.json`.

## Automation

Renovate opens bump PRs (auto-merged after `validate-bump` passes); `push-to-obs`
syncs to OBS on merge. Dependabot keeps Actions updated (auto-merged after a
YAML+justfile gate). Secrets: `OBS_USER`, `OBS_PASSWORD`.

osc runs via distrobox (`just obs-create`); CI sets `OSC_RUN=""` for host osc.
