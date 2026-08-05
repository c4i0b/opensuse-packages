# opensuse-packages

Personal packaging monorepo for [OBS](https://build.opensuse.org).

## Layout

Each top-level directory is a **category** and maps 1:1 to an OBS subproject.
Each package lives in `<category>/<name>/` and mirrors one OBS package.

```
<category>/<name>/            OBS: home:<USER>:<category>/<name>
```

| category | OBS project             |
|----------|-------------------------|
| tools    | home:`<USER>`:tools     |
| apps     | home:`<USER>`:apps      |

Categories are independent OBS projects, each with its own published
repository. Packages that depend on each other must live in the same category.

## Setup

Set `OBS_USER` (and `OBS_API` if needed) at the top of the `justfile`.

    just bootstrap
    just osc-config

OBS credentials live in `~/.oscrc` (in your home, never in this repo). Create
it by running any `osc` command once, e.g.
`osc -A https://api.opensuse.org ls home:<USER>`, which prompts for your
user/password and writes `~/.oscrc` (mode 0600). The gitignore also blocks any
credential-like file as a safety net.

## Workflow

    just create-project tools                create/Update the OBS project meta
    just new-pkg    <category>/<name>        create the OBS package + local checkout
    just checkout   <category>/<name>        refresh the local osc working copy
    just push       <category>/<name> "msg"  sync files and commit to OBS (asks)
    just status     <category>/<name>        osc status

OBS working copies live under `~/obs/` (outside this repo) so the git tree
stays clean of `.osc/` metadata and credentials.

Packages can be built and tested locally in a container (host stays clean)
before pushing:

    just fetch <pkg>            run the package fetch.sh (if present)
    just build <pkg>            build the package (podman: RPM via rpm-build, or Dockerfile)
    just run   <pkg> [args...]  smoke-test: install the RPM / run the image

`<pkg>` is `<category>/<name>`. Builds run inside `registry.opensuse.org/opensuse/tumbleweed`
with `HOME=/tmp`. Pass flags directly, e.g. `just run <pkg> --version`.

Version bump (if the package ships a `bump.sh`):

    just bump <pkg> <version>

## Automation

New upstream releases are picked up automatically:

1. [Renovate](https://renovatebot.com) (`renovate.json`) opens a PR bumping
   `VERSION`, `_service`, and the RPM `Version:` at once.
2. On merge to `main`, `.github/workflows/push-to-obs.yml` detects which
   packages changed and runs `just push` for each. OBS then rebuilds and
   publishes natively. Run manually with a package list:

       gh workflow run push-to-obs.yml -f packages=tools/opencode

The workflow needs two repository secrets:

| secret         | value                                  |
|----------------|----------------------------------------|
| `OBS_USER`     | OBS login (e.g. `caiobruno`)           |
| `OBS_PASSWORD` | an OBS app password (not your main one)|

`push` skips its interactive confirmation when `CI=true` (set by GitHub Actions).

## Conventions

- The root `justfile` is generic and package-agnostic. Anything specific to a
  package lives in that package dir as `fetch.sh`, `bump.sh`, and `VERSION`.
- `just push` excludes dev-only files (`fetch.sh`, `bump.sh`, `VERSION`,
  downloaded archives) so only real package sources reach OBS. A package may
  add its own `.obsignore` for extra exclusions.
- No binaries are committed. Sources are fetched by an OBS `_service`
  (server-side) or by the package `fetch.sh` (local).
- RPM packages build against `openSUSE:Tumbleweed`; container packages build
  on `registry.opensuse.org/opensuse/tumbleweed`.
