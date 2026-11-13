# Template: prebuilt/no-build font package (validated by the *-nerd-fonts,
# press-start-2p-fonts, scientifica-fonts, selawik-fonts ports).
# openSUSE conventions (verified against Factory fira-code-fonts /
# jetbrains-mono-fonts and the fontpackages-devel macros):
#   - macros come from BuildRequires: fontpackages-devel (Factory name;
#     Fedora's fonts-srpm-macros / fontpackages-filesystem do not exist).
#     %%_ttfontsdir = %%{_datadir}/fonts/truetype and is THE install dir for
#     both ttf and otf on openSUSE (no per-package subdir — unlike Fedora's
#     %%_fontbasedir/<name> model). %%files lists %%{_ttfontsdir} bare: that
#     includes the installed files AND the co-owned truetype dir, which every
#     font package shares (standard SUSE pattern, do not add %dir).
#   - %%reconfigure_fonts_prereq next to BuildRequires wires the
#     post/postun/posttrans scriptlets; %%reconfigure_fonts_scriptlets in the
#     body regenerates the fontconfig cache via fonts-config (SUSE's
#     replacement for Fedora's fontcache ghost files).
#   - Sources are full upstream URLs (release tarball + license file, since
#     most font artifacts ship no license inside); each gets a download_url
#     entry in _service. Use v%%{version} in URLs for autoupdate.
#   - Changelog lives in <name>.changes (OBS merges it into %changelog).
# Appstream/metainfo: only if upstream ships one — add
#   %{_datadir}/metainfo/*.metainfo.xml to %files (metainfo is a system
#   datadir, no %dir needed); none of the current font ports do.
Name:           __NAME__-fonts
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            __URL__
Source0:        __SOURCE0__
Source1:        __SOURCE1__
BuildArch:      noarch
BuildRequires:  fontpackages-devel

%reconfigure_fonts_prereq

%description
__DESCRIPTION__

%prep
# Tarball layout varies: flat release tarball (nerd fonts, selawik zip),
# top-dir tarball (scientifica -n <dir>), or bare files (press-start-2p:
# %setup -T -q -c and install straight from %%{SOURCE0}).
%setup -T -q -c -a 0
cp -a %{SOURCE1} LICENSE

%build

%install
install -d %{buildroot}%{_ttfontsdir}
install -m 0644 -p *.ttf %{buildroot}%{_ttfontsdir}/

%reconfigure_fonts_scriptlets

%files
%license LICENSE
%{_ttfontsdir}

%changelog
