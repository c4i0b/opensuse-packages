Name:           dockle
Version:        0.4.15
Release:        0
Summary:        Container image linter for security, helping build best-practice Docker images
License:        Apache-2.0
URL:            https://github.com/goodwithtech/dockle
Source0:        dockle-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.22
# vendored containers/storage compiles its btrfs driver (cgo)
BuildRequires:  libbtrfs-devel

%description
Dockle scans container images for security issues and Dockerfile best
practices, including CIS Benchmarks checkpoints. It helps build the Best
Practice Docker Image and is suitable for CI pipelines.

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
go build -mod=vendor -o dockle ./cmd/dockle

%install
install -Dpm 0755 dockle %{buildroot}%{_bindir}/dockle

%files
%doc README.md CHECKPOINT.md
%license LICENSE
%{_bindir}/dockle

%changelog
