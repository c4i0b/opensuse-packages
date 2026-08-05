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

Container packages (those with a `Dockerfile`) can be built and tested
locally before pushing:

    just fetch <pkg>            run the package fetch.sh (if present)
    just build <pkg>            podman build
    just run   <pkg> [args...]  run the image

`<pkg>` is `<category>/<name>`. `run` keeps the host clean: the container home
is under `/tmp`, only the current directory is mounted. Pass flags to the image
with `--`, e.g. `just run <pkg> -- --version` (otherwise `just` may consume them).

Version bump (if the package ships a `bump.sh`):

    just bump <pkg> <version>

## Automation

New upstream releases are picked up automatically:

1. [Renovate](https://renovatebot.com) (`renovate.json`) opens a PR bumping
   `VERSION`, `_service`, and the RPM `Version:` at once.
2. On merge to `main`, `.github/workflows/push-to-obs.yml` detects which
   packages changed and runs `just push` for each. OBS then rebuilds and
   publishes natively. Run manually with a package list:

       gh workflow run push-to-obs.yml -f packages=tools/opencode-image,tools/opencode

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
- Container builds are `Dockerfile` packages built on
  `registry.opensuse.org/opensuse/tumbleweed`.
- RPM packages that wrap a container install a launcher under `/usr/bin`.
