# Electron payload: stripping corrupts the embedded snapshot, and the
# debugsource list would be empty anyway
%define debug_package %{nil}
%global __strip /bin/true

# Bundled Electron must not leak into rpm provides/requires
%global __provides_exclude_from ^%{_libdir}/pear-desktop/.*$
%global __requires_exclude_from ^%{_libdir}/pear-desktop/.*$

# single definition of the upstream desktop-file id
%global desktop_id com.github.th-ch.youtube-music

ExclusiveArch:  x86_64

Name:           pear-desktop
Version:        3.12.0
Release:        0
Summary:        YouTube Music Desktop App including custom plugins (Electron)

License:        MIT AND BSD-2-Clause AND BSD-3-Clause AND LGPL-2.1-or-later AND Apache-2.0 AND Zlib
URL:            https://github.com/pear-devs/pear-desktop
Source0:        https://github.com/pear-devs/pear-desktop/releases/download/v%{version}/youtube-music-%{version}.x86_64.rpm
Source1:        https://raw.githubusercontent.com/pear-devs/pear-desktop/v%{version}/license

BuildRequires:  bsdtar
BuildRequires:  desktop-file-utils

Requires:       gtk3
Requires:       nss
Requires:       libsecret
Requires:       alsa-lib
Requires:       libXScrnSaver

%description
Pear Desktop is a YouTube Music Desktop App including custom plugins,
bringing a native look and feel to the YouTube Music streaming service.
It bundles its own Electron runtime.

%prep
%setup -T -q -c
bsdtar -xf %{SOURCE0}

%build

%install
appdir=%{buildroot}%{_libdir}/pear-desktop
install -d "$appdir"
cp -a "opt/YouTube Music/." "$appdir"/
rm -f "$appdir"/resources/app-update.yml

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/pear-desktop <<EOF
#!/bin/sh
exec %{_libdir}/pear-desktop/youtube-music "\$@"
EOF
chmod 755 %{buildroot}%{_bindir}/pear-desktop

# Upstream desktop Exec points into the bundle; rewrite to our wrapper
sed -i 's|^Exec=.*|Exec=pear-desktop %U|' "usr/share/applications/%{desktop_id}.desktop"
grep -q '^Exec=pear-desktop' "usr/share/applications/%{desktop_id}.desktop" || {
    echo "Exec= rewrite failed in %{desktop_id}.desktop" >&2
    exit 1
}
echo 'Keywords=pear;pear-desktop;music;player;' >> "usr/share/applications/%{desktop_id}.desktop"
install -Dpm644 "usr/share/applications/%{desktop_id}.desktop" \
  %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

for png in usr/share/icons/hicolor/*/apps/*.png; do
  install -Dpm644 "$png" "%{buildroot}%{_datadir}/icons/hicolor/${png#*hicolor/}"
done

install -pm644 %{SOURCE1} LICENSE
cp -a "opt/YouTube Music/LICENSE.electron.txt" "opt/YouTube Music/LICENSES.chromium.html" .

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files
%license LICENSE LICENSE.electron.txt LICENSES.chromium.html
%{_bindir}/pear-desktop
%{_libdir}/pear-desktop/
%{_datadir}/applications/*.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/*.png

%changelog
