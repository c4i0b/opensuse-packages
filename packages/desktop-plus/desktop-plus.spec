# Electron payload: stripping corrupts the embedded snapshot
%global debug_package %{nil}
%global __strip /bin/true

# Bundled Electron must not leak into rpm provides/requires
%global __provides_exclude_from ^%{_prefix}/lib/desktop-plus/.*$
%global __requires_exclude_from ^%{_prefix}/lib/desktop-plus/.*$

ExclusiveArch:  x86_64 aarch64

Name:           desktop-plus
Version:        3.6.11.0
Release:        0
Summary:        A GitHub Desktop fork with advanced functionality and improvements
License:        MIT
URL:            https://desktop-plus.org
Source0:        https://github.com/desktop-plus/desktop-plus/releases/download/v%{version}/DesktopPlus-v%{version}-linux-x86_64.rpm
Source1:        https://github.com/desktop-plus/desktop-plus/releases/download/v%{version}/DesktopPlus-v%{version}-linux-arm64.rpm
Source2:        org.desktop-plus.DesktopPlus.metainfo.xml

BuildRequires:  desktop-file-utils
# rpm2archive streams the payload as a tarball (libarchive misreads the
# rpm-6-built containers of these releases)
BuildRequires:  rpm

Requires:       git
Requires:       gtk3
Requires:       nss
Requires:       libsecret
Recommends:     (gnome-keyring or kwalletmanager)

%description
Desktop Plus is a community fork of GitHub Desktop with additional features:
commit search, multi-account support (GitHub, Bitbucket, GitLab, Codeberg),
commit graph, multiple stashes per branch, and more.

%prep
%setup -T -q -c
%ifarch x86_64
rpm2archive %{SOURCE0} > payload.tgz
%else
rpm2archive %{SOURCE1} > payload.tgz
%endif
tar -xzf payload.tgz

%build

%install
cp -a usr %{buildroot}/
appdir=%{buildroot}%{_prefix}/lib/desktop-plus
rm -f "$appdir"/chrome-sandbox
# Upstream links libcurl-gnutls (Debian-built Electron); retarget to the
# system libcurl (name padded to the same on-disk string length)
find "$appdir" -type f -executable -exec \
  sed -i 's/libcurl-gnutls\.so\.4/libcurl.so.4\x00\x00\x00\x00\x00\x00\x00/g' {} \;
chmod 0755 "$appdir"/resources/app/static/desktop-plus-cli
ln -sf %{_prefix}/lib/desktop-plus/resources/app/static/desktop-plus-cli \
  %{buildroot}%{_bindir}/desktop-plus-cli
rm -f %{buildroot}%{_datadir}/doc/desktop-plus/copyright

install -Dpm644 %{SOURCE2} %{buildroot}%{_datadir}/metainfo/org.desktop-plus.DesktopPlus.metainfo.xml

# Upstream desktop file uses an unregistered Category; sanitize it
sed -i 's/^Categories=.*/Categories=Development;X-GitHub;/' \
  %{buildroot}%{_datadir}/applications/*.desktop
install -pm644 "$appdir"/LICENSE . 2>/dev/null || true

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop

%files
%license LICENSE
%{_bindir}/desktop-plus
%{_bindir}/desktop-plus-cli
%{_prefix}/lib/desktop-plus/
%{_datadir}/applications/*.desktop
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/*.png
%{_datadir}/metainfo/org.desktop-plus.DesktopPlus.metainfo.xml

%changelog
