Name:           dnscontrol
Version:        5.8.2
Release:        0
Summary:        Infrastructure as code for DNS
License:        MIT
URL:            https://github.com/DNSControl/dnscontrol
Source0:        dnscontrol-%{version}.tar.gz
# go_modules cannot vendor this server-side yet (OBS service runs go 1.26,
# go.mod requires >= 1.27.3), so vendor.tar.zst is generated client-side:
#   go mod vendor && tar --zstd -cf vendor.tar.zst vendor
Source1:        vendor.tar.zst
ExclusiveArch:  x86_64 aarch64
BuildRequires:  golang(API) >= 1.27

%description
DNSControl is an infrastructure-as-code tool for DNS: declare zones and
records in a DSL (or TypeScript), then preview and push changes to any of
100+ DNS providers (Cloudflare, Route53, Google, Azure, and many more),
keeping providers in sync and enabling reviewable, version-controlled DNS.

%prep
%autosetup -a 1

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -o dnscontrol .

%install
install -Dpm 0755 dnscontrol %{buildroot}%{_bindir}/dnscontrol

%files
%doc README.md
%license LICENSE
%{_bindir}/dnscontrol

%changelog
