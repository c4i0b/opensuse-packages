# Nerd Fonts prebuilt family: patched .ttf set straight from a
# ryanoasis/nerd-fonts release tarball (patching at build time would drag
# fontforge plus the original font sources for zero gain). The release
# tarballs ship .ttf files only, so Source1 is the ORIGINAL font license
# under patched-fonts/<Family>/ in the nerd-fonts repo.
Name:           fira-code-nerd-fonts
Version:        3.5.1
Release:        0
Summary:        Fira Code typeface patched with Nerd Fonts symbols
License:        OFL-1.1
URL:            https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/FiraCode
Source0:        https://github.com/ryanoasis/nerd-fonts/releases/download/v%{version}/FiraCode.tar.xz
Source1:        https://raw.githubusercontent.com/ryanoasis/nerd-fonts/v%{version}/patched-fonts/FiraCode/LICENSE
BuildArch:      noarch
BuildRequires:  fontpackages-devel

%reconfigure_fonts_prereq

%description
Fira Code typeface patched with Nerd Fonts symbols (icon glyphs for
developer tools, patched in by the Nerd Fonts project).

%prep
%setup -T -q -c -a 0
cp -a %{SOURCE1} LICENSE

%build

%install
install -d %{buildroot}%{_ttfontsdir}
install -m 0644 -p *.ttf %{buildroot}%{_ttfontsdir}/

%reconfigure_fonts_scriptlets

%files
%license LICENSE
%{_ttfontsdir}

%changelog
