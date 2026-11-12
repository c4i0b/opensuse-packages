# Development environment

The host provides only `just` + `podman`: every recipe transparently runs in
the `tooling` container, an **ephemeral** openSUSE Tumbleweed environment
defined by `Containerfile` + `compose.yml` and started via
`podman compose run --rm tooling`. No state survives a run; anything the
environment needs must be in the image — if it is not in the `Containerfile`,
it does not exist. `OPENSUSE_PACKAGES_DIRECT=1` runs commands directly on the
host instead (escape hatch for CI or hosts without podman).

## Lifecycle

- `just image` builds the image and wires the versioned git hooks
  (`core.hooksPath` → `.githooks`) — re-run after `Containerfile` changes.
- `just shell` opens an interactive shell in the container with the repo
  bind-mounted.
- `just --list` lists every recipe: `image`, `shell`, `lint`, `lint-all`,
  `build`, `push`, `fetch`, `bump`, `run`, `vc`, `osc`, `checkout`,
  `new-pkg`, `create-project`, `results`, `log`.

## Credentials and state

- `osc` runs **inside** the container. The host `~/.oscrc` (OBS credentials)
  is mounted read-only into it: point the `OSCRC` env var at your oscrc file
  (e.g. in your shell profile: `export OSCRC=$HOME/.oscrc`). Without it the
  mount is an empty placeholder: lint and build work, osc commands fail auth.
- The OBS checkout workspace is `work/` in the repo (gitignored): it persists
  on the host through the repo bind mount. `just checkout <name>`
  materializes a package there; `just osc`, `just results`, `just log`
  operate on it.
- The container HOME is ephemeral, so no tool state can go stale between
  runs.
- git push / gh are HOST-side only; do not require them inside the container.

## Hooks

`.githooks/pre-commit` is a thin wrapper: it runs the linter wherever
`python3` lives — directly inside the container (`just shell`), or through
the container runtime when invoked by host git.

## Recipe logic

Recipe logic lives in `tools/*.sh`; the justfile stays a thin dispatcher —
put new logic in a script, not inline in the justfile.
