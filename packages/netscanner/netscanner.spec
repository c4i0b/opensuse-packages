Name:           netscanner
Version:        0.6.43
Release:        0
Summary:        Terminal network scanner and diagnostic tool with modern TUI
License:        MIT
URL:            https://github.com/Chleba/netscanner
Source0:        netscanner-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging
BuildRequires:  openssl-devel

%description
Network scanner and diagnostic tool with a ratatui TUI: lists hardware
interfaces, scans WiFi networks with signal charts, pings IPv4 CIDRs with
hostname and OUI/MAC resolution, dumps TCP/UDP/ICMP/ARP packets, scans open
TCP ports, and exports results to CSV. Requires root at runtime.

%prep
%autosetup -p1 -a1

%build
%{cargo_build}

%install
install -Dpm 0755 target/release/netscanner %{buildroot}%{_bindir}/netscanner
install -Dpm 0644 debian/netscanner.manpage %{buildroot}%{_mandir}/man1/netscanner.1

%files
%license LICENSE
%doc README.md
%{_bindir}/netscanner
%{_mandir}/man1/netscanner.1%{?ext_man}

%changelog
