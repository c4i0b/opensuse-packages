# Repo conventions

## Package layout

`packages/<name>/` is one OBS package (`home:caiobruno/<name>`).

- Required: `*.spec`.
- Optional: `_service` (OBS-side source fetch), `fetch.sh` (local source
  fetch), `bump.sh` (version bump helper), `BIN` (command name when it
  differs from the package name), `.obsignore` (extra push exclusions),
  `<name>.rpmlintrc` (per-package rpmlint filters), `<name>.changes`
  (changelog, merged into `%changelog` by OBS).

Dev-only files (`fetch.sh`, `bump.sh`, `BIN`, `.obsignore`) and archives
never reach OBS: `just push` excludes them.

## `-bin`-only policy

Every package ships upstream's official release artifacts as-is; OBS fetches
them via `_service`. Never introduce a source build without reading the
history below.

### Source builds: rejected

Source builds (superfile, television, opencode) were attempted and reverted
in 2026-08. They compile from upstream, but need vendored dependencies
(`cargo vendor` / `go mod vendor` / `bun install`) that are gitignored and
must be regenerated on a dev machine. The automation can only
automate what is in git, and OBS builds offline, so every update required a
manual `bump.sh` + `fetch.sh` + `just push`. Automation is the priority, so
all packages stay `-bin`: OBS fetches the official release ELF via
`_service` and updates are fully automatic. The three source-build packages
were removed from git and OBS.

## Versioning

Single source of truth: the spec's `Version:` tag. There is no `VERSION`
file — `bump.sh`/`fetch.sh` read the current version straight from the spec
(`awk '/^Version:/{print $2}'`). This keeps autoupdate bumps (spec +
`_service` only) from drifting out of sync with anything else.

## Repo hygiene

- Never commit archives: `*.tar.gz`, `*.tar.zst`, `*.rpm` are gitignored.
  OBS fetches real sources via `_service`; local builds use `fetch.sh`.
- Run `just lint` before pushing (catches CI-only mistakes locally).
- English only, concise prose. Comments only for non-obvious workarounds;
  full context lives in these docs.
