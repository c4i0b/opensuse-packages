Name:           deckcraft
Version:        0.18.1
Release:        0
Summary:        Presentation designer with themes, animations and pptx support
License:        MIT OR Apache-2.0
URL:            https://github.com/storytold/deckcraft
Source0:        deckcraft-%{version}.tar.zst
Source1:        vendor.tar.zst
Source2:        %{name}.desktop
BuildRequires:  cargo-packaging
BuildRequires:  gcc
# cpal's ALSA backend resolves libasound through pkg-config
BuildRequires:  pkgconfig(alsa)
BuildRequires:  desktop-file-utils
ExclusiveArch:  x86_64 aarch64

# Bin-only crate: do not install sources into the cargo registry
%global cargo_install_lib false

# Release profile strips the binary and vendor sources trip the shebang BRP
%global debug_package %{nil}

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
DeckCraft is an open-source, pure-Rust presentation and slide designer.
It builds decks with themes, layouts, shapes, pictures, tables, charts,
transitions and animations, opens and saves .pptx presentation files, and
presents them full screen. Every button is also a command that the CLI and
AI agents (through MCP) can drive.

%prep
%autosetup -p1 -a1

%build
# zbus-lockstep's validate macro looks for ../xml relative to the crate
# being compiled: in a vendored tree that resolves to the vendored "xml"
# crate (whose extensionless LICENSE panics the macro) instead of
# atspi-common's D-Bus XML dir. obs-service-cargo_vendor dirs carry a
# version suffix, hence the glob.
lockstep_xml="$(echo vendor/atspi-common-*/xml)"
[ -d "$lockstep_xml" ] && export LOCKSTEP_XML_PATH="$(pwd)/$lockstep_xml"
%{cargo_build}

%install
install -Dpm0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

install -Dpm0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/ai.storyteller.deckcraft.desktop

# ship whatever sizes upstream provides (they change between releases)
for icon in assets/app-icon/hicolor/*/apps/*; do
    install -Dpm0644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/${icon#assets/app-icon/hicolor/}"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/ai.storyteller.deckcraft.desktop

%files
%license LICENSE-APACHE LICENSE-MIT NOTICE
%doc README.md
%{_bindir}/deckcraft
%{_datadir}/applications/ai.storyteller.deckcraft.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/ai.storyteller.deckcraft.*

%changelog
