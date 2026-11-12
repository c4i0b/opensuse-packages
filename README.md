# opensuse-packages

Personal RPM packaging monorepo for [OBS](https://build.opensuse.org),
hosted in the
[`home:caiobruno`](https://build.opensuse.org/project/show/home:caiobruno)
project (openSUSE Tumbleweed). The GitHub repo is the source of truth: a
merge to `main` triggers `push-to-obs`, which syncs the touched packages to
OBS, where they are built.

[![push-to-obs](https://github.com/c4i0b/opensuse-packages/actions/workflows/push-to-obs.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/push-to-obs.yml)
[![validate-bump](https://github.com/c4i0b/opensuse-packages/actions/workflows/validate-bump.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/validate-bump.yml)
[![autoupdate](https://github.com/c4i0b/opensuse-packages/actions/workflows/autoupdate.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/autoupdate.yml)
[![badges](https://github.com/c4i0b/opensuse-packages/actions/workflows/badges.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/badges.yml)

## Build status

<!-- repo-badges begin -->
[![tumbleweed aarch64](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fopensuse-tumbleweed-aarch64.json%3Fv%3D6r2)](https://build.opensuse.org/project/monitor?project=home%3Acaiobruno)
[![tumbleweed x86_64](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fopensuse-tumbleweed-x86_64.json%3Fv%3D6r2)](https://build.opensuse.org/project/monitor?project=home%3Acaiobruno)
<!-- repo-badges end -->

## Per-package build

<!-- package-badges begin -->
[![fisher](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffisher.json%3Fv%3D4.4.8r2)](https://github.com/jorgebucaran/fisher/)
[![pear-desktop-bin](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpear-desktop-bin.json%3Fv%3D3.12.0r2)](https://github.com/pear-devs/pear-desktop/)
[![superfile-bin](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fsuperfile-bin.json%3Fv%3D1.6.0r2)](https://github.com/yorukot/superfile/)
[![television-bin](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ftelevision-bin.json%3Fv%3D0.15.9r2)](https://github.com/alexpasmantier/television/)
[![ytm-player](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fytm-player.json%3Fv%3D2.2.0r2)](https://github.com/peternaame-boop/ytm-player/)
<!-- package-badges end -->

## Install (openSUSE Tumbleweed)

    zypper ar -f https://download.opensuse.org/repositories/home:/caiobruno/opensuse_tumbleweed/home:caiobruno.repo
    zypper ref
    zypper in <package>

## How it works

- `packages/<name>/` — one OBS package. Required: `*.spec`. Optional:
  `_service`, `fetch.sh`, `bump.sh`, `BIN`, `.obsignore`, `<name>.rpmlintrc`,
  `<name>.changes`.
- `_project.meta.xml` — OBS project template (repos, arches).
- Each package's `_service` tells OBS to fetch official upstream release
  artifacts server-side, so no archives are committed.
- A scheduled workflow (`autoupdate`) checks upstream releases (per
  package's `upstream` file) and bumps the spec and `_service`
  automatically; Dependabot keeps Actions updated.

See [docs/](docs/README.md) for the full picture.

## Development

The host needs only `just` + `podman` — everything else runs in the
ephemeral tooling container ([docs/environment.md](docs/environment.md)).

    just image                      # once: build the tooling container + wire hooks
    just lint                       # lint the repo (run before push)
    just build packages/<name>      # pre-flight local rpmbuild, rpmlint-gated
    just push packages/<name> "msg" # lint, then sync to OBS and commit

## Adding a package

1. `just new-pkg <name>` — scaffold from [templates/](templates/)
   (`templates/*.spec.tpl`) and fill the OBS title/description from the
   spec.
2. Add a `_service` so OBS fetches upstream sources, plus `bump.sh`/
   `fetch.sh` for version updates.
3. Add `packages/<name>/upstream` (`owner/repo`, `tags:owner/repo` or
   `npm:<package>`) so autoupdate tracks it.
4. `just push packages/<name> "initial package"` — the package only exists
   on OBS after push.
5. Manual bump, if ever needed: `just bump packages/<name> <version>`.
