# opensuse-packages

Personal RPM packaging monorepo for [OBS](https://build.opensuse.org),
hosted in the
[`home:caiobruno`](https://build.opensuse.org/project/show/home:caiobruno)
project (openSUSE Tumbleweed). The GitHub repo is the source of truth: a
merge to `main` triggers `push-to-obs`, which syncs the touched packages to
OBS, where they are built.

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
- [Renovate](docs/autoupdate.md) opens version-bump PRs (spec and `_service`
  together), auto-merged after the `validate-bump` gate; Dependabot keeps
  Actions updated.

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
3. `just push packages/<name> "initial package"` — the package only exists
   on OBS after push.
4. Manual bump, if ever needed: `just bump packages/<name> <version>`.
