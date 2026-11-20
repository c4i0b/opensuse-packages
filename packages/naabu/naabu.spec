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
go build -mod=vendor -o naabu ./cmd/naabu

%install
install -Dpm 0755 naabu %{buildroot}%{_bindir}/naabu

%files
%doc README.md
%license LICENSE.md
%{_bindir}/naabu

%changelog
