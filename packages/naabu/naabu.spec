Name:           naabu
Version:        2.7.0
Release:        0
Summary:        Fast port scanner written in Go
License:        MIT
URL:            https://github.com/projectdiscovery/naabu
Source0:        naabu-%{version}.tar.gz
Source1:        vendor.tar.gz
# %{go_arches} is NOT defined in Tumbleweed's prjconf anymore: an empty
# expansion makes OBS exclude every arch. List the arches explicitly.
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.26
BuildRequires:  libpcap-devel

%description
naabu is a port scanning tool written in Go that allows you to enumerate
open ports on hosts in a fast and reliable manner. It performs SYN scans
via raw sockets (which require root privileges) and CONNECT scans
unprivileged, and is designed to be combined with other ProjectDiscovery
tools in pipelines.

%prep
%autosetup -a 1
# slowroll's Go lags upstream's go.mod floor (GOTOOLCHAIN=local, offline
# workers); clamp the directive to the buildroot toolchain. A real
# newer-language-feature need still fails loud in `go build` below.
gover="$(go env GOVERSION | cut -c3-)"
sed -i "s/^go .*/go $gover/" go.mod
# deps' floors in vendor/modules.txt are checked too; clamp them as well
sed -i -E "s/^(## (explicit; )?)go .*/\1go $gover/" vendor/modules.txt

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -o naabu ./cmd/naabu

%install
install -Dpm 0755 naabu %{buildroot}%{_bindir}/naabu

%files
%doc README.md
%license LICENSE.md
%{_bindir}/naabu

%changelog
