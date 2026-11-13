%global tag    2026-09-10

Name:           whitesur-icon-theme
Version:        2026.09.10
Release:        0
Summary:        WhiteSur icon theme (macOS style)
License:        GPL-3.0-only
URL:            https://github.com/vinceliuice/WhiteSur-icon-theme
Source0:        whitesur-icon-theme-%{version}.tar.gz
BuildArch:      noarch

%description
WhiteSur icon theme (macOS style)

%prep
%setup -q -n WhiteSur-icon-theme-%{tag}

%build

%install
# install.sh calls gtk-update-icon-cache (absent from the buildroot; caches
# are rpm file triggers on user systems) and refuses a missing dest dir.
sed -i '/gtk-update-icon-cache/d' install.sh
mkdir -p %{buildroot}%{_datadir}/icons
./install.sh -d %{buildroot}%{_datadir}/icons
# install.sh leaves symlinks whose targets only exist in other theme
# variants; OBS brp fails the build on dangling links
find %{buildroot}%{_datadir}/icons -xtype l -delete

%files
%license COPYING
%{_datadir}/icons/WhiteSur*
%changelog
