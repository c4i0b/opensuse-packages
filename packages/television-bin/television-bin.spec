Name:           television-bin
Version:        0.15.9
Release:        0
Summary:        A very fast, portable and hackable fuzzy finder
License:        MIT
URL:            https://github.com/alexpasmantier/television
Source0:        tv-%{version}-x86_64-unknown-linux-gnu.tar.gz
ExclusiveArch:  x86_64

%description
A very fast, portable and hackable fuzzy finder for the terminal.

%prep
%setup -T -c -D
tar -xzf %{SOURCE0}

%build

%install
src="tv-%{version}-x86_64-unknown-linux-gnu"
install -Dpm 0755 "$src/tv" %{buildroot}%{_bindir}/tv
install -Dpm 0644 "$src/LICENSE" LICENSE
install -Dpm 0644 "$src/doc/tv.1" %{buildroot}%{_mandir}/man1/tv.1.gz
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions %{buildroot}%{_datadir}/zsh/site-functions %{buildroot}%{_datadir}/fish/vendor_completions.d
"$src/tv" init bash > %{buildroot}%{_datadir}/bash-completion/completions/tv
"$src/tv" init zsh  > %{buildroot}%{_datadir}/zsh/site-functions/_tv
"$src/tv" init fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/tv.fish

%files
%license LICENSE
%{_bindir}/tv
%{_mandir}/man1/tv.1.gz
%{_datadir}/bash-completion/completions/tv
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_tv
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/tv.fish

%changelog
