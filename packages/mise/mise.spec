Name:           mise
Version:        2026.10.23
Release:        0
Summary:        Polyglot runtime and tool version manager (modern asdf)
License:        MIT
URL:            https://github.com/jdx/mise
Source0:        mise-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging
# aws-lc-sys (vendored) builds via cmake
BuildRequires:  cmake
BuildRequires:  gcc-c++
# default features pull native-tls (reqwest/gix/rattler)
BuildRequires:  openssl-devel

%description
Mise manages runtime and tool versions per project, directory or globally:
node, python, go, terraform and hundreds of other tools, plus environment
variables and tasks. A fast single-binary replacement for asdf, nvm, pyenv
and friends.

%prep
%autosetup -p1 -a1

%build
%{cargo_build}

%install
install -Dpm 0755 target/release/mise %{buildroot}%{_bindir}/mise
install -Dpm 0644 man/man1/mise.1 %{buildroot}%{_mandir}/man1/mise.1
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions %{buildroot}%{_datadir}/zsh/site-functions %{buildroot}%{_datadir}/fish/vendor_completions.d
target/release/mise completion bash > %{buildroot}%{_datadir}/bash-completion/completions/mise
target/release/mise completion zsh  > %{buildroot}%{_datadir}/zsh/site-functions/_mise
target/release/mise completion fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/mise.fish

%check
target/release/mise --version

%files
%license LICENSE
%doc README.md
%{_bindir}/mise
%{_mandir}/man1/mise.1%{?ext_man}
%{_datadir}/bash-completion/completions/mise
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_mise
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/mise.fish

%changelog
