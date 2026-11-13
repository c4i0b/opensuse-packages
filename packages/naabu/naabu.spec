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
ExclusiveArch:  x86_64 aarch64
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
