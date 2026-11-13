Name:           whosthere
Version:        0.9.0
Release:        0
Summary:        LAN discovery tool with an interactive TUI
License:        Apache-2.0
URL:            https://github.com/ramonvermeulen/whosthere
Source0:        whosthere-%{version}.tar.gz
# vendor.tar.zst is generated client-side (see _service): the server-side
# go_modules service runs go 1.26 with GOTOOLCHAIN=local and cannot vendor
# a module whose go.mod directive is newer.
Source1:        vendor.tar.zst
ExclusiveArch:  x86_64 aarch64
BuildRequires:  golang(API) >= 1.27

%description
Local Area Network discovery tool with an interactive TUI, written in Go.
Whosthere performs unprivileged concurrent scans using mDNS and SSDP, sweeps
the local subnet to populate the ARP cache, and enriches discovered devices
with OUI manufacturer lookups. It can also scan TCP ports on found hosts, run
as a daemon with an HTTP API, and export scan results as JSON.

%prep
%autosetup -a 1

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -ldflags "-X main.versionStr=%{version}" -o whosthere .

%install
install -Dpm 0755 whosthere %{buildroot}%{_bindir}/whosthere

%files
%doc README.md
%license LICENSE
%{_bindir}/whosthere

%changelog
