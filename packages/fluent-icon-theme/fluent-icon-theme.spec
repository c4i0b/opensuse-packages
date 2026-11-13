%global tag    2026-07-27

Name:           fluent-icon-theme
Version:        2026.07.27
Release:        0
Summary:        Fluent icon theme
License:        GPL-3.0-only
URL:            https://github.com/vinceliuice/Fluent-icon-theme
Source0:        fluent-icon-theme-%{version}.tar.gz
BuildArch:      noarch

%description
Fluent icon theme

%prep
%setup -q -n Fluent-icon-theme-%{tag}

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
%{_datadir}/icons/Fluent*
# Shared content lives once in hidden .Fluent-* base dirs (each theme dir
# is symlinks into them); without the dotfile glob the links dangle.
%{_datadir}/icons/.Fluent*
%changelog
