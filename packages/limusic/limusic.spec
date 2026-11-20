# Upstream-RPM repackage: Source0 is the official x86_64 RPM (Rust/Tauri
# binary + desktop file + icons), unpacked with rpm2archive and reinstalled
# verbatim. Single system-linked ELF, so auto requires resolve the sonames
# (libmpv.so.2 -> libmpv2, libwebkit2gtk-4.1 -> webkitgtk) and, being a Rust
# prebuilt, it is strip-safe: no strip overrides, unlike the Electron
# siblings (rpm-repackage.spec.tpl).
ExclusiveArch:  x86_64

Name:           limusic
Version:        1.4.1
Release:        0
Summary:        Native desktop YouTube Music client (Rust + Tauri, no Electron)
License:        GPL-3.0-or-later
URL:            https://limusic.app
Source0:        https://github.com/SimoHypers/limusic/releases/download/v%{version}/limusic-%{version}-1.x86_64.rpm
Source1:        https://raw.githubusercontent.com/SimoHypers/limusic/v%{version}/LICENSE
Source2:        https://raw.githubusercontent.com/SimoHypers/limusic/v%{version}/THIRD-PARTY-NOTICES.md

# rpm2archive streams the payload as a tarball (libarchive/bsdtar cannot
# parse the RPMv4 containers electron-builder-era tooling ships)
BuildRequires:  rpm
BuildRequires:  desktop-file-utils

# WebKit's GStreamer backend has no soname requires for its plugins: without
# autoaudiosink (gstreamer-plugins-good) the Google sign-in page aborts the
# WebKitWebProcess on purpose (red: limusic 1.4.0 crash after clicking Next,
# upstream issue #430 — upstream is adding it to limusic-bin deps too)
Requires:       gstreamer-plugins-good

%description
Limusic is a feature-rich, native desktop YouTube Music client built with
Rust and Tauri: no bundled browser runtime, no server, no ads in the audio.
It talks directly to YouTube's internal API, plays through the MPV library
with gapless playback and loudness normalization, and ships synced lyrics,
Discord Rich Presence, Last.FM and ListenBrainz scrobbling and Listen
Together rooms.

%prep
%setup -T -q -c
rpm2archive %{SOURCE0} > payload.tgz
tar -xzf payload.tgz

%build

%install
install -Dpm755 usr/bin/limusic-app %{buildroot}%{_bindir}/limusic-app

# Upstream desktop Exec/Comment/Categories are fine; only Name is
# all-lowercase (upstream branding), which reads off in menus — normalize
# like the fedora-packages twin
sed -i 's|^Name=.*|Name=Limusic|' usr/share/applications/limusic.desktop
grep -q '^Name=Limusic' usr/share/applications/limusic.desktop || {
    echo "Name= rewrite failed in limusic.desktop" >&2
    exit 1
}
install -Dpm644 usr/share/applications/limusic.desktop \
  %{buildroot}%{_datadir}/applications/limusic.desktop

# Includes the 256x256@2 hi-dpi slot; path-preserving copy handles it
for png in usr/share/icons/hicolor/*/apps/*.png; do
  install -Dpm644 "$png" "%{buildroot}%{_datadir}/icons/hicolor/${png#*hicolor/}"
done

install -pm644 %{SOURCE1} LICENSE
install -pm644 %{SOURCE2} THIRD-PARTY-NOTICES.md

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/limusic.desktop

%files
%license LICENSE
%doc THIRD-PARTY-NOTICES.md
%{_bindir}/limusic-app
%{_datadir}/applications/limusic.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/*.png

%changelog
