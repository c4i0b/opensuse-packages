Name:           nexttrace
Version:        1.7.6
Release:        0
Summary:        Open source visual route tracking CLI tool
License:        GPL-3.0-only
URL:            https://github.com/nxtrace/NTrace-core
Source0:        nexttrace-%{version}.tar.gz
# go_modules cannot vendor this server-side yet (OBS service runs go 1.26,
# go.mod requires >= 1.27.3), so vendor.tar.zst is generated client-side:
#   go mod vendor && tar --zstd -cf vendor.tar.zst vendor
Source1:        vendor.tar.zst
# rpmuncompress needs zstd for the client-side vendor.tar.zst (Source1)
BuildRequires:  zstd
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.27

%description
NextTrace is an open source visual route tracking CLI tool written in Go,
with map visualization, GeoIP enrichment, and both ICMP TCP and UDP tracing
modes.

%prep
%autosetup -a 1
# slowroll's Go lags upstream's go.mod floor (GOTOOLCHAIN=local, offline
# workers); clamp the directive to the buildroot toolchain. Vendored deps
# all declare <= it — a real newer-language-feature need still fails loud
# in `go build` below.
sed -i "s/^go .*/go $(go env GOVERSION | cut -c3-)/" go.mod

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -o nexttrace .

%install
install -Dpm 0755 nexttrace %{buildroot}%{_bindir}/nexttrace

%files
%doc README.md
%license LICENSE
%{_bindir}/nexttrace

%changelog
