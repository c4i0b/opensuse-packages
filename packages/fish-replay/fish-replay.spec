Name:           fish-replay
Version:        1.2.1
Release:        0
Summary:        Replay the captured output of a fish command without re-running it
License:        MIT
URL:            https://github.com/jorgebucaran/replay.fish
Source0:        fish-replay-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish

%description
Replay the captured output of a fish command without re-running it: lets
functions consume the output of another command as if it had just been
executed on demand.

%prep
%setup -q -n replay.fish-%{version}

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
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/*.fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/*.fish

%changelog
