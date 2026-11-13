%global cargo_install_lib false
# vendored crate sources trip brp-mangle-shebangs during debugsource collection
%global debug_package %{nil}

Name:           topmatic
Version:        1.2.0
Release:        0
Summary:        User-level scheduled updates powered by topgrade
License:        MIT
URL:            https://github.com/c4i0b/topmatic
Source0:        topmatic-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging

Requires:       topgrade

%description
Topmatic turns Topgrade into scheduled systemd jobs managed from a TUI,
updating user-level tools (flatpaks, cargo installs, npm globals, pipx apps)
without sudo, daemons or cron.

%prep
%autosetup -p1 -a1

%build
%{cargo_build}

%install
install -Dpm 0755 target/release/topmatic %{buildroot}%{_bindir}/topmatic

%check
target/release/topmatic --version

%files
%license LICENSE
%doc README.md
%{_bindir}/topmatic

%changelog
