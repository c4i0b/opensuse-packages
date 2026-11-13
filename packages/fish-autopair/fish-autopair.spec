Name:           fish-autopair
Version:        1.0.4
Release:        0
Summary:        Automatic insertion of matching brackets and quotes for the fish shell
License:        MIT
URL:            https://github.com/jorgebucaran/autopair.fish
Source0:        fish-autopair-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish

%description
Automatic insertion and deletion of matching brackets and quotes for the
fish shell, with skipping over closing characters and wrapping of
selections.

%prep
%setup -q -n autopair.fish-%{version}

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
%license LICENSE.md
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_conf.d
%{_datadir}/fish/vendor_conf.d/*.fish
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/*.fish

%changelog
