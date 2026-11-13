# Template: noarch icon theme (vinceliuice family: Colloid/Tela/Qogir/
# WhiteSur/Fluent; validated by packages/tela-icon-theme).
# Invariants:
# - noarch, no build step, no scriptlets: Tumbleweed updates icon caches
#   via RPM file triggers (gtk3/gtk4 own them), matching current Factory
#   practice (papirus-icon-theme, kora-icon-theme ship no %post).
# - upstream tags are dates ("2026-08-10"); RPM Version forbids '-', so
#   the raw tag lives in %global tag (referenced by %setup -n) and Version
#   is the dot-sanitized form. Bumps go through tools/bump-date-tag.sh
#   via a per-package bump.sh (spec tag + Version + _service stay in sync).
# - %install runs upstream install.sh with -d into the buildroot; it
#   assembles the theme from src/ + links/ (recoloring variants on the
#   fly), so file lists must stay glob-based (%{_datadir}/icons/<Theme>*),
#   never enumerated. Icons dirs are distro-owned: no %dir ownership
#   needed (icons is a system datadir, see opensuse-lint.py).
# Changelog lives in <name>.changes (OBS merges it into %changelog).
%global tag    __TAG__

Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            __URL__
Source0:        __NAME__-%{version}.tar.gz
BuildArch:      noarch

%description
__DESCRIPTION__

%prep
%setup -q -n __REPO__-%{tag}

%build

%install
# install.sh calls gtk-update-icon-cache (absent from the buildroot; caches
# are rpm file triggers on user systems) and refuses a missing dest dir.
sed -i '/gtk-update-icon-cache/d' install.sh
mkdir -p %{buildroot}%{_datadir}/icons
./install.sh -d %{buildroot}%{_datadir}/icons
# install.sh leaves symlinks whose targets only exist in other theme
# variants; OBS brp fails the build on dangling links
find %{buildroot}%{_datadir}/icons -xtype l -delete

%files
%license __LICENSEFILE__
%{_datadir}/icons/__THEME__*

%changelog
