# opensuse-packages

Personal RPM packaging monorepo for [OBS](https://build.opensuse.org),
hosted in the
[`home:caiobruno`](https://build.opensuse.org/project/show/home:caiobruno)
project (openSUSE Tumbleweed). The GitHub repo is the source of truth: a
merge to `main` triggers `push-to-obs`, which syncs the touched packages to
OBS, where they are built.

[![push-to-obs](https://github.com/c4i0b/opensuse-packages/actions/workflows/push-to-obs.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/push-to-obs.yml)
[![validate](https://github.com/c4i0b/opensuse-packages/actions/workflows/validate.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/validate.yml)
[![autoupdate](https://github.com/c4i0b/opensuse-packages/actions/workflows/autoupdate.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/autoupdate.yml)
[![badges](https://github.com/c4i0b/opensuse-packages/actions/workflows/badges.yml/badge.svg)](https://github.com/c4i0b/opensuse-packages/actions/workflows/badges.yml)

## Build status

<!-- repo-badges begin -->
[![tumbleweed aarch64](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fopensuse-tumbleweed-aarch64.json%3Fv%3D17r2)](https://build.opensuse.org/project/monitor?project=home%3Acaiobruno)
[![tumbleweed x86_64](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fopensuse-tumbleweed-x86_64.json%3Fv%3D19r2)](https://build.opensuse.org/project/monitor?project=home%3Acaiobruno)
<!-- repo-badges end -->

## Per-package build

<!-- package-badges begin -->
[![cadcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fcadcraft.json%3Fv%3D0.20.1r2)](https://github.com/storytold/cadcraft)
[![deckcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdeckcraft.json%3Fv%3D0.18.1r2)](https://github.com/storytold/deckcraft)
[![designcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fdesigncraft.json%3Fv%3D0.20.1r2)](https://github.com/storytold/designcraft)
[![effectcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Feffectcraft.json%3Fv%3D0.24.1r2)](https://github.com/storytold/effectcraft)
[![figcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffigcraft.json%3Fv%3D0.18.1r2)](https://github.com/storytold/figcraft)
[![filmcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffilmcraft.json%3Fv%3D0.20.1r2)](https://github.com/storytold/filmcraft)
[![fisher](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ffisher.json%3Fv%3D4.4.8r2)](https://github.com/jorgebucaran/fisher/)
[![gridcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fgridcraft.json%3Fv%3D0.19.1r2)](https://github.com/storytold/gridcraft)
[![lightcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Flightcraft.json%3Fv%3D0.21.1r2)](https://github.com/storytold/lightcraft)
[![pdfcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpdfcraft.json%3Fv%3D0.21.1r2)](https://github.com/storytold/pdfcraft)
[![pear-desktop](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fpear-desktop.json%3Fv%3D3.12.0r2)](https://github.com/pear-devs/pear-desktop/)
[![photocraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fphotocraft.json%3Fv%3D0.23.1r2)](https://github.com/storytold/photocraft)
[![solidcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fsolidcraft.json%3Fv%3D0.40.1r2)](https://github.com/tangency-labs/solidcraft)
[![soundcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fsoundcraft.json%3Fv%3D0.20.1r2)](https://github.com/storytold/soundcraft)
[![superfile](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fsuperfile.json%3Fv%3D1.6.0r2)](https://github.com/yorukot/superfile/)
[![television](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Ftelevision.json%3Fv%3D0.15.9r2)](https://github.com/alexpasmantier/television)
[![vectorcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fvectorcraft.json%3Fv%3D0.24.1r2)](https://github.com/storytold/vectorcraft)
[![wordcraft](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fc4i0b%2Fopensuse-packages%2Fmain%2Fbadges%2Fwordcraft.json%3Fv%3D0.18.1r2)](https://github.com/storytold/wordcraft)
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
