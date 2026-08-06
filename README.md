# opensuse-packages

Personal packaging monorepo for [OBS](https://build.opensuse.org).

## Install (openSUSE Tumbleweed)

    zypper ar -f https://download.opensuse.org/repositories/home:/caiobruno/opensuse_tumbleweed/home:caiobruno.repo
    zypper ref
    zypper in <package>

## Layout

- `packages/<name>/` — one OBS package. Required: `*.spec`. Optional:
  `_service`, `fetch.sh`, `bump.sh`, `BIN`, `.obsignore`.
- `_project.meta.xml` — OBS project template (repos/arches).
- `renovate.json` — dependency bump configuration.
- `.github/workflows/` — `validate-bump` (PR gate), `push-to-obs` (syncs on merge), `dependabot-automerge`.

## Add a package

1. Create `packages/<name>/` with a `.spec` — use `packages/opencode-bin/` as a template.
2. Add a `_service` so OBS fetches upstream sources, plus `bump.sh`/`fetch.sh` for version updates.
3. `push-to-obs` syncs it to OBS on merge.

## Automation

- Renovate opens bump PRs (auto-merged after `validate-bump` passes).
- `push-to-obs` syncs changed packages to OBS on merge; it drives `osc` directly
  (self-contained, no external tooling).
- Dependabot keeps Actions updated (auto-merged after a YAML gate).
- Secrets: `OBS_USER`, `OBS_PASSWORD`.
