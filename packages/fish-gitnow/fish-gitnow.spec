Name:           fish-gitnow
Version:        2.13.0
Release:        0
Summary:        Speed up your Git workflow with these few fish shell keybindings
License:        MIT
URL:            https://github.com/joseluisq/gitnow
Source0:        fish-gitnow-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish
Requires:       git

%description
Speed up your Git workflow with these few fish shell keybindings: stage,
commit, switch branches, stash and more, all from quick two-letter
bindings grouped by task.

%prep
%setup -q -n gitnow-%{version}

%build

%install
install_vendor() {
  # $2: vendor subdir; conf.d already ends in .d, the others do not
  [ -d "$1" ] || return 0
  for f in "$1"/*.fish; do
    install -Dpm644 "$f" "%{buildroot}%{_datadir}/fish/vendor_$2/$(basename "$f")"
  done
}
install -Dpm644 conf.d/gitnow.fish %{buildroot}%{_datadir}/fish/vendor_conf.d/gitnow.fish
install -Dpm644 conf.d/.gitnow %{buildroot}%{_datadir}/fish/vendor_conf.d/.gitnow
install_vendor functions functions.d
install_vendor completions completions.d

%files
%license LICENSE.md
%doc README.md
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_conf.d
%{_datadir}/fish/vendor_conf.d/gitnow.fish
%{_datadir}/fish/vendor_conf.d/.gitnow
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/*.fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/*.fish

%changelog
