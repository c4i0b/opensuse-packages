# Template: Electron app prebuilt (validated by packages/pear-desktop-bin).
# Invariants: the app tree installs under %{_libdir}/<name> with a symlink in
# %{_bindir}. The desktop file is a Source because release tarballs rarely
# ship one. Every dir under icons/hicolor must be owned via %dir or OBS
# check-filelist FAILs. Electron prebuilts are strip-safe.
# Changelog lives in <name>.changes (OBS merges it into %changelog).
Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            __URL__
Source0:        __SOURCE0__
Source1:        __NAME__.desktop
ExclusiveArch:  x86_64

%description
__DESCRIPTION__

%prep
%setup -T -c -D
tar -xzf %{SOURCE0}

%build

%install
src="__EXTRACTDIR__"
appdst="%{buildroot}%{_libdir}/__NAME__"
mkdir -p "$appdst" "%{buildroot}%{_bindir}" "%{buildroot}%{_datadir}/applications" "%{buildroot}%{_datadir}/icons/hicolor/scalable/apps"
cp -a "$src/." "$appdst/"
# Upstream binary name inside the tarball may differ from the package name:
mv "$appdst/__UPSTREAM_BIN__" "$appdst/__NAME__"
ln -s "%{_libdir}/__NAME__/__NAME__" "%{buildroot}%{_bindir}/__NAME__"
install -Dpm 0644 "%{SOURCE1}" "%{buildroot}%{_datadir}/applications/__NAME__.desktop"
# Pick the best icon upstream ships (scalable preferred over PNG sizes):
install -Dpm 0644 "$src/__ICONPATH__" "%{buildroot}%{_datadir}/icons/hicolor/scalable/apps/__NAME__.svg"

%files
%{_libdir}/__NAME__
%{_bindir}/__NAME__
%{_datadir}/applications/__NAME__.desktop
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/scalable
%dir %{_datadir}/icons/hicolor/scalable/apps
%{_datadir}/icons/hicolor/scalable/apps/__NAME__.svg

%changelog
