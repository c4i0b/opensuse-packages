Name:           nexttrace
Version:        1.7.6
Release:        0
Summary:        Open source visual route tracking CLI tool
License:        GPL-3.0-only
URL:            https://github.com/nxtrace/NTrace-core
Source0:        nexttrace-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64 aarch64
BuildRequires:  golang(API) >= 1.27

%description
NextTrace is an open source visual route tracking CLI tool written in Go,
with map visualization, GeoIP enrichment, and both ICMP TCP and UDP tracing
modes.

%prep
%autosetup -a 1

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
