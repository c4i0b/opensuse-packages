# Template: upstream-RPM repackage (validated by packages/pear-desktop).
# Model: NOT a source compile — Source0/Source1 are the official upstream
# RPMs (one per arch); %prep untars the matching one with bsdtar and %install
# re-bundles the payload under %_libdir with a wrapper in %_bindir.
#
# OBS fetches the RPMs server-side via _service download_url entries shaped
# like (one per arch + license, filenames must match the spec's sources):
#   <service name="download_url">
#     <param name="protocol">https</param>
#     <param name="host">github.com</param>
#     <param name="path">/OWNER/REPO/releases/download/v__VERSION__/NAME-__VERSION__.x86_64.rpm</param>
#     <param name="filename">NAME-__VERSION__.x86_64.rpm</param>
#   </service>
# Never commit the RPMs (gitignored); a per-package fetch.sh curls them for
# local pre-flight builds.
#
# Invariants (each one has a red behind it):
# - Stripping corrupts the embedded Electron snapshot -> strip + debug off.
# - The bundled Electron tree must not leak into rpm provides/requires ->
#   __provides_exclude_from / __requires_exclude_from on %_libdir/__NAME__.
# - OBS check-filelist FAILs on unowned hicolor dirs -> %dir lines in %files.
# - Changelog lives in <name>.changes (OBS merges it), %changelog stays empty.
%define debug_package %{nil}
%global __strip /bin/true

%global __provides_exclude_from ^%{_libdir}/__NAME__/.*$
%global __requires_exclude_from ^%{_libdir}/__NAME__/.*$

ExclusiveArch:  x86_64 aarch64

Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__

License:        __LICENSE__
URL:            __URL__
Source0:        https://github.com/__OWNER_REPO__/releases/download/v%{version}/__RPMBASE__-%{version}.x86_64.rpm
Source1:        https://github.com/__OWNER_REPO__/releases/download/v%{version}/__RPMBASE__-%{version}.aarch64.rpm
Source2:        https://raw.githubusercontent.com/__OWNER_REPO__/v%{version}/license

BuildRequires:  bsdtar
BuildRequires:  desktop-file-utils

# Host libs the bundled Electron dlopen()s: their requires are excluded with
# the bundle, so declare them here (rpmlintrc: explicit-lib-dependency).
Requires:       gtk3
Requires:       nss
Requires:       libsecret
Requires:       alsa-lib
Requires:       libXScrnSaver

%description
__DESCRIPTION__

%prep
%setup -T -q -c
%ifarch x86_64
bsdtar -xf %{SOURCE0}
%else
bsdtar -xf %{SOURCE1}
%endif

%build

%install
appdir=%{buildroot}%{_libdir}/__NAME__
install -d "$appdir"
cp -a __PAYLOAD_DIR__/. "$appdir"/
rm -f "$appdir"/resources/app-update.yml

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/__NAME__ <<EOF
#!/bin/sh
exec %{_libdir}/__NAME__/__BIN__ "\$@"
EOF
chmod 755 %{buildroot}%{_bindir}/__NAME__

# Upstream desktop Exec points into the bundle; rewrite to our wrapper
sed -i 's|^Exec=.*|Exec=__NAME__ %U|' usr/share/applications/__APPID__.desktop
install -Dpm644 usr/share/applications/__APPID__.desktop \
  %{buildroot}%{_datadir}/applications/__APPID__.desktop

for png in usr/share/icons/hicolor/*/apps/*.png; do
  install -Dpm644 "$png" "%{buildroot}%{_datadir}/icons/hicolor/${png#*hicolor/}"
done

install -pm644 %{SOURCE2} LICENSE
cp -a __PAYLOAD_DIR__/LICENSE.electron.txt __PAYLOAD_DIR__/LICENSES.chromium.html .

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files
%license LICENSE LICENSE.electron.txt LICENSES.chromium.html
%{_bindir}/__NAME__
%{_libdir}/__NAME__/
%{_datadir}/applications/*.desktop
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/*.png

%changelog
