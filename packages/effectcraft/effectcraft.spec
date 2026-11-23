# Bin-only crate: nothing is installed into the cargo registry
%global cargo_install_lib false

# single definition of the desktop-file id (%install/%check/%files)
%global desktop_id ai.storyteller.%{name}
# release build carries no debuginfo; the empty -debuginfo would fail checks
%global debug_package %{nil}

# OOM red: distro RUSTFLAGS inject debuginfo and the release
# profile uses thin-LTO + codegen-units=1, so one rustc needs >4 GB;
# relax both
%global build_rustflags -Clink-arg=-Wl,-z,relro,-z,now -C codegen-units=16 -C debuginfo=0

ExclusiveArch:  x86_64

Name:           effectcraft
Version:        0.25.1
Release:        0
Summary:        Motion graphics and compositing tool
License:        MIT OR Apache-2.0
URL:            https://github.com/storytold/effectcraft
Source0:        effectcraft-%{version}.tar.zst
Source1:        vendor.tar.zst
Source2:        %{name}.desktop

BuildRequires:  cargo-packaging
# cpal's ALSA backend builds alsa-sys, resolved via pkg-config
BuildRequires:  pkgconfig(alsa)
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
EffectCraft is an open-source, native motion graphics and compositing
application with a keyframe timeline, layer-based compositing, GPU rendering,
expressions and scriptable effects. It imports and exports video through
pure-Rust codecs and reads Lottie, SVG, PSD and PDF assets.

%prep
%autosetup -p1 -a1

%build
# zbus-lockstep's validate macro looks for ../xml relative to the crate
# being compiled: in a vendored tree that resolves to the vendored "xml"
# crate instead of atspi-common's D-Bus XML dir, so point it there
# explicitly (overlay layout: vendor-deps/, pinvendor pre-cleans the
# patched Cargo.toml that -a1 unpacks over the source)
[ -d vendor-deps/atspi-common/xml ] && export LOCKSTEP_XML_PATH="$(pwd)/vendor-deps/atspi-common/xml"
# select the workspace member via a direct cargo call (the cargo_packaging
# build macro is parametric and rejects option letters like -p); plain
# cargo also honors the overlay's .cargo/config.toml source replacement,
# which the packaging macro does not (pdfcraft red)
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
%{__cargo} build %{?_smp_mflags} --offline --release -p %{name}

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

install -Dpm 0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

# ship whatever sizes upstream provides (they change between releases)
for icon in assets/app-icon/hicolor/*/apps/*.png assets/app-icon/hicolor/*/apps/*.svg; do
    [ -e "$icon" ] || continue
    install -Dpm 0644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/${icon#assets/app-icon/hicolor/}"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

%files
%license LICENSE-APACHE LICENSE-MIT NOTICE
%doc README.md
%{_bindir}/effectcraft
%{_datadir}/applications/%{desktop_id}.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/%{desktop_id}.*

%changelog
