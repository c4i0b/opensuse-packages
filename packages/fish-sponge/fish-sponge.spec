Name:           fish-sponge
Version:        1.1.0
Release:        0
Summary:        Fish history filter: drop failed or short-lived commands
License:        MIT
URL:            https://github.com/meaningful-ooo/sponge
Source0:        fish-sponge-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish

%description
Fish history filter: sponge removes failed and short-lived commands from
the fish history automatically, so it stays clean and useful.

%prep
%setup -q -n sponge-%{version}

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
install_vendor completions completions.d

%files
%license LICENSE
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_conf.d
%{_datadir}/fish/vendor_conf.d/*.fish
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/*.fish

%changelog
