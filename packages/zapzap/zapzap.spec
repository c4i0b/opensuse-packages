# Ported from the fedora-packages spec (github.com/c4i0b/fedora-packages),
# behavior kept; openSUSE macros per templates/python.spec.tpl.
# NOTE: openSUSE:Factory carries zapzap 6.4.x — this package tracks current
# upstream (7.x) ahead of the official one.
Name:           zapzap
Version:        7.5.1
Release:        0
Summary:        WhatsApp desktop application written in PyQt6 + QtWebEngine
License:        GPL-3.0-or-later
URL:            https://github.com/rafatosta/zapzap
Source0:        zapzap-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-base
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  python3-setuptools
BuildRequires:  python3-rpm-macros
BuildRequires:  desktop-file-utils

# pyproject.toml dependencies (PyQt6, PyQt6-WebEngine) under their
# Tumbleweed binary names; sip rides in via python3-PyQt6
Requires:       python3-PyQt6
Requires:       python3-PyQt6-WebEngine

%description
ZapZap is an unofficial WhatsApp desktop client that wraps WhatsApp Web in a
QtWebEngine window, adding tray integration, spell checking, themes and
per-window settings.

%prep
%autosetup -n zapzap-%{version}

%build
%python3_pyproject_wheel

%install
%python3_pyproject_install

install -Dpm644 share/applications/com.rtosta.zapzap.desktop \
  %{buildroot}%{_datadir}/applications/com.rtosta.zapzap.desktop
install -Dpm644 share/icons/com.rtosta.zapzap.svg \
  %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg
install -Dpm644 share/metainfo/com.rtosta.zapzap.appdata.xml \
  %{buildroot}%{_datadir}/metainfo/com.rtosta.zapzap.appdata.xml

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/com.rtosta.zapzap.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/zapzap
%{python3_sitelib}/zapzap/
%{python3_sitelib}/zapzap-*.dist-info/
%{_datadir}/applications/com.rtosta.zapzap.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/scalable
%dir %{_datadir}/icons/hicolor/scalable/apps
%{_datadir}/icons/hicolor/scalable/apps/com.rtosta.zapzap.svg
%{_datadir}/metainfo/com.rtosta.zapzap.appdata.xml

%changelog
