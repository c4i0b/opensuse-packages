Name:           fish-abbreviation-tips
Version:        0.7.0
Release:        0
Summary:        Help you remember your fish abbreviations and aliases
License:        MIT
URL:            https://github.com/gazorby/fish-abbreviation-tips
Source0:        fish-abbreviation-tips-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish

%description
Helps you remember your fish abbreviations and aliases: after you use an
abbreviation, a tip showing the underlying command is displayed for a few
seconds so the full syntax eventually sticks.

%prep
%setup -q -n fish-abbreviation-tips-%{version}

%build

%install
install_vendor() {
  # $2: vendor subdir; conf.d already ends in .d, the others do not
  [ -d "$1" ] || return 0
  for f in "$1"/*.fish; do
    install -Dpm644 "$f" "%{buildroot}%{_datadir}/fish/vendor_$2/$(basename "$f")"
  done
}
install_vendor conf.d conf.d
install_vendor functions functions.d

%files
%license LICENSE
%doc README.md
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_conf.d
%{_datadir}/fish/vendor_conf.d/abbr_tips.fish
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/*.fish

%changelog
