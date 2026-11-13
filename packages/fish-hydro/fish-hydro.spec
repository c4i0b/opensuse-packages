# No upstream tags/releases: version is a pinned commit snapshot (manual bumps).
Name:           fish-hydro
Version:        2026.02.23
Release:        0
Summary:        Fast async git prompt for fish (hydro)
License:        MIT
URL:            https://github.com/jorgebucaran/hydro
Source0:        fish-hydro-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish

# Mutually exclusive with other prompts: they all own
# vendor_functions.d/fish_prompt.fish, and only one prompt can.
Provides:       fish-prompt = %{version}-%{release}
Conflicts:      fish-prompt

%description
Fast async git prompt for fish: hydro renders the prompt in the
background so interactive sessions never block on git status.

%prep
%setup -q -n hydro-f130b55ee3eaf099eccf588e2a62e5447068d120

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
%doc README.md
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_conf.d
%{_datadir}/fish/vendor_conf.d/*.fish
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/*.fish

%changelog
