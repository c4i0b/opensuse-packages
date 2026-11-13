Name:           fish-fzf
Version:        11.0
Release:        0
Summary:        fzf key bindings for the fish shell
License:        MIT
URL:            https://github.com/patrickf1/fzf.fish
Source0:        fish-fzf-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish
Requires:       fzf
Requires:       fd
Requires:       bat

%description
fzf key bindings for the fish shell: fuzzy search of history, directory
contents, git status and log, processes and variables, with file previews.

%prep
%setup -q -n fzf.fish-%{version}

%build

%install
install -Dpm644 conf.d/fzf.fish %{buildroot}%{_datadir}/fish/vendor_conf.d/fzf.fish
for f in functions/*.fish; do
  install -Dpm644 "$f" "%{buildroot}%{_datadir}/fish/vendor_functions.d/$(basename "$f")"
done
install -Dpm644 completions/fzf_configure_bindings.fish \
  %{buildroot}%{_datadir}/fish/vendor_completions.d/fzf_configure_bindings.fish

%files
%license LICENSE.md
%doc README.md
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_conf.d
%{_datadir}/fish/vendor_conf.d/fzf.fish
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/*.fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/fzf_configure_bindings.fish

%changelog
