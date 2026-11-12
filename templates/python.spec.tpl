# Template: pure-Python app built from source (validated by packages/ytm-player).
#
# Invariants (docs/packaging/python.md):
# - Always %python3_* macros, never bare %pyproject_wheel/%pyproject_install:
#   without the multi-flavor machinery (%global flavor @BUILD_FLAVOR@ +
#   %python_subpackages + OBS flavors) the bare macros expand to EVERY python
#   flavor and the build fails (e.g. python314 not installed).
# - %pyproject_check_import is Fedora-only (undefined on openSUSE) — do not use.
# - pythondistdeps drops dependencies declared with environment markers
#   (e.g. "dbus-fast>=5; sys_platform == 'linux'", "tomli; python_version < '3.11'").
#   Enumerate runtime deps from pyproject.toml and add an explicit Requires:
#   for every one that must hold on Tumbleweed.
# - PyPI -> openSUSE package names differ (hyphen vs underscore:
#   python3-dbus_fast, python3-SecretStorage, python3-Pillow). Verify the real
#   binary name with `zypper se` / OBS published-binary search before adding
#   a Requires:; Tumbleweed ships flavored python313-* binaries that provide
#   the unflavored python3-* names.
# - Changelog lives in <name>.changes (OBS merges it into %changelog):
#
#   -------------------------------------------------------------------
#   __DATE__ - __PACKAGER__
#
#   - Initial package of __NAME__ __VERSION__.
#
# _service fetches the sdist server-side (never commit archives). Shape for a
# GitHub release sdist (adjust version in path and filename):
#
#   <services>
#     <service name="download_url">
#       <param name="protocol">https</param>
#       <param name="host">github.com</param>
#       <param name="path">/__OWNER__/__NAME__/releases/download/v__VERSION__/__SRCNAME__-__VERSION__.tar.gz</param>
#       <param name="filename">__SRCNAME__-__VERSION__.tar.gz</param>
#     </service>
#   </services>
Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            __URL__
Source0:        __SRCNAME__-__VERSION__.tar.gz
BuildArch:      noarch

# BuildRequires set proven on OBS (Tumbleweed): __BUILD_BACKEND__ is the
# [build-system] requires of pyproject.toml — python3-hatchling for
# hatchling.build, python3-setuptools + python3-wheel for setuptools.
BuildRequires:  python3-base
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  __BUILD_BACKEND__
BuildRequires:  python3-rpm-macros

# One Requires: per runtime dep in [project] dependencies (see invariants
# above: markers get dropped, names may differ from PyPI). Non-Python
# runtime tools go here too (e.g. mpv for python-mpv).
Requires:       __RUNTIME_DEPS__

%description
__DESCRIPTION__

%prep
%autosetup -n __SRCNAME__-__VERSION__

%build
%python3_pyproject_wheel

%install
%python3_pyproject_install

%files
%license LICENSE
%{_bindir}/__BIN__
%{python3_sitelib}/__SRCNAME__/
%{python3_sitelib}/__SRCNAME__-*.dist-info/

%changelog
