Name:           fish-nvm
Version:        2.2.17
Release:        0
Summary:        The Node.js version manager for fish
License:        MIT
URL:            https://github.com/jorgebucaran/nvm.fish
Source0:        fish-nvm-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish
# version downloads (curl) and tarball extraction (tar) are unguarded
Requires:       curl
Requires:       tar

%description
The Node.js version manager for fish: install, switch and remove Node
versions with a fast, simple interface built around fish abbreviations.

%prep
%setup -q -n nvm.fish-%{version}

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
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/*.fish

%changelog
