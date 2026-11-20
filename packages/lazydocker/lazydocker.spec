Name:           lazydocker
Version:        0.25.2
Release:        0
Summary:        Simple terminal UI for docker and docker-compose
License:        MIT
URL:            https://github.com/jesseduffield/lazydocker
Source0:        lazydocker-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.22

%description
A simple terminal UI for both docker and docker-compose, written in Go with
the gocui library: inspect and manage containers, images, volumes, and
services without leaving the keyboard.

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
go build -mod=vendor -o lazydocker .

%install
install -Dpm 0755 lazydocker %{buildroot}%{_bindir}/lazydocker

%files
%doc README.md
%license LICENSE
%{_bindir}/lazydocker

%changelog
