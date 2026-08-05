Name:           pear-desktop-bin
Version:        3.12.0
Release:        0
Summary:        YouTube Music desktop app
License:        MIT
URL:            https://github.com/pear-devs/pear-desktop
Source0:        youtube-music-%{version}.tar.gz
Source1:        pear-desktop.desktop
ExclusiveArch:  x86_64

%description
YouTube Music desktop app with custom plugins.

%prep
%setup -T -c -D
tar -xzf %{SOURCE0}

%build

%install
src="youtube-music-%{version}"
appdst="%{buildroot}%{_libdir}/pear-desktop"
mkdir -p "$appdst" "%{buildroot}%{_bindir}" "%{buildroot}%{_datadir}/applications" "%{buildroot}%{_datadir}/icons/hicolor/scalable/apps"
cp -a "$src/." "$appdst/"
mv "$appdst/youtube-music" "$appdst/pear-desktop"
ln -s "%{_libdir}/pear-desktop/pear-desktop" "%{buildroot}%{_bindir}/pear-desktop"
install -Dpm 0644 "%{SOURCE1}" "%{buildroot}%{_datadir}/applications/pear-desktop.desktop"
install -Dpm 0644 "$src/resources/app.asar.unpacked/assets/icon.svg" "%{buildroot}%{_datadir}/icons/hicolor/scalable/apps/pear-desktop.svg"

%files
%{_libdir}/pear-desktop
%{_bindir}/pear-desktop
%{_datadir}/applications/pear-desktop.desktop
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/scalable
%dir %{_datadir}/icons/hicolor/scalable/apps
%{_datadir}/icons/hicolor/scalable/apps/pear-desktop.svg

%changelog
