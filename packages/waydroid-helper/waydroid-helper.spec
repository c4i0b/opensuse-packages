Name:           waydroid-helper
Version:        0.2.9
Release:        0
Summary:        A GUI application for Waydroid configuration and extension installation
License:        GPL-3.0-or-later
URL:            https://github.com/waydroid-helper/waydroid-helper
Source0:        waydroid-helper-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  meson
BuildRequires:  ninja
BuildRequires:  gcc
BuildRequires:  python3-devel
BuildRequires:  python3-rpm-macros
BuildRequires:  cairo-devel
BuildRequires:  gtk4-devel
BuildRequires:  libadwaita-devel
BuildRequires:  gobject-introspection-devel
BuildRequires:  dbus-1-devel
BuildRequires:  gettext-runtime
BuildRequires:  systemd
BuildRequires:  desktop-file-utils

Requires:       python3-base
Requires:       gtk4
Requires:       libadwaita
Requires:       fakeroot
Requires:       python3-aiofiles
Requires:       python3-httpx
Requires:       python3-cairo
Requires:       python3-gobject >= 3.50
Requires:       python3-pywayland
Requires:       python3-PyYAML
Requires:       python3-dbus-python
Requires:       android-tools

# waydroid itself is not in the Tumbleweed repositories; users install it
# from an upstream/OBS repository, so keep the dependency soft
Recommends:     waydroid

Recommends:     bindfs
Recommends:     hicolor-icon-theme

%description
Waydroid Helper is a graphical user interface application that provides a
user-friendly way to configure Waydroid and install extensions, including
Magisk, ARM translation, and various Google services alternatives.

%prep
%autosetup -p1

%build
%meson
%meson_build

%install
%meson_install

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/com.jaoushingan.WaydroidHelper.desktop

%files
%license COPYING
%doc README.md
%{_bindir}/waydroid-helper
%{_bindir}/waydroid-cli
%dir %{_datadir}/waydroid-helper
%{_datadir}/waydroid-helper/
%{_datadir}/applications/com.jaoushingan.WaydroidHelper.desktop
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/scalable/apps/com.jaoushingan.WaydroidHelper.svg
%{_datadir}/icons/hicolor/symbolic/apps/com.jaoushingan.WaydroidHelper-symbolic.svg
%{_datadir}/metainfo/com.jaoushingan.WaydroidHelper.metainfo.xml
%{_datadir}/glib-2.0/schemas/com.jaoushingan.WaydroidHelper.gschema.xml
%{_datadir}/polkit-1/actions/com.jaoushingan.WaydroidHelper.policy
%{_datadir}/locale/*/LC_MESSAGES/*.mo
%{_datadir}/dbus-1/system.d/id.waydro.Mount.conf
%{_datadir}/dbus-1/system-services/id.waydro.Mount.service
%{_prefix}/lib/systemd/system/waydroid-mount.service
%{_prefix}/lib/systemd/user/waydroid-monitor.service

%changelog
