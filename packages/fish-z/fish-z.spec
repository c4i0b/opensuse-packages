Name:           fish-z
Version:        2026.04.16
Release:        0
Summary:        Quick jumping between directories by frecent usage (z for fish)
License:        MIT
URL:            https://github.com/jethrokuan/z
Source0:        fish-z-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish

%description
Quick jumping between directories by frecent usage: a z implementation
for fish that tracks directory history and fuzzy-matches partial paths.

%prep
%setup -q -n z-26a50962bc68f5cb60fc488ee008b3d4d5be75f4

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
install -Dpm644 man/man1/z.1 %{buildroot}%{_mandir}/man1/z.1

%files
%license LICENSE
%{_mandir}/man1/z.1*
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_conf.d
%{_datadir}/fish/vendor_conf.d/*.fish
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/*.fish

%changelog
