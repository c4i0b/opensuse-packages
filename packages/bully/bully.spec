Name:           bully
Version:        1.2
Release:        0
Summary:        WPS brute-force attack tool
License:        GPL-3.0-or-later
URL:            https://github.com/aanarchyy/bully
Source0:        bully-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  libpcap-devel

%description
Bully is an implementation of the WPS brute-force attack, written in
C. It references the original Reaver code, but is a standalone project.
Given an AP's pin, it can retrieve the WPA/WPA2 key — it is also used
by wifite for WPS attacks and to fetch the PSK once the PIN is known.

%prep
%autosetup

%build
# Env (not command-line) CFLAGS/LDFLAGS so the Makefile's += keeps the
# internal crypto defines and -lpcap on top of the RPM flags
export CFLAGS="%{build_cflags}"
export LDFLAGS="%{build_ldflags}"
%make_build -C src

%install
# Cleanup helper from Kali's packaging: removes WPS session files
# (--restore/--p2c) left by bully runs.
cat > bully-cleanup << 'EOF'
#!/bin/sh
rm -f ./bully.*.run ./bully.*.pin ./bully.*.p2c 2>/dev/null || true
EOF
install -Dpm755 bully-cleanup %{buildroot}%{_bindir}/bully-cleanup

%make_install -C src prefix=%{_prefix} bindir=%{_bindir}

%files
%license LICENSE.md
%{_bindir}/bully
%{_bindir}/bully-cleanup

%changelog
