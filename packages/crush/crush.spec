Name:           crush
Version:        0.102.0
Release:        0
Summary:        Agentic coding assistant for the terminal
License:        FSL-1.1-MIT
URL:            https://github.com/charmbracelet/crush
Source0:        crush-%{version}.tar.gz
# go_modules cannot vendor this server-side (OBS service host runs go 1.26,
# go.mod requires 1.27.3), so vendor.tar.zst is generated client-side:
#   go mod vendor && tar --zstd -cf vendor.tar.zst vendor
Source1:        vendor.tar.zst
# rpmuncompress needs zstd for the client-side vendor.tar.zst (Source1)
BuildRequires:  zstd
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.27

%description
A powerful terminal-based AI assistant for developers, providing intelligent
coding assistance directly in your terminal. Supports a wide range of LLM
providers, LSP integration for context, MCP servers and session management.

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
# OBS build workers are offline: never try to fetch a newer toolchain
export GOTOOLCHAIN=local
go build -mod=vendor -ldflags "-X github.com/charmbracelet/crush/internal/version.Version=%{version}" -o crush .

%install
install -Dpm 0755 crush %{buildroot}%{_bindir}/crush
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions %{buildroot}%{_datadir}/zsh/site-functions %{buildroot}%{_datadir}/fish/vendor_completions.d
./crush completion bash > %{buildroot}%{_datadir}/bash-completion/completions/crush
./crush completion zsh  > %{buildroot}%{_datadir}/zsh/site-functions/_crush
./crush completion fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/crush.fish
./crush man > crush.1
install -Dpm 0644 crush.1 %{buildroot}%{_mandir}/man1/crush.1

%files
%doc README.md
%license LICENSE.md
%{_bindir}/crush
%{_datadir}/bash-completion/completions/crush
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_crush
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/crush.fish
%{_mandir}/man1/crush.1%{?ext_man}

%changelog
