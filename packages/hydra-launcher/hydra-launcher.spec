# Electron payload: stripping corrupts the embedded snapshot
%define debug_package %{nil}
%global __strip /bin/true
# bundled python stdlib ships "#!/usr/bin/env python" shebangs brp-mangle rejects
%global __brp_mangle_shebangs %{nil}

# Bundled Electron + Python runtime must not leak into rpm provides/requires
%global __provides_exclude_from ^%{_libdir}/hydra-launcher/.*$
%global __requires_exclude_from ^%{_libdir}/hydra-launcher/.*$

ExclusiveArch:  x86_64

Name:           hydra-launcher
Version:        4.4.1
Release:        0
Summary:        Game launcher with a self-hosted torrent library source
License:        MIT AND GPL-3.0-only
URL:            https://github.com/hydralauncher/hydra
Source0:        https://github.com/hydralauncher/hydra/releases/download/v%{version}/hydralauncher-%{version}.x86_64.rpm
Source1:        https://raw.githubusercontent.com/hydralauncher/hydra/v%{version}/LICENSE

BuildRequires:  bsdtar
BuildRequires:  desktop-file-utils
BuildRequires:  binutils

# Host libs the bundled Electron dlopen()s; the bundle's requires are excluded
Requires:       gtk3
Requires:       nss
Requires:       libsecret
Requires:       alsa-lib
Requires:       libXScrnSaver

%description
Hydra is a game launcher that lets you organize and launch your library,
track playtime, achievements and leaderboards, and download games from
self-hosted torrent library sources. Also launches Epic titles via the
bundled Legendary and runs Windows games through umu/proton.
Bundles its own Electron and Python runtimes.

%prep
%setup -T -q -c
bsdtar -xf %{SOURCE0}

%build
# The app's own i18n is JS; Chromium locale paks only cover Electron-internal
# strings and fall back to en-US — keep the majors
for pak in opt/Hydra/locales/*.pak; do
  case "$(basename "$pak" .pak)" in
    en-US|en-GB|pt-BR|pt-PT|es|es-419|fr|de|it|ja|ko|ru|pl|nl|tr|uk|zh-CN|zh-TW|cs|el|hu|id|ro|sv|th|vi|ar|hi) ;;
    *) rm -f "$pak" ;;
  esac
done

# strip symtab/debug from the bundled native ELFs (Rust addon, sharp/libvips,
# classic-level prebuilds). Never the Electron binary or its snapshot —
# stripping corrupts those, see the globals. resources/legendary must stay
# untouched: the app verifies that tree against .runtime-files.json on startup.
strip --strip-unneeded \
  opt/Hydra/resources/hydra-native/hydra-native.node \
  opt/Hydra/resources/hydra-native/libhydra_torrent_bridge.so
# classic-level prebuilds ship every architecture; keep the x86-64 one
rm -rf opt/Hydra/resources/app.asar.unpacked/node_modules/classic-level/prebuilds/{linux-arm64,linux-arm,darwin-x64+arm64,android-arm64,android-arm}
find opt/Hydra/resources/app.asar.unpacked -name '*.node' -o -name '*.so*' \
  | xargs -r strip --strip-unneeded 2>/dev/null || :

%install
appdir=%{buildroot}%{_libdir}/hydra-launcher
install -d "$appdir"
cp -a opt/Hydra/. "$appdir"/
rm -f "$appdir"/resources/app-update.yml

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/hydralauncher <<EOF
#!/bin/sh
exec %{_libdir}/hydra-launcher/hydralauncher "\$@"
EOF
chmod 755 %{buildroot}%{_bindir}/hydralauncher

# Upstream desktop Exec points into the bundle; rewrite to our wrapper
sed -i 's|^Exec=.*|Exec=hydralauncher %U|' usr/share/applications/hydralauncher.desktop
install -Dpm644 usr/share/applications/hydralauncher.desktop \
  %{buildroot}%{_datadir}/applications/hydralauncher.desktop

for png in usr/share/icons/hicolor/*/apps/*.png; do
  install -Dpm644 "$png" "%{buildroot}%{_datadir}/icons/hicolor/${png#*hicolor/}"
done

install -pm644 %{SOURCE1} LICENSE
cp -a opt/Hydra/LICENSE.electron.txt opt/Hydra/LICENSES.chromium.html .
cp -a opt/Hydra/resources/legendary/LICENSE legendary-LICENSE
cp -a opt/Hydra/resources/legendary/NOTICE.md legendary-NOTICE.md

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files
%license LICENSE LICENSE.electron.txt LICENSES.chromium.html legendary-LICENSE legendary-NOTICE.md
%{_bindir}/hydralauncher
%{_libdir}/hydra-launcher/
%{_datadir}/applications/hydralauncher.desktop
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/hydralauncher.png

%changelog
