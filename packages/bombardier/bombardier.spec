Name:           bombardier
Version:        2.0.2
Release:        0
Summary:        Fast cross-platform HTTP benchmarking tool
License:        MIT
URL:            https://github.com/codesenberg/bombardier
Source0:        bombardier-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.22

%description
A modern cross-platform HTTP benchmarking tool written in Go, supporting
multiple protocols, connection reuse, rate limiting, and live latency
distributions.

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
go build -mod=vendor -o bombardier .

%install
install -Dpm 0755 bombardier %{buildroot}%{_bindir}/bombardier

%files
%doc README.md
%license LICENSE
%{_bindir}/bombardier

%changelog
