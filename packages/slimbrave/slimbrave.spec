Name:           slimbrave
Version:        2.4.0
Release:        0
Summary:        Debloat and harden Brave Browser using Chromium enterprise policies
License:        GPL-3.0-only
URL:            https://github.com/ChaoticSi1ence/SlimBrave-Neo
Source0:        SlimBrave-Neo-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-base

Requires:       python3-base

%description
SlimBrave applies Chromium enterprise policies to debloat and harden the
Brave browser: 79 policies across 6 presets, managed through a curses TUI
with zero runtime dependencies beyond Python's standard library.

%prep
%autosetup -n SlimBrave-Neo-%{version} -p1

%build

%install
install -Dpm 0755 slimbrave-linux.py %{buildroot}%{_bindir}/slimbrave

%check
python3 -m py_compile slimbrave-linux.py

%files
%license LICENSE
%{_bindir}/slimbrave

%changelog
