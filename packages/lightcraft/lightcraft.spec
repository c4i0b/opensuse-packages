Name:           lightcraft
Version:        0.21.1
Release:        0
Summary:        Non-destructive photo library and raw developer

License:        MIT OR Apache-2.0
URL:            https://github.com/storytold/lightcraft
Source0:        lightcraft-%{version}.tar.zst
Source1:        vendor.tar.zst
Source2:        %{name}.desktop

BuildRequires:  cargo-packaging
BuildRequires:  desktop-file-utils

# Bin-only crate: do not install sources into the cargo registry
%global cargo_install_lib false

# Upstream release profile keeps only line tables; vendor sources would
# otherwise trip the debuginfo BRP
%global debug_package %{nil}

ExclusiveArch:  x86_64 aarch64

# winit/wgpu dlopen these at runtime; Rust binaries declare no auto-deps
Requires:       libX11
Requires:       libXcursor
Requires:       libXi
Requires:       libXrandr
Requires:       libxkbcommon
Requires:       libxkbcommon-x11
Requires:       libwayland-client
Requires:       vulkan-loader

%description
LightCraft is a non-destructive photo library and raw developer. It organises
photos and develops raw files with a GPU pipeline, using XMP-style sidecar
metadata so originals are never modified.

%prep
%autosetup -p1 -a1
# git [patch.crates-io] entries for crates nothing in the graph depends on
# are never vendored, yet cargo eagerly validates every patch entry against
# the directory source and aborts offline: drop the unvendored ones
for crate in $(awk '/^\[patch\.crates-io\]/{p=1;next} /^\[/{p=0} p && /= *\{ *git/{split($0,a,"="); print a[1]}' Cargo.toml); do
    ls -d vendor/"${crate}"-[0-9]* >/dev/null 2>&1 || \
        sed -i "/^${crate} *= *{ *git /d" Cargo.toml
done

%build
# zbus-lockstep's validate macro resolves ../xml relative to the crate being
# compiled: in a vendored tree that lands on the vendored "xml" crate (whose
# extensionless LICENSE panics the macro) instead of atspi-common's D-Bus
# XML dir
for d in vendor/atspi-common-*/xml; do
    [ -d "$d" ] && export LOCKSTEP_XML_PATH="$(pwd)/$d"
done
# the workspace root has no default member: build from the app crate dir
cd apps/%{name}
%cargo_build
cd ..

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

install -Dpm 0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/ai.storyteller.lightcraft.desktop

# ship whatever sizes upstream provides (they change between releases)
for icon in assets/app-icon/hicolor/*/apps/*; do
    install -Dpm 0644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/${icon#assets/app-icon/hicolor/}"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/ai.storyteller.lightcraft.desktop

%files
%license LICENSE-APACHE LICENSE-MIT NOTICE
%doc README.md
%{_bindir}/lightcraft
%{_datadir}/applications/ai.storyteller.lightcraft.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/ai.storyteller.lightcraft.*

%changelog
