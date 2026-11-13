Name:           ludusavi
Version:        0.31.0
Release:        0
Summary:        Game save backup tool
License:        MIT
URL:            https://github.com/mtkennerly/ludusavi
Source0:        ludusavi-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(xkbcommon)

%description
Ludusavi backs up and restores game saves across multiple roots, mapping them
to a known game database (the ludusavi manifest) so files land in predictable
locations.

%prep
%autosetup -p1 -a1

%build
%{cargo_build}

%install
install -Dpm 0755 target/release/ludusavi %{buildroot}%{_bindir}/ludusavi
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions %{buildroot}%{_datadir}/zsh/site-functions %{buildroot}%{_datadir}/fish/vendor_completions.d
target/release/ludusavi complete bash > %{buildroot}%{_datadir}/bash-completion/completions/ludusavi
target/release/ludusavi complete zsh  > %{buildroot}%{_datadir}/zsh/site-functions/_ludusavi
target/release/ludusavi complete fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/ludusavi.fish

%files
%license LICENSE
%doc README.md
%{_bindir}/ludusavi
%{_datadir}/bash-completion/completions/ludusavi
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_ludusavi
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/ludusavi.fish

%changelog
