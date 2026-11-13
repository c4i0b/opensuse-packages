Name:           fish-done
Version:        1.21.1
Release:        0
Summary:        Notifications when long-running fish commands finish
License:        MIT
URL:            https://github.com/franciscolourenco/done
Source0:        fish-done-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish

%description
Notifications when long-running fish commands finish: done watches every
command issued in the terminal and fires a desktop notification when it
completes after a configurable duration threshold.

%prep
%setup -q -n done-%{version}

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

%changelog
