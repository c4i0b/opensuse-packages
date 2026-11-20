Name:           superfile
Version:        1.6.0
Release:        0
Summary:        Pretty fancy and modern terminal file manager
License:        MIT
URL:            https://github.com/yorukot/superfile
Source0:        superfile-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.25

%description
A pretty fancy and modern terminal file manager written in Go, with vim-like
keybindings, tabs, panels, themes, and an extensible plugin system.

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
go build -mod=vendor -o spf .

%install
install -Dpm 0755 spf %{buildroot}%{_bindir}/spf

%files
%doc README.md
%license LICENSE
%{_bindir}/spf

%changelog
