# Packaging quirks: general

Hard-won lessons for RPM specs in this repo, not specific to Python.

## Offline dependency models (OBS workers have no network)

OBS build workers are offline, and so are Fedora's official Koji builders
— only COPR workers get external network by default. A fedora-packages
spec that runs `npm install` or `pip`/`uv pip install` at build time
builds there purely on COPR's network (a COPR-only shortcut, never
Koji-viable), so a port must swap in an offline model. For npm apps,
prefer in order:

1. a release tarball that already ships a prebuilt `dist/` — no
   build-time npm at all (the cockpit route in Fedora; our
   `devcontainers-cli`);
2. the npm-bundle model below — same class as Fedora's accepted practice
   of committing a zipped `node_modules` as a lookaside Source, and the
   OBS-canonical one (the cockpit family in openSUSE:Factory uses the
   same `local-npm-registry` + client-side vendoring via
   `obs-service-node_modules`; their `npm install --package-lock-only` →
   `osc service manualrun` update flow is our `fetch.sh --vendor`).

The legacy per-module model (`%nodejs_symlink_deps` from the old Node.js
packaging guidelines) is effectively dead for applications.

Both models below vendor the closure CLIENT-side; OBS only ever installs
from local artifacts. Templates carry the full invariants:
`templates/npm-bundle.spec.tpl`, `templates/python-venv-wheels.spec.tpl`;
the linter FAILs any build-time `npm install` without `local-npm-registry`
and any `pip`/`uv pip install` without `--no-index` (check `offline-build`).

- **npm-bundle** (openclaw, rea-agents): Source0 = registry.npmjs.org
  tarball (via `_service download_url`); `package-lock.json` and
  `node_modules.spec.inc` committed (Source10/Source11, %include'd).
  spec.inc lists every dependency tarball as a Source10000+ **registry
  URL with a flat rename** (`url#/<flat-name>.tgz` — the cockpit model in
  openSUSE:Factory) that the `download_files` service fetches
  server-side: only the lock and spec.inc are committed or pushed, never
  the tarballs. At build time `BuildRequires: local-npm-registry` serves
  the fetched tarballs (flat in `%{_sourcedir}`) to `npm install`;
  `node_modules.obscpio` is the local-only cache the pre-flight build
  expands. Gotchas encoded in the template: bundled deps
  (`"inBundle": true`) have no registry URL — npm-pack them from the
  tarball itself and let them ride the obs-rsync P filter; a shipped `npm-shrinkwrap.json` doubles as the lockfile and must
  be removed in %prep (its resolved URLs bypass the local registry); the
  npm CLI needs `BuildRequires: npm-default` (nodejs24 alone has none) and
  the interpreter is `/usr/bin/node24`. Local pre-flight builds expand the
  cpio flat into the package dir via `fetch.sh` (never committed).
- **bundled venv** (hermes-agent): the closure comes from upstream's lock
  (uv.lock) via `uv export --frozen`, downloaded client-side into
  `wheels.tar.zst` (pushed via the `--filter='P *.tar.zst'` protection, like
  rust vendors); `requirements.txt` committed as Source2. OBS-side:
  `BuildRequires: python31X-uv` (single-spec: binary `python314-uv`, NOT
  `python-uv`) + `python314`, `uv venv` under `%{_libdir}`, installs with
  `--no-index --find-links --no-deps`, the project itself via
  `--no-build-isolation` with setuptools/wheel preinstalled from the vendor
  set. Not Fedora-canonical (per-module packaging; a bundled venv there
  needs a Packaging Committee exception) — acceptable for a home OBS
  project, and the only offline path: no `obs-service` for PyPI exists
  (Factory ships one for cargo/go_modules/node_modules/... but nothing
  PyPI). The `==` pins shared by spec and `fetch.sh` are kept in sync by
  the `vendor-pin-drift` lint check.

## Prebuilt binaries and strip

- **Bun prebuilts must disable strip**: `%global __os_install_post %{nil}`.
  Without it, OBS brp strips the ELF and the binary falls back to the Bun
  CLI (Bun single-file executables append their payload after the ELF
  section that strip removes).
- **Electron bundles must disable strip too** (`%define debug_package
  %{nil}` + `%global __strip /bin/true`): stripping corrupts the embedded
  snapshot (fedora-packages red — this corrects the earlier "electron is
  strip-safe" claim).
- Go and Rust prebuilts are **strip-safe** and must NOT add the macro.

## PREBUILT_ORIGIN registry

Register every prebuilt package in `PREBUILT_ORIGIN` (`opensuse-lint.py`):
classify it as `"bun"` (single-file exe, payload appended, needs
`__os_install_post %{nil}`; the lint FAILs without it) or
`"go"`/`"rust"`/`"electron"` (strip-safe). Unknown prebuilts produce a WARN
until classified.

## rpmlintrc filters

- Per-package `<name>.rpmlintrc` with `addFilter(...)` is honored by OBS
  (loaded from SOURCES) and locally by `just build`.
- `tools/rpmlintrc` mirrors OBS's global filter set (`dist/obs-rpmlintrc`)
  to silence local-only noise. The three mirrors and why:
  - `no-changelogname-tag` — OBS merges `<pkg>.changes` into `%changelog`.
  - `python-bytecode-inconsistent-mtime` — OBS normalizes bytecode mtimes
    at install.
  - `files-duplicate` — `.pyc` + `.opt-1.pyc` from
    `%python3_pyproject_install`; the regex covers `files-duplicated-waste`
    too.
- Because the mirror only matches some packages, rpmlint reports its
  patterns as `E: unused-rpmlintrc-filter` locally on unrelated builds —
  the `just build` gate ignores those, but STILL fails on unused filters
  from per-package rpmlintrc. Those are pushed to OBS, where stale filters
  show as `E: unused-rpmlintrc-filter` on the src package — non-fatal, but
  noisy. Only add filters that match on OBS, and prune stale ones.
- Prefer rewording the spec `Summary`/`%description` over a spelling
  filter.

## Directory ownership

Icon and completion directories need explicit `%dir` ownership: OBS
check-filelist FAILs if dirs under `%{_datadir}/icons/hicolor/*/apps/`,
`%{_datadir}/zsh/` or `%{_datadir}/fish/` are not owned by the package.
`just lint` catches this before pushing.

## ExclusiveArch

Archful `-bin` packages must declare `ExclusiveArch` matching the
architectures upstream actually publishes (missing it makes OBS fail the
excluded arches instead of skipping them).
