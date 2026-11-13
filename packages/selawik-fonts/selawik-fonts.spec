# Prebuilt release zip: ttf set plus web formats (eot/svg/woff/woff2) that
# fontconfig does not consume — only the ttf set is installed. The zip
# carries no license file, so Source1 is the OFL text from the tagged repo.
# Selawik is the Segoe UI metric-compatible open typeface by Microsoft.
Name:           selawik-fonts
Version:        1.01
Release:        0
Summary:        Open Segoe UI metric-compatible typeface by Microsoft
License:        OFL-1.1
URL:            https://github.com/microsoft/Selawik
Source0:        https://github.com/microsoft/Selawik/releases/download/%{version}/Selawik_Release.zip
Source1:        https://raw.githubusercontent.com/microsoft/Selawik/%{version}/LICENSE.txt
BuildArch:      noarch
BuildRequires:  fontpackages-devel
BuildRequires:  unzip

%reconfigure_fonts_prereq

%description
Selawik is an open, Segoe UI metric-compatible typeface by Microsoft,
usable as a drop-in replacement for Segoe UI on other platforms.

%prep
# flat zip (no top dir): -c creates the dir, -a 0 extracts into it
%setup -T -q -c -a 0
cp -a %{SOURCE1} LICENSE.txt

%build

%install
install -d %{buildroot}%{_ttfontsdir}
install -m 0644 -p *.ttf %{buildroot}%{_ttfontsdir}/

%reconfigure_fonts_scriptlets

%files
%license LICENSE.txt
%{_ttfontsdir}

%changelog
