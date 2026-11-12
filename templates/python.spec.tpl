# Template: pure-Python app from PyPI/source (validated by packages/ytm-player).
# Invariants: openSUSE requires the %python3_* macros, never bare %pyproject_*
# (those expand to every python flavor and fail without the multi-flavor
# machinery). Runtime deps are an explicit Requires: list because
# pythondistdeps drops marker-only deps and openSUSE names can differ from
# PyPI (hyphen/underscore, e.g. python3-dbus_fast). %pyproject_check_import
# is Fedora-only, do not use it.
# Changelog lives in <name>.changes (OBS merges it into %changelog).
Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            __URL__
Source0:        __SOURCE0__
BuildArch:      noarch

BuildRequires:  python3-base
BuildRequires:  python3-pip
BuildRequires:  __BUILD_BACKEND__ # e.g. python3-hatchling, python3-setuptools
BuildRequires:  python-rpm-macros

Requires:       __RUNTIME_DEPS__

%description
__DESCRIPTION__

%prep
%autosetup -n __SRCNAME__-%{version}

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
