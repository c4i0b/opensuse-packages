Name:           bombardier
Version:        2.0.2
Release:        0
Summary:        Fast cross-platform HTTP benchmarking tool
License:        MIT
URL:            https://github.com/codesenberg/bombardier
Source0:        bombardier-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64 aarch64
BuildRequires:  golang(API) >= 1.22

%description
A modern cross-platform HTTP benchmarking tool written in Go, supporting
multiple protocols, connection reuse, rate limiting, and live latency
distributions.

%prep
%autosetup -a 1

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -o bombardier .

%install
install -Dpm 0755 bombardier %{buildroot}%{_bindir}/bombardier

%files
%doc README.md
%license LICENSE
%{_bindir}/bombardier

%changelog
