# AGENTS.md — opensuse-packages

RPM spec monorepo built server-side by OBS (openSUSE Tumbleweed, project
`home:caiobruno`). GitHub is the source of truth: a merge to `main` syncs the
touched packages to OBS via CI, and OBS builds them — there is no local
building outside the pre-flight. Keep this file lean: behavioral rules an
agent must follow every session. Detailed policies live in `docs/`
([index](docs/README.md)); when adding rules here, prefer extending a linked
doc over growing this file.

## Environment

- The host provides only `just` + `podman`; every recipe runs in the
  ephemeral `tooling` container. Run `just image` once (it also wires the
  git hooks); `just shell` for interactive work.
  Full details: [docs/environment.md](docs/environment.md).

## Golden rules

- OBS is the build validator: `just build` is a pre-flight rpmlint-gated
  rpmbuild, never a substitute. Push, then watch `just results`/`just log`.
- Never commit archives — OBS fetches sources via `_service`.
- Register every prebuilt package's origin in `PREBUILT_ORIGIN`
  (`opensuse-lint.py`): `bun` needs `%global __os_install_post %{nil}`,
  `go`/`rust`/`electron` are strip-safe and must not add it.
- Never add a spec rule without its red: encode the failure class in the
  linter or a template, not just the instance.
- On an OBS failure, follow `skills/diagnose-obs-failure/SKILL.md`; if the
  same class of failure bites twice, encode it in the linter.
- Recipe logic lives in `tools/*.sh`; the justfile stays a thin dispatcher.
- English only; comments only for non-obvious workarounds.

## Reference

- OBS contract, `_service` fetch, push and build policy:
  [docs/obs.md](docs/obs.md)
- Environment, container, credentials: [docs/environment.md](docs/environment.md)
- Automatic updates (Renovate, validate-bump, Dependabot):
  [docs/autoupdate.md](docs/autoupdate.md)
- Conventions (`-bin`-only policy, layout, versioning, hygiene):
  [docs/conventions.md](docs/conventions.md)
- Packaging quirks: [general](docs/packaging/general.md) ·
  [python](docs/packaging/python.md)
- Failure diagnosis: [skills/diagnose-obs-failure/SKILL.md](skills/diagnose-obs-failure/SKILL.md)
- Package templates: [templates/](templates/) (`*.spec.tpl`)
- Planned work: [BACKLOG.md](BACKLOG.md)
- Task tracking (optional): when the `bd` command is available on the host,
  organize multi-step work with it; when it is not, carry on without it.
  Details: [docs/workflow.md](docs/workflow.md)
