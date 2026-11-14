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

## Build models (source builds enabled 2026-11)

Packages build from source whenever the ecosystem allows it; the repo is
no longer `-bin`-only:

- **Python** — sdist via `_service download_url`, deps from Tumbleweed
  `python3-*` packages (see [packaging/python.md](packaging/python.md)).
- **Go** — `_service` with `tar_scm` + `go_modules`: the OBS server-side
  service vendors modules, nothing client-side is needed (reference:
  Factory/lazygit; template `go-source.spec.tpl`). `ExclusiveArch` must
  list arches explicitly — `%{go_arches}` is undefined in the Tumbleweed
  prjconf (the linter FAILs on it). go_modules only works while go.mod's
  `go` directive is <= the Go on the OBS source-service host (which lags
  the distro; `OBS_GO_MODULES_GO` in `opensuse-lint.py` is the ceiling and
  the lint FAILs above it — red: nexttrace 1.7.6 needed go 1.27.3, the
  service host ran 1.26, package broken with no logfile). Above the
  ceiling: client-side `vendor.tar.zst` + `BuildRequires: zstd`, like
  Rust (reference: dnscontrol, nexttrace); bumps stay manual until the
  service host catches up.
- **Rust** — `cargo_vendor` is NOT in the OBS server-side service
  allowlist: the vendor archive is generated client-side (`vendor.tar.zst`,
  gitignored, OBS-only; template `rust-source.spec.tpl` documents the
  command). Consequence: no `upstream` file until vendor regeneration is
  automated — bumps are manual for Rust packages.
- **Electron** — no node vendoring exists on OBS; package as an
  upstream-RPM repackage (template `rpm-repackage.spec.tpl`), never as a
  source compile. Strip must be disabled in the spec: stripping corrupts
  the embedded snapshot (fedora-packages red).
- `-bin` suffix is gone; the only prebuilt registry entry left is
  `pear-desktop` (`PREBUILT_ORIGIN` in `opensuse-lint.py`).
- Toolchains (`rustc`/`go`/`python`) come from the distro; never pin a
  compiler version in a spec.

### Source builds: rejected 2026-08, un-rejected 2026-11

The 2026-08 rejection (vendored deps gitignored, regenerated per dev
machine, un-automatable) held while updates ran through Renovate PRs and
the only known vendoring was client-side. Two things changed: OBS
server-side services (`go_modules`) do the vendoring server-side for Go,
and updates now run through our own autoupdate bot, which can be taught
whatever the repo needs. The 2026-11 conversion validated the model end
to end on OBS.

## Versioning

Single source of truth: the spec's `Version:` tag. There is no `VERSION`
file — `bump.sh`/`fetch.sh` read the current version straight from the spec
(`awk '/^Version:/{print $2}'`). This keeps autoupdate bumps (spec +
`_service` only) from drifting out of sync with anything else.

## Fix for the long term

A fix that only repairs the current instance dies at the next bump.

1. **Single definition** — one `%global` (or spec field) per repeated
   constant; every other occurrence derives from it. (Red: the desktop
   id `ai.storyteller.<name>` was pasted 4× per craft spec — a rename
   meant chasing every line in every sibling.)
2. **Derive from upstream metadata/globs** — never hardcode what
   upstream controls (versions, asset names, file lists); expand from
   `Version:` or globs so a bump needs no spec edits.
3. **Seds/selectors carry a grep guard** — any bump script that seds or
   selects a value must grep the result back and fail loud, not freeze
   silently (red: ytm-player's asset name stuck at 2.0.0 while the
   directory said 2.2.0).
4. **Class knowledge lives in docs/templates, not spec-local
   comments** — and check the sibling packages: one member's fix
   usually applies to the family (red: the rustc worker-OOM
   mitigation lives in only 5 of the 14 craft siblings; the rest are
   one bad link away from the same OOM kill).

## Repo hygiene

- Never commit archives: `*.tar.gz`, `*.tar.zst`, `*.rpm` are gitignored.
  OBS fetches real sources via `_service`; local builds use `fetch.sh`.
- Run `just lint` before pushing (catches CI-only mistakes locally).
- English only, concise prose. Comments only for non-obvious workarounds;
  full context lives in these docs.
