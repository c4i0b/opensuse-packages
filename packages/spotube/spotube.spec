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

ExclusiveArch:  x86_64 aarch64

Name:           spotube
Version:        6.0.0
Release:        0
Summary:        Open source, collaborative Spotify client that does not require Premium
License:        AGPL-3.0-only
URL:            https://spotube.krtirtho.dev
%ifarch x86_64
Source0:        https://github.com/team-spotube/Spotube/releases/download/v%{version}/Spotube-linux-x86_64.rpm
%endif
%ifarch aarch64
Source0:        https://github.com/team-spotube/Spotube/releases/download/v%{version}/Spotube-linux-aarch64.rpm
%endif
Source1:        https://raw.githubusercontent.com/team-spotube/Spotube/v%{version}/LICENSE

# rpm2archive streams the payload as a tarball (libarchive/bsdtar cannot
# parse the RPMv4 containers electron-builder-era tooling ships)
BuildRequires:  rpm
BuildRequires:  desktop-file-utils

# Host libs the bundled tree dlopen()s/links: its requires are excluded
# with the bundle, so declare them here (rpmlintrc: explicit-lib-dependency)
Requires:       Mesa-libGL1
Requires:       libX11-6
Requires:       libfontconfig1
Requires:       libfreetype6
Requires:       libharfbuzz0
Requires:       alsa-lib

%description
Spotube is an open source, cross-platform Spotify client that plays tracks
from YouTube/other sources so a Spotify Premium subscription is not needed.
It keeps the Spotify ecosystem for library, playlists and metadata, streams
audio ad-free, syncs lyrics and is fully local: no telemetry, no ads.

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

# Upstream desktop Exec points into the bundle; rewrite to our wrapper
sed -i 's|^Exec=.*|Exec=spotube %U|' usr/share/applications/%{desktop_id}.desktop
grep -q '^Exec=spotube' usr/share/applications/%{desktop_id}.desktop || {
    echo "Exec= rewrite failed in %{desktop_id}.desktop" >&2
    exit 1
}
install -Dpm644 usr/share/applications/%{desktop_id}.desktop \
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
