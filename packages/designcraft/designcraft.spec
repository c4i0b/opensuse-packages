# Bin-only crate: do not install sources into the cargo registry
%global cargo_install_lib false
# Release profile strips the binary and vendor sources trip the shebang BRP
%global debug_package %{nil}

# wgpu renders only on these (no 32-bit, no ppc)
ExclusiveArch:  x86_64 aarch64

Name:           designcraft
Version:        0.20.1
Release:        0
Summary:        Page layout and desktop publishing studio
License:        MIT OR Apache-2.0
URL:            https://github.com/storytold/designcraft
Source0:        designcraft-%{version}.tar.zst
Source1:        vendor.tar.zst
Source2:        %{name}.desktop
BuildRequires:  cargo-packaging
BuildRequires:  gcc
BuildRequires:  desktop-file-utils

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
DesignCraft is an open-source, native desktop publishing and page layout
studio built in pure Rust. It lays out magazines, books and print
documents with an egui-based GPU-accelerated workspace, and imports
IDML and EPUB content.

%prep
%autosetup -p1 -a1
# patched but unused in the build graph: cargo locks them but does not
# vendor them, and offline cargo cannot verify their git patch locations
sed -i -e '/^egui_demo_lib = /d' -e '/^egui_inspection = /d' \
       -e '/^egui_system_font_provider = /d' Cargo.toml

%build
# zbus-lockstep's validate macro looks for ../xml relative to the crate
# being compiled: in a vendored tree that resolves to the vendored "xml"
# crate (whose extensionless LICENSE panics the macro) instead of
# atspi-common's D-Bus XML dir
[ -d vendor/atspi-common/xml ] && export LOCKSTEP_XML_PATH="$(pwd)/vendor/atspi-common/xml"
# virtual workspace: build only the app member
%{cargo_build} -p %{name}

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/ai.storyteller.designcraft.desktop

# ship whatever sizes upstream provides (they change between releases)
for icon in assets/app-icon/hicolor/*/apps/*; do
    install -Dpm 0644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/${icon#assets/app-icon/hicolor/}"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/ai.storyteller.designcraft.desktop

%files
%license LICENSE-APACHE LICENSE-MIT NOTICE
%doc README.md
%{_bindir}/designcraft
%{_datadir}/applications/ai.storyteller.designcraft.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/ai.storyteller.designcraft.*

%changelog
