Name:           ytm-player
Version:        2.0.0
Release:        0
Summary:        YouTube Music TUI client with vim keybindings and synced lyrics
License:        MIT
URL:            https://github.com/peternaame-boop/ytm-player
Source0:        ytm_player-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  %{python_module hatchling}
BuildRequires:  python-rpm-macros
Requires:       python3-textual
Requires:       python3-ytmusicapi
Requires:       yt-dlp
Requires:       python3-python-mpv
Requires:       python3-aiosqlite
Requires:       python3-click
Requires:       python3-packaging
Requires:       python3-Pillow
Requires:       mpv

%description
A full-featured YouTube Music TUI client for the terminal.

%prep
%autosetup -n ytm_player-%{version}

%build
%pyproject_wheel

%install
%pyproject_install
%python_compileall

%files
%license LICENSE
%{_bindir}/ytm
%{python_sitelib}/ytm_player/
%{python_sitelib}/ytm_player-*.dist-info/

%changelog
