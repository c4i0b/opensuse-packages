# Upstream-RPM repackage: Source0 is the official upstream RPM; %prep
# unpacks it with rpm2archive and %install re-bundles the payload under
# %_libdir with a wrapper in %_bindir (rpm-repackage.spec.tpl model).
# Spotube 6 is Kotlin Compose Multiplatform: the payload bundles a JVM and
# the Skiko (Skia) runtime whose sonames must not leak into requires, and
# the prebuilt tree is kept byte-identical -> strip off, like ventoy.
%define debug_package %{nil}
%global __strip /bin/true

# Bundled JVM/Skiko tree must not leak into rpm provides/requires
%global __provides_exclude_from ^%{_libdir}/spotube/.*$
%global __requires_exclude_from ^%{_libdir}/spotube/.*$

# single definition of the upstream payload dir and desktop id
%global appdir opt/spotube
%global desktop_id spotube

ExclusiveArch:  x86_64

Name:           spotube
Version:        6.0.0
Release:        0
Summary:        Spotify-compatible client that streams from YouTube Music
License:        AGPL-3.0-only
URL:            https://spotube.krtirtho.dev
Source0:        https://github.com/team-spotube/Spotube/releases/download/v%{version}/Spotube-linux-x86_64.rpm
Source1:        https://raw.githubusercontent.com/team-spotube/Spotube/v%{version}/LICENSE

# rpm2archive streams the payload as a tarball (libarchive/bsdtar cannot
# parse the RPMv4 containers electron-builder-era tooling ships)
BuildRequires:  rpm
BuildRequires:  desktop-file-utils

# Host libs the bundled tree dlopen()s/links: its requires are excluded
# with the bundle, so declare them here (rpmlintrc: explicit-lib-dependency)
Requires:       Mesa-libGL1
Requires:       libX11-6
Requires:       libXext6
Requires:       libXi6
Requires:       libXrender1
Requires:       libXtst6
Requires:       libfontconfig1
Requires:       libfreetype6
Requires:       libharfbuzz0
Requires:       alsa-lib
Requires:       dbus-1
# vlcj loads libvlc via JNA/dlopen at runtime: no auto-requires is
# generated, but the app hard-fails without it (red: spotube 6.0.0 crash
# on launch, UnsatisfiedLinkError libvlc.so). Minimal set, mirroring the
# upstream .deb Depends (libvlc5 + vlc-plugin-base): libvlc5 + vlc-noX
# (plugin set without X/UI) — NOT the full vlc (Qt UI and X video outputs
# the app never uses). vlc-codecs (ffmpeg plugin) is deliberately NOT
# required: it lives only in Packman (libavcodec unrestricted) and the
# native libopus/libfaad plugins in vlc-noX cover YouTube Music's
# opus/aac streams
Requires:       libvlc5
Requires:       vlc-noX
# Compose webview (Spotify login) dlopens WebKitGTK; the AWT/Swing GTK
# backend dlopens gtk3 — neither generates soname requires
Requires:       libwebkit2gtk-4_1-0
Requires:       gtk3
# Upstream .deb Recommends it for the tray icon
Recommends:     libappindicator3-1

%description
Spotube is a lightweight Spotify-compatible client that streams audio from
YouTube Music, needing no Spotify Premium account. It is a Kotlin Compose
Multiplatform app that bundles its own JVM/Skiko runtime and plays through
the system VLC libraries.

%prep
%setup -T -q -c
rpm2archive %{SOURCE0} > payload.tgz
tar -xzf payload.tgz

%build

%install
appdir=%{buildroot}%{_libdir}/spotube
install -d "$appdir"
cp -a %{appdir}/. "$appdir"/

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/spotube <<EOF
#!/bin/sh
exec %{_libdir}/spotube/spotube "\$@"
EOF
chmod 755 %{buildroot}%{_bindir}/spotube

# Upstream desktop Exec points into the bundle; rewrite to our wrapper and
# fix the upstream-generic Name/Categories ("Packaged desktop application",
# Utility — same fix the fedora-packages twin carries)
desktop_file=usr/share/applications/%{desktop_id}.desktop
sed -i -e 's|^Exec=.*|Exec=spotube %U|' \
       -e 's|^Name=.*|Name=Spotube|' \
       -e 's|^Comment=.*|Comment=Spotify-compatible client using YouTube Music|' \
       -e 's|^Categories=.*|Categories=Audio;AudioVideo;Music;|' "$desktop_file"
grep -q '^Exec=spotube' "$desktop_file" || {
    echo "Exec= rewrite failed in %{desktop_id}.desktop" >&2
    exit 1
}
install -Dpm644 "$desktop_file" \
  %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

for png in usr/share/icons/hicolor/*/apps/*.png; do
  install -Dpm644 "$png" "%{buildroot}%{_datadir}/icons/hicolor/${png#*hicolor/}"
done

install -pm644 %{SOURCE1} LICENSE

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

%files
%license LICENSE
%{_bindir}/spotube
%{_libdir}/spotube/
%{_datadir}/applications/%{desktop_id}.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/*.png

%changelog
