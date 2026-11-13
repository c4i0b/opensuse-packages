Name:           fish-pure
Version:        4.19.2
Release:        0
Summary:        Minimalistic, fast fish prompt (pure)
License:        MIT
URL:            https://github.com/pure-fish/pure
Source0:        fish-pure-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish

# Mutually exclusive with other prompts: they all own
# vendor_functions.d/fish_prompt.fish, and only one prompt can.
Provides:       fish-prompt = %{version}-%{release}
Conflicts:      fish-prompt

%description
Minimalistic, fast fish prompt: a pure-fish port of sindresorhus/pure
with git integration, command duration and exit status on failure.

%prep
%setup -q -n pure-%{version}

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
%doc README.md
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_conf.d
%{_datadir}/fish/vendor_conf.d/*.fish
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/*.fish

%changelog
