Name:           masscan
Version:        1.3.2
Release:        0
Summary:        Fast TCP port scanner
License:        AGPL-3.0-only
URL:            https://github.com/robertdavidgraham/masscan
Source0:        masscan-%{version}.tar.gz
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  libpcap-devel

%description
Masscan is the fastest TCP port scanner: it can scan the entire Internet
in under 6 minutes, transmitting 10 million packets per second, by using
its own custom TCP/IP stack built on libpcap/raw sockets. It produces
results similar to nmap, the legendary port scanner, but unlike nmap it
supports only asynchronous (stateless) scanning.

%prep
%autosetup

%build
# The Makefile hard-assigns CFLAGS (dropping -Wall -O2), so the distro
# flags must come in as a command-line override; LDFLAGS is honored as-is.
%make_build CFLAGS="%{optflags}" LDFLAGS="%{?build_ldflags}"

%install
%make_install PREFIX=%{_prefix} BINDIR=%{_bindir}
install -Dpm 0644 doc/masscan.8 %{buildroot}%{_mandir}/man8/masscan.8
install -Dpm 0644 data/exclude.conf %{buildroot}%{_datadir}/masscan/exclude.conf

%files
%doc README.md
%license LICENSE
%{_bindir}/masscan
%{_mandir}/man8/masscan.8%{?ext_man}
%{_datadir}/masscan/exclude.conf

%changelog
