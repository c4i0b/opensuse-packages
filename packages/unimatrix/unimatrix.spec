# Upstream has no tags/releases: pinned commit snapshot, no autoupdate
%global commit dff519f972103f91384f360f270614184de8aa92

Name:           unimatrix
Version:        0.1.0
Release:        0
Summary:        Simulate the display from "The Matrix" in a terminal
License:        GPL-3.0-or-later
URL:            https://github.com/will8211/unimatrix
Source0:        unimatrix-%{commit}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-base

Requires:       python3-base

%description
Python script to simulate the display from "The Matrix" in a terminal. Uses
half-width katakana unicode characters by default, but can use custom
character sets. Accepts keyboard controls while running.

%prep
%autosetup -n unimatrix-%{commit}

%build

%install
install -Dpm 0755 unimatrix.py %{buildroot}%{_bindir}/unimatrix

%check
python3 -m py_compile unimatrix.py

%files
%license LICENSE
%doc README.md
%{_bindir}/unimatrix

%changelog
