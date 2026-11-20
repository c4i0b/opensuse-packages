Name:           nuclei
Version:        3.11.1
Release:        0
Summary:        Fast and customizable vulnerability scanner based on simple YAML based DSL
License:        MIT
URL:            https://github.com/projectdiscovery/nuclei
Source0:        nuclei-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.26

%description
Nuclei is a fast, customizable vulnerability scanner powered by a simple
YAML-based DSL. It supports prototyping, reconnaissance, fuzzing and
scanning across templates for DNS, files, HTTP, TCP and more, with
community-driven template collaboration.

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
# upstream main package lives in cmd/nuclei, not the repo root
go build -mod=vendor -o nuclei ./cmd/nuclei

%install
install -Dpm 0755 nuclei %{buildroot}%{_bindir}/nuclei

%files
%doc README.md
%license LICENSE.md
%{_bindir}/nuclei

%changelog
