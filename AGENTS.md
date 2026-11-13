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
  (`opensuse-lint.py`): `bun` and Electron bundles must disable strip,
  `go`/`rust` prebuilts are strip-safe and must not.
- Never add a spec rule without its red: encode the failure class in the
  linter or a template, not just the instance.
- Specs and templates are written for the next bump, not the current
  build: one definition per repeated constant, derive what upstream
  controls, drift fails loud — see "Fix for the long term" in
  [conventions](docs/conventions.md).
- On an OBS failure, follow `skills/diagnose-obs-failure/SKILL.md`; if the
  same class of failure bites twice, encode it in the linter.
- Recipe logic lives in `tools/*.sh`; the justfile stays a thin dispatcher.
- English only; comments only for non-obvious workarounds.

## Reference

- OBS contract, `_service` fetch, push and build policy:
  [docs/obs.md](docs/obs.md)
- Environment, container, credentials: [docs/environment.md](docs/environment.md)
- Automatic updates (autoupdate bot, validate, Dependabot):
  [docs/autoupdate.md](docs/autoupdate.md)
- Conventions (build models, layout, versioning, hygiene):
  [docs/conventions.md](docs/conventions.md)
- Packaging quirks: [general](docs/packaging/general.md) ·
  [python](docs/packaging/python.md) ·
  [rust](docs/packaging/rust.md)
- Failure diagnosis: [skills/diagnose-obs-failure/SKILL.md](skills/diagnose-obs-failure/SKILL.md)
- Package templates: [templates/](templates/) (`*.spec.tpl`)
- Task tracking (optional): when the `bd` command is available on the host,
  organize multi-step work with it; when it is not, carry on without it.
  Details: [docs/workflow.md](docs/workflow.md)
