Name:           oxker
Version:        0.13.4
Release:        0
Summary:        TUI to view and control docker containers
License:        MIT
URL:            https://github.com/mrjackwills/oxker
Source0:        oxker-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging

%description
Oxker is a simple TUI for viewing and controlling docker containers, built
with ratatui: sort, restart, stop, and inspect containers with keyboard
shortcuts.

%prep
%autosetup -p1 -a1

%build
%{cargo_build}

%install
install -Dpm 0755 target/release/oxker %{buildroot}%{_bindir}/oxker

%files
%license LICENSE
%doc README.md
%{_bindir}/oxker

%changelog
