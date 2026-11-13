%global tag    2026-07-07

Name:           tela-icon-theme
Version:        2026.07.07
Release:        0
Summary:        Tela icon theme
License:        GPL-3.0-only
URL:            https://github.com/vinceliuice/Tela-icon-theme
Source0:        tela-icon-theme-%{version}.tar.gz
BuildArch:      noarch

%description
Tela icon theme

%prep
%setup -q -n Tela-icon-theme-%{tag}

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
%{_datadir}/icons/Tela*
%changelog
