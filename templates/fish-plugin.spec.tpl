# Template: Fish shell plugin (validated by packages/fisher).
# Invariant: noarch, no build step. Files drop into the fish vendor dirs,
# which must be owned via %dir or OBS check-filelist FAILs. Requires: fish
# because the plugin is inert without it.
# Changelog lives in <name>.changes (OBS merges it into %changelog).
Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            __URL__
Source0:        __SOURCE0__
BuildArch:      noarch

Requires:       fish

%description
__DESCRIPTION__

%prep
%setup -q

%build

%install
# Drop or extend per upstream layout (functions/, completions/, conf.d/):
install -Dpm 0644 functions/__NAME__.fish %{buildroot}%{_datadir}/fish/vendor_functions.d/__NAME__.fish
install -Dpm 0644 completions/__NAME__.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/__NAME__.fish

%files
%license LICENSE.md
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_functions.d
%{_datadir}/fish/vendor_functions.d/__NAME__.fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/__NAME__.fish

%changelog
