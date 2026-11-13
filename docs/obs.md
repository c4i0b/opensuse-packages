# OBS integration

OBS (Build Service) is the build system: packages live in the
`home:caiobruno` project and this repo is their source of truth. A package
only exists on OBS after `just push` — a commit alone changes nothing
server-side.

## Source fetching

- `_service` describes how OBS fetches real sources **server-side** (release
  tarballs, ELFs, verification). OBS builds offline, so everything the build
  needs must be reachable through `_service`.
- Never commit archives (`*.tar.gz`, `*.tar.zst`, `*.rpm` are gitignored).
  Local builds fetch sources via the package's `fetch.sh`.
- `.changes` files are merged by OBS into the spec's `%changelog` at build
  time (`just vc <name>` maintains them).

## Push contract

- `just push packages/<name> "msg"` runs the linter first (aborts on FAIL),
  then syncs `packages/<name>/` to `home:caiobruno/<name>` via rsync and
  commits with `osc addremove` + `osc ci`.
- The rsync excludes dev-only files OBS must not see: `fetch.sh`, `bump.sh`,
  `BIN`, archives, `.obsignore`.
- `_project.meta.xml` is the project template (repos, arches);
  `just create-project` applies it.
- `just new-pkg <name>` creates a package from the templates and fills the
  OBS `<title>`/`<description>` from the spec automatically.

## CI workflow roles

The pipeline shape is bump → gate → push to builder → report; workflow
names follow it (file name always equals `name:`):

- `autoupdate` — scheduled version bumps.
- `validate` — the git-side gate (PR): version/asset checks.
- `push-to-obs` — delivery: syncs touched packages to OBS (the builder
  cannot pull). Run duration in the Actions list includes
  concurrency-group queueing: a 5m13s "run" can be a 2s no-op that
  queued behind a fleet push — not slowness.
- `badges` — status-artifact refresh.
- `auto-merge` — Dependabot PR merging, gated on `validate`.

Generic workflow conventions (pinned SHAs, bash-invoked scripts, timeouts,
concurrency, push-retry, GITHUB_TOKEN semantics) live in the
gh-actions-conventions skill.

## Build validation policy

- `just build packages/<name>` is a **pre-flight**: a local rpmbuild gated on
  rpmlint errors (fails on `E:`). OBS is the real validator — a green local
  build does not guarantee a green OBS build.
- After pushing, watch the result with `just results <name>` and read
  failures with `just log <name>`.
- `just status` snapshots the whole project (all packages, both arches);
  `just watch` blocks until every in-flight build finishes and exits
  non-zero if any failed.
- On an OBS failure, follow the `diagnose-obs-failure` skill
  (`skills/diagnose-obs-failure/SKILL.md`). If the same class of failure
  bites twice, encode it in the linter (`opensuse-lint.py`) — fix the class,
  not the instance.
- Do not block waiting for OBS builds. Continue working and check
  `just status` / `just watch` when finishing if builds are pending.
