Name:           dnscontrol
Version:        5.10.1
Release:        0
Summary:        Infrastructure as code for DNS
License:        MIT
URL:            https://github.com/DNSControl/dnscontrol
Source0:        dnscontrol-%{version}.tar.gz
# go_modules cannot vendor this server-side yet (OBS service runs go 1.26,
# go.mod requires >= 1.27.3), so vendor.tar.zst is generated client-side:
#   go mod vendor && tar --zstd -cf vendor.tar.zst vendor
Source1:        vendor.tar.zst
# rpmuncompress needs zstd for the client-side vendor.tar.zst (Source1)
BuildRequires:  zstd
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.27

%description
DNSControl is an infrastructure-as-code tool for DNS: declare zones and
records in a DSL (or TypeScript), then preview and push changes to any of
100+ DNS providers (Cloudflare, Route53, Google, Azure, and many more),
keeping providers in sync and enabling reviewable, version-controlled DNS.

%prep
%autosetup -a 1
# slowroll's Go lags upstream's go.mod floor (GOTOOLCHAIN=local, offline
# workers); clamp the directive to the buildroot toolchain. Vendored deps
# all declare <= it — a real newer-language-feature need still fails loud
# in `go build` below.
gover="$(go env GOVERSION | cut -c3-)"
# Clamp go floors DOWN to the buildroot toolchain (slowroll lags upstream;
# GOTOOLCHAIN=local, offline workers) — never up, old go.mod module-graph
# semantics must survive. Deps' floors in vendor/modules.txt are checked
# too; a real newer-language-feature need still fails loud in `go build` below.
clamp() {
  awk -v g="$gover" '
    function newer(a, b,  x, y, i) {
      split(a, x, "."); split(b, y, ".")
      for (i = 1; i <= 3; i++) {
        if (x[i] + 0 > y[i] + 0) return 1
        if (x[i] + 0 < y[i] + 0) return 0
      }
      return 0
    }
    match($0, /^(## (explicit; )?)?go [0-9][0-9.]*/) {
      m = substr($0, RSTART, RLENGTH)
      ver = m; sub(/^.*go /, "", ver)
      if (newer(ver, g)) {
        pre = substr(m, 1, length(m) - length(ver))
        $0 = pre g substr($0, RSTART + RLENGTH)
      }
    }
    { print }' "$1" > "$1.tmp" && mv "$1.tmp" "$1"
}
clamp go.mod
clamp vendor/modules.txt

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
