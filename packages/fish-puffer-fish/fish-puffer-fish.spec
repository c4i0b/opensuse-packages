Name:           fish-puffer-fish
Version:        1.1.0
Release:        0
Summary:        Text objects and double-tap key bindings for the fish shell (puffer-fish)
License:        MIT
URL:            https://github.com/nickeb96/puffer-fish
Source0:        fish-puffer-fish-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish

%description
Text objects and double-tap key bindings for the fish shell: expand
commands to pipelines, arguments and options with a few extra taps of
the Tab key.

%prep
%setup -q -n puffer-fish-%{version}

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
