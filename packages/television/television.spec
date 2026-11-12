Name:           television
Version:        0.15.9
Release:        0
Summary:        A very fast and hackable fuzzy finder for the terminal
License:        MIT
URL:            https://github.com/alexpasmantier/television
Source0:        television-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging

%description
Television is a fast and portable fuzzy finder with a channel system: canned
selections (files, git, env, emojis, ...) each with their own source command,
preview command and keybindings.

%prep
%autosetup -p1 -a1

%build
%{cargo_build}

%install
install -Dpm 0755 target/release/tv %{buildroot}%{_bindir}/tv
install -Dpm 0644 man/tv.1 %{buildroot}%{_mandir}/man1/tv.1
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions %{buildroot}%{_datadir}/zsh/site-functions %{buildroot}%{_datadir}/fish/vendor_completions.d
target/release/tv init bash > %{buildroot}%{_datadir}/bash-completion/completions/tv
target/release/tv init zsh  > %{buildroot}%{_datadir}/zsh/site-functions/_tv
target/release/tv init fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/tv.fish

%files
%license LICENSE
%doc CHANGELOG.md README.md
%{_bindir}/tv
%{_mandir}/man1/tv.1%{?ext_man}
%{_datadir}/bash-completion/completions/tv
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_tv
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/tv.fish

%changelog
