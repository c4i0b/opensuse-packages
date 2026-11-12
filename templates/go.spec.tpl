# Template: Go prebuilt release binary (validated by packages/superfile-bin).
# Invariant: Go prebuilts are strip-safe, so never add __os_install_post here.
# OBS fetches the release tarball via _service. Source0's filename embeds the
# upstream naming scheme including the version and arch triplet.
# Changelog lives in <name>.changes (OBS merges it into %changelog).
Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            __URL__
Source0:        __SOURCE0__
ExclusiveArch:  x86_64

%description
__DESCRIPTION__

%prep
%setup -T -c -D
tar -xzf %{SOURCE0}

%build

%install
install -Dpm 0755 __EXTRACTDIR__/__BIN__ %{buildroot}%{_bindir}/__BIN__

%files
%{_bindir}/__BIN__

%changelog
