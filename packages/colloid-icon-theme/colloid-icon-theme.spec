%global tag    2026-08-10

Name:           colloid-icon-theme
Version:        2026.08.10
Release:        0
Summary:        Colloid icon theme
License:        GPL-3.0-only
URL:            https://github.com/vinceliuice/Colloid-icon-theme
Source0:        colloid-icon-theme-%{version}.tar.gz
BuildArch:      noarch

%description
Colloid icon theme

%prep
%setup -q -n Colloid-icon-theme-%{tag}

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
%license LICENSE
%{_datadir}/icons/Colloid*
%changelog
