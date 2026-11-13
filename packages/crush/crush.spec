Name:           crush
Version:        0.101.0
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
ExclusiveArch:  x86_64 aarch64
BuildRequires:  golang(API) >= 1.27

%description
A powerful terminal-based AI assistant for developers, providing intelligent
coding assistance directly in your terminal. Supports a wide range of LLM
providers, LSP integration for context, MCP servers and session management.

%prep
%autosetup -a 1

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
