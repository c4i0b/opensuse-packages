%global tag    2025-02-15

Name:           qogir-icon-theme
Version:        2025.02.15
Release:        0
Summary:        Qogir icon theme
License:        GPL-3.0-only
URL:            https://github.com/vinceliuice/Qogir-icon-theme
Source0:        qogir-icon-theme-%{version}.tar.gz
BuildArch:      noarch

%description
Qogir icon theme

%prep
%setup -q -n Qogir-icon-theme-%{tag}

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
%{_datadir}/icons/Qogir*
%changelog
