Name:           fish-tide
Version:        6.2.1
Release:        0
Summary:        The ultimate fish prompt (tide)
License:        MIT
URL:            https://github.com/IlanCosman/tide
Source0:        fish-tide-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish

# Mutually exclusive with other prompts: they all own
# vendor_functions.d/fish_prompt.fish, and only one prompt can.
Provides:       fish-prompt = %{version}-%{release}
Conflicts:      fish-prompt

%description
The ultimate fish prompt: a modern, highly configurable prompt framework
with powerline styling and items for git, duration, time and more,
configured interactively from fish itself.

%prep
%setup -q -n tide-%{version}

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
cp -a functions/tide %{buildroot}%{_datadir}/fish/vendor_functions.d/

%files
%license LICENSE.md
%doc README.md
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_conf.d
%{_datadir}/fish/vendor_conf.d/*.fish
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/*.fish
%{_datadir}/fish/vendor_functions.d/tide/
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/*.fish

%changelog
