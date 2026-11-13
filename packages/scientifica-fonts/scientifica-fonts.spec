# Prebuilt font straight from the GitHub release tarball (patching at
# build time would drag fontforge for zero gain); the tarball ships no
# license file, so Source1 is the OFL text from the tagged repo. Only the
# ttf set is installed: the bdf/otb copies serve legacy X11 bitmap apps
# that fontconfig does not consume.
Name:           scientifica-fonts
Version:        2.3
Release:        0
Summary:        Tall and condensed bitmap-style typeface based on creep
License:        OFL-1.1
URL:            https://github.com/oppiliappan/scientifica
Source0:        https://github.com/oppiliappan/scientifica/releases/download/v%{version}/scientifica.tar
Source1:        https://raw.githubusercontent.com/oppiliappan/scientifica/v%{version}/LICENSE
BuildArch:      noarch
BuildRequires:  fontpackages-devel

%reconfigure_fonts_prereq

%description
Tall and condensed bitmap-style typeface based on creep, designed for
small terminal sizes.

%prep
%setup -q -n scientifica
cp -a %{SOURCE1} LICENSE

%build

%install
install -d %{buildroot}%{_ttfontsdir}
install -m 0644 -p ttf/*.ttf %{buildroot}%{_ttfontsdir}/

%reconfigure_fonts_scriptlets

%files
%license LICENSE
%{_ttfontsdir}

%changelog
