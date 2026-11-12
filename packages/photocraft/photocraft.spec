ExclusiveArch:  x86_64 aarch64

Name:           photocraft
Version:        0.23.1
Release:        0
Summary:        Photo editor with layers, masks and PSD support

License:        MIT OR Apache-2.0
URL:            https://github.com/storytold/photocraft
Source0:        photocraft-%{version}.tar.zst
Source1:        vendor.tar.zst
Source2:        %{name}.desktop

BuildRequires:  cargo-packaging
BuildRequires:  gcc
# aws-lc-sys (via rustls) and craft-print build C/C++ with cmake; pipewire-sys
# runs bindgen, which needs libclang
BuildRequires:  cmake
BuildRequires:  clang-devel
BuildRequires:  desktop-file-utils

# aarch64 OBS workers OOM linking the upstream release profile (thin-LTO,
# codegen-units=1) with the debuginfo the packaging flags inject; relax both
%global build_rustflags %{nil}

# Bin-only crate: do not install sources into the cargo registry
%global cargo_install_lib false

# aws-lc-sys (via rustls) rejects -O2
%global build_cflags %(echo "%{build_cflags}" | sed 's/ *-O2//g')

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
PhotoCraft is an open-source, native image editor with layers, masks,
adjustment layers, layer styles, type and brushes. It opens and saves layered
PSD/PSB documents, supports 8/16/32-bit float documents in RGB, grayscale,
CMYK and Lab, and a GPU compositor with multithreaded filters.

%prep
%autosetup -p1 -a1

%build
# zbus-lockstep's validate macro looks for ../xml relative to the crate
# being compiled: in a vendored tree that resolves to the vendored "xml"
# crate (whose extensionless LICENSE panics the macro) instead of
# atspi-common's D-Bus XML dir; vendored in vendor-deps (upstream's own
# patched path-dep crates live in vendor/)
[ -d vendor-deps/atspi-common/xml ] && export LOCKSTEP_XML_PATH="$(pwd)/vendor-deps/atspi-common/xml"
# the cargo_packaging build macro is parametric and rejects option letters
# (-p), so select the workspace member via a direct cargo call (same
# env/profile wiring)
# relax the memory-hungry release profile (see build_rustflags note above)
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
%{__cargo} build %{?_smp_mflags} --offline --release -p %{name}

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

install -Dpm 0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/ai.storyteller.photocraft.desktop

# ship whatever sizes upstream provides (they change between releases)
for icon in assets/app-icon/hicolor/*/apps/*; do
    install -Dpm 0644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/${icon#assets/app-icon/hicolor/}"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/ai.storyteller.photocraft.desktop

%files
%license LICENSE-APACHE LICENSE-MIT NOTICE
%doc README.md
%{_bindir}/photocraft
%{_datadir}/applications/ai.storyteller.photocraft.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/ai.storyteller.photocraft.*

%changelog
