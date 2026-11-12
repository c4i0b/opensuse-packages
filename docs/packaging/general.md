# Packaging quirks: general

Hard-won lessons for RPM specs in this repo, not specific to Python.

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
