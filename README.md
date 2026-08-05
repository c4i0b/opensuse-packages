# opensuse-packages

Personal packaging monorepo for [OBS](https://build.opensuse.org).

## Layout

Each top-level dir is a **category** (local organization only). All packages
go to one OBS project `home:<USER>`.

| category | local dir  |
|----------|------------|
| tools    | tools/     |
| apps     | apps/      |

## Add a package

1. Create `<category>/<name>/` with a `.spec` — use `tools/opencode-bin/` as a
   template (`VERSION`, `fetch.sh`, `bump.sh` optional; `BIN` only if the command
   name differs from the package name).
2. `just create-project`
3. `just push <category>/<name> "initial package"`

Track upstream releases by adding an entry to `renovate.json` (mirror the
`opencode-bin` block). New packages are discovered/installed via OBS the same
way as `opencode-bin`.

## Install (openSUSE Tumbleweed)

    zypper ar -f https://download.opensuse.org/repositories/home:/caiobruno/openSUSE_Tumbleweed/home:caiobruno.repo
    zypper ref
    zypper in opencode

`tools/opencode-bin` ships the upstream prebuilt binary; it `Provides: opencode`,
so `zypper in opencode` resolves to it. Command: `/usr/bin/opencode`.

## Setup

Set `OBS_USER`, `OBS_NAME`, `OBS_EMAIL` at the top of the `justfile`.

    just bootstrap
    just obs-create     create the 'obs' distrobox (osc/git/build)
    just obs-login      one-time: log in as OBS_USER (writes ~/.oscrc in the distrobox)

All `osc` calls go through the distrobox by default; set `OSC_RUN=""` to use a
host `osc` instead (this is what CI does).

## Workflow

    just create-project <category>            create/Update OBS project meta
    just push   <category>/<name> "msg"       sync files and commit to OBS (asks)
    just bump   <category>/<name> <version>   bump version (if the package has bump.sh)

OBS working copies live under `~/obs/` (outside this repo).

Build/test locally (in a container, host stays clean):

    just build <pkg>            build (podman: RPM via rpm-build, or Dockerfile)
    just run   <pkg> [args...]  smoke-test (install the RPM / run the image)

Inspect OBS:

    just results <pkg>          build status
    just log    <pkg>           build log
    just vc     <pkg>           add a .changes entry (openSUSE format, opens $EDITOR)
    just osc    <osc args...>   run any osc command

`<pkg>` is `<category>/<name>`. Pass flags directly, e.g. `just run <pkg> --version`.

## Automation

1. [Renovate](https://renovatebot.com) (`renovate.json`) opens a PR bumping
   `VERSION`, `_service` and the spec `Version:` atomically; on a green
   `validate-bump` check it **auto-merges**.
2. `.github/workflows/push-to-obs.yml` then pushes changed packages to OBS,
   which rebuilds and publishes.

Manual run: `gh workflow run push-to-obs.yml -f packages=tools/opencode-bin`
Secrets: `OBS_USER`, `OBS_PASSWORD`.

## Conventions

- The `justfile` is generic; per-package bits live in `<pkg>/` (`fetch.sh`,
  `bump.sh`, `VERSION`, optional `BIN` = command name when it differs from the
  package name).
- `just push` excludes dev files (`fetch.sh`, `bump.sh`, `VERSION`, `BIN`,
  archives) from OBS; add `<pkg>/.obsignore` for more.
- `just new-pkg` fills the OBS package `<title>`/`<description>` from the spec.
- Sources are fetched by an OBS `_service` (server) or `fetch.sh` (local); RPMs
  build on `openSUSE:Tumbleweed`. Prebuilt binaries use
  `%global debug_package %{nil}` + `%global __strip /bin/true`.
