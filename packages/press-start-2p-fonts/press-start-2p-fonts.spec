# Prebuilt single-family font shipped as final .ttf by google/fonts (OFL:
# the upstream source is a .glyphs file, not buildable here): raw files
# pinned to a commit — google/fonts has no tags/releases, so version bumps
# are manual (no upstream file: the autoupdate bot skips it).
Name:           press-start-2p-fonts
Version:        3.000
Release:        0
Summary:        Press Start 2P pixel 8-bit arcade display font
License:        OFL-1.1
URL:            https://fonts.google.com/specimen/Press+Start+2P
Source0:        https://raw.githubusercontent.com/google/fonts/e06fe11c39051bddaef73ec338a9d1c8175723f1/ofl/pressstart2p/PressStart2P-Regular.ttf
Source1:        https://raw.githubusercontent.com/google/fonts/e06fe11c39051bddaef73ec338a9d1c8175723f1/ofl/pressstart2p/OFL.txt
BuildArch:      noarch
BuildRequires:  fontpackages-devel

%reconfigure_fonts_prereq

%description
Press Start 2P pixel 8-bit arcade display font, based on the Namco arcade
font of the 1980s.

%prep
%setup -T -q -c
cp -a %{SOURCE1} OFL.txt

%build

%install
install -d %{buildroot}%{_ttfontsdir}
install -m 0644 -p %{SOURCE0} %{buildroot}%{_ttfontsdir}/

%reconfigure_fonts_scriptlets

%files
%license OFL.txt
%{_ttfontsdir}

%changelog
