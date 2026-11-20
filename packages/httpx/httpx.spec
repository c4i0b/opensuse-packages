Name:           httpx
Version:        1.12.0
Release:        0
Summary:        Fast and multi-purpose HTTP toolkit
License:        MIT
URL:            https://github.com/projectdiscovery/httpx
Source0:        httpx-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.26

%description
httpx is a fast and multi-purpose HTTP toolkit that allows running multiple
probes using the retryablehttp library. It returns the status code, response
time, title, tech stack, and other information for a list of URLs, with
support for probing over HTTP(S), following redirects, and customizable
output formats.

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
go build -mod=vendor -o httpx ./cmd/httpx

%install
install -Dpm 0755 httpx %{buildroot}%{_bindir}/httpx

%files
%doc README.md
%license LICENSE.md
%{_bindir}/httpx

%changelog
