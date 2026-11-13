Name:           atac
Version:        0.24.0
Release:        0
Summary:        Simple yet powerful API client TUI (terminal Postman)
License:        MIT
URL:            https://github.com/julien-cpsn/ATAC
# Upstream repo name is ATAC, so tar_scm produces ATAC-<version>.tar.zst
Source0:        ATAC-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging

%description
ATAC (Argument-Tree API Client) is a feature-rich API client that lives in
the terminal: collections, environments, keybind-driven requests, syntax
highlighted responses and curl import — a Postman/Insomnia experience
without leaving the keyboard.

%prep
%autosetup -n ATAC-%{version} -p1 -a1

%build
%{cargo_build}

%install
install -Dpm 0755 target/release/atac %{buildroot}%{_bindir}/atac
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions %{buildroot}%{_datadir}/zsh/site-functions %{buildroot}%{_datadir}/fish/vendor_completions.d
# 'atac completions <shell> <dir>' writes the file into <dir>
compdir="$(mktemp -d)"
target/release/atac completions bash "$compdir"
install -Dpm 0644 "$compdir"/* %{buildroot}%{_datadir}/bash-completion/completions/atac
rm -f "$compdir"/*
target/release/atac completions zsh "$compdir"
install -Dpm 0644 "$compdir"/* %{buildroot}%{_datadir}/zsh/site-functions/_atac
rm -f "$compdir"/*
target/release/atac completions fish "$compdir"
install -Dpm 0644 "$compdir"/* %{buildroot}%{_datadir}/fish/vendor_completions.d/atac.fish

%files
%license LICENSE
%doc README.md
%{_bindir}/atac
%{_datadir}/bash-completion/completions/atac
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_atac
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/atac.fish

%changelog
