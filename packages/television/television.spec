Name:           television
Version:        0.15.9
Release:        0
Summary:        A fast, portable fuzzy finder for the terminal
License:        MIT
URL:            https://github.com/alexpasmantier/television
Source0:        television-%{version}.tar.gz
Source1:        vendor.tar.zst
Source2:        cargo_config
Source3:        tv.1
BuildRequires:  cargo-packaging
BuildRequires:  rust >= 1.90

%description
A fast, portable and flexible fuzzy finder for the terminal.

%prep
%autosetup -n television-%{version} -a1 -p1
mkdir -p .cargo
cp %{SOURCE2} .cargo/config

%build
%{cargo_build}

%install
%{cargo_install}
install -Dm0644 %{SOURCE3} %{buildroot}%{_mandir}/man1/tv.1
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions %{buildroot}%{_datadir}/zsh/site-functions %{buildroot}%{_datadir}/fish/vendor_completions.d
%{buildroot}%{_bindir}/tv init bash > %{buildroot}%{_datadir}/bash-completion/completions/tv
%{buildroot}%{_bindir}/tv init zsh  > %{buildroot}%{_datadir}/zsh/site-functions/_tv
%{buildroot}%{_bindir}/tv init fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/tv.fish

%files
%license LICENSE
%doc README.md
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
