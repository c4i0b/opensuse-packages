ExclusiveArch:  x86_64

Name:           pdfcraft
Version:        0.21.1
Release:        0
Summary:        PDF reader and editor with annotations, forms and signing

License:        MIT OR Apache-2.0
URL:            https://github.com/storytold/pdfcraft
Source0:        pdfcraft-%{version}.tar.zst
Source1:        vendor.tar.zst
Source2:        %{name}.desktop

BuildRequires:  cargo-packaging
BuildRequires:  gcc
# aws-lc-sys (via rustls, from pdfcraft-sign) builds C with cmake; no bindgen
# users in the app's tree, so no clang-devel needed
BuildRequires:  cmake
BuildRequires:  desktop-file-utils

# OOM red: distro RUSTFLAGS inject debuginfo and the release
# profile uses thin-LTO + codegen-units=1, so one rustc needs >4 GB;
# relax both
%global build_rustflags -Clink-arg=-Wl,-z,relro,-z,now -C codegen-units=16 -C debuginfo=0

# Bin-only crate: do not install sources into the cargo registry
%global cargo_install_lib false

# single definition of the desktop-file id (%install/%check/%files)
%global desktop_id ai.storyteller.%{name}

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
PdfCraft is a pure-Rust PDF reader and editor with an egui-based workspace.
It opens and edits PDF documents with page organize (merge, split, rotate),
annotations, form filling, redaction, digital signing and certification,
OCR, preflight audits, and encryption with granular permissions.

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
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
%{__cargo} build %{?_smp_mflags} --offline --release -p %{name}

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

install -Dpm 0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

# ship whatever sizes upstream provides (they change between releases)
for icon in assets/app-icon/hicolor/*/apps/*; do
    install -Dpm 0644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/${icon#assets/app-icon/hicolor/}"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

%files
%license LICENSE-APACHE LICENSE-MIT NOTICE
%doc README.md
%{_bindir}/pdfcraft
%{_datadir}/applications/%{desktop_id}.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/%{desktop_id}.*

%changelog
