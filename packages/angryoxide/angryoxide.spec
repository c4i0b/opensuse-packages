Name:           angryoxide
Version:        0.9.2
Release:        0
Summary:        802.11 attack tool producing hashcat-ready hashlines
License:        GPL-3.0-only
URL:            https://github.com/Ragnt/AngryOxide
Source0:        angryoxide-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging
Requires:       hashcat

# release profile strips the binary (Cargo.toml): no debugsource
%global debug_package %{nil}

%description
Single-interface 802.11 survey and attack tool with automated attacks that
result in valid hashcat hashlines. Heavily inspired by hcxdumptool.

%prep
%autosetup -p1 -a1

%build
%{cargo_build}

%install
install -Dpm 0755 target/release/angryoxide %{buildroot}%{_bindir}/angryoxide
install -Dpm 0644 completions/bash_angryoxide_completions %{buildroot}%{_datadir}/bash-completion/completions/angryoxide
install -Dpm 0644 completions/zsh_angryoxide_completions %{buildroot}%{_datadir}/zsh/site-functions/_angryoxide

%files
%license LICENSE
%doc README.md
%{_bindir}/angryoxide
%{_datadir}/bash-completion/completions/angryoxide
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_angryoxide

%changelog
