Name:           fisher
Version:        4.4.8
Release:        0
Summary:        A plugin manager for the Fish shell
License:        MIT
URL:            https://github.com/jorgebucaran/fisher
Source0:        fisher-%{version}.tar.gz
BuildArch:      noarch

Requires:       fish

%description
A plugin manager for the Fish shell.

%prep
%setup -q

%build

%install
install -Dpm 0644 functions/fisher.fish %{buildroot}%{_datadir}/fish/vendor_functions.d/fisher.fish
install -Dpm 0644 completions/fisher.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/fisher.fish

%files
%license LICENSE.md
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/fisher.fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/fisher.fish

%changelog
