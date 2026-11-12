# Packaging quirks: Python

## Macros: `%python3_*`, never bare `%pyproject_*`

For a single default-flavor noarch app, use
`%python3_pyproject_wheel`/`%python3_pyproject_install`. The bare
`%pyproject_wheel`/`%pyproject_install` require the multi-flavor machinery
(`%global flavor @BUILD_FLAVOR@` + `%python_subpackages` + flavors
configured on OBS); without it they expand to EVERY python flavor and the
build fails (e.g. python314 not installed). The lint flags this as
`pyproject-flavor`.

`%pyproject_check_import` is Fedora-only (undefined on openSUSE) — do not
use it.

## Marker-only dependencies get dropped

pythondistdeps drops dependencies declared with environment markers (e.g.
`dbus-fast>=5; sys_platform == 'linux'`). Add an explicit `Requires:` for
them.

## PyPI → openSUSE name differences

openSUSE package names can differ from PyPI names (hyphen → underscore:
`python3-dbus_fast`). Verify the binary package name with
`zypper se`/`zypper info` before adding a `Requires:`.
