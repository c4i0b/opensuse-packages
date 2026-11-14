Name:           filmcraft
Version:        0.20.1
Release:        0
Summary:        Nonlinear video editor with timeline, color and audio tools
License:        MIT OR Apache-2.0
URL:            https://github.com/storytold/filmcraft
Source0:        filmcraft-%{version}.tar.zst
Source1:        vendor.tar.zst
Source2:        %{name}.desktop
BuildRequires:  cargo-packaging
BuildRequires:  gcc
# cpal -> alsa -> alsa-sys resolves libasound via pkg-config
BuildRequires:  pkgconfig(alsa)
BuildRequires:  desktop-file-utils
ExclusiveArch:  x86_64

# Bin-only crate: do not install sources into the cargo registry
%global cargo_install_lib false

# single definition of the desktop-file id (%install/%check/%files)
%global desktop_id ai.storyteller.%{name}

# Release profile strips the binary and vendor sources trip the shebang BRP
%global debug_package %{nil}

# OOM red: distro RUSTFLAGS inject debuginfo and the release
# profile uses thin-LTO + codegen-units=1, so one rustc needs >4 GB;
# relax both
%global build_rustflags -Clink-arg=-Wl,-z,relro,-z,now -C codegen-units=16 -C debuginfo=0

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
FilmCraft is an open-source, native nonlinear video editor with a
multitrack timeline, trimming and ripple edits, color grading with scopes,
audio mixing and effects, titles and captions, and export to common video
formats via its own codec suite.

%prep
%autosetup -p1 -a1
# [patch.crates-io] redirects egui/winit to storytold forks; entries for
# crates outside the dependency graph (egui_demo_lib, egui_inspection,
# egui_system_font_provider) are never vendored, and cargo then fails
# resolving the patch against the vendored source replacement
sed -i -E '/^(egui_demo_lib|egui_inspection|egui_system_font_provider) = \{ git /d' Cargo.toml

%build
# zbus-lockstep's validate macro looks for ../xml relative to the crate
# being compiled: in a vendored tree that resolves to the vendored "xml"
# crate (whose extensionless LICENSE panics the macro) instead of
# atspi-common's D-Bus XML dir. obs-service-cargo_vendor dirs carry a
# version suffix, hence the glob.
lockstep_xml="$(echo vendor/atspi-common-*/xml)"
[ -d "$lockstep_xml" ] && export LOCKSTEP_XML_PATH="$(pwd)/$lockstep_xml"
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
%{cargo_build}

%install
install -Dpm0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

install -Dpm0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

# ship whatever sizes upstream provides (they change between releases)
for icon in assets/app-icon/hicolor/*/apps/*; do
    install -Dpm0644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/${icon#assets/app-icon/hicolor/}"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

%files
%license LICENSE-APACHE LICENSE-MIT NOTICE
%doc README.md
%{_bindir}/filmcraft
%{_datadir}/applications/%{desktop_id}.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/%{desktop_id}.*

%changelog
