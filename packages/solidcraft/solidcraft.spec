# Bin-only crate: do not install sources into the cargo registry
%global cargo_install_lib false

# Release profile strips the binary and vendor sources trip the shebang BRP
%global debug_package %{nil}

# aarch64 OOM red: distro RUSTFLAGS inject debuginfo and the release
# profile uses thin-LTO + codegen-units=1, so one rustc needs >4 GB;
# relax both
%global build_rustflags -Clink-arg=-Wl,-z,relro,-z,now -C codegen-units=16 -C debuginfo=0

ExclusiveArch:  x86_64 aarch64

Name:           solidcraft
Version:        0.40.1
Release:        0
Summary:        Parametric 3D CAD application with sketches, features and assemblies

License:        MIT OR Apache-2.0
URL:            https://github.com/tangency-labs/solidcraft
Source0:        solidcraft-%{version}.tar.zst
Source1:        vendor.tar.zst
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
SolidCraft is an open-source parametric 3D CAD application built in pure
Rust. Sketch on a plane, constrain and dimension the sketch, turn profiles
into solids on an editable feature timeline, and change a parameter to watch
the model rebuild. It reads and writes STEP, IGES, 3MF, STL, OBJ and glTF,
and ships a headless CLI with an MCP server for AI agents.

%prep
%autosetup -p1 -a1

%build
# zbus-lockstep's validate macro resolves ../xml relative to the compiled
# crate: in a vendored tree that lands on the vendored "xml" crate (whose
# extensionless LICENSE panics the macro) instead of atspi-common's D-Bus XML dir
[ -d vendor2/atspi-common/xml ] && export LOCKSTEP_XML_PATH="$(pwd)/vendor2/atspi-common/xml"
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
%{cargo_build}

%install
install -Dpm755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
install -Dpm755 target/release/%{name}-cli %{buildroot}%{_bindir}/%{name}-cli

# upstream renames its app id between releases (ai.storyteller.* ->
# io.tangencylabs.*): ship whatever desktop file linux/platforms carries
desktop_file=$(basename assets/platforms/linux/*.desktop)
install -Dpm644 "assets/platforms/linux/$desktop_file" \
    %{buildroot}%{_datadir}/applications/$desktop_file

# ship whatever sizes upstream provides (they change between releases)
for icon in assets/icons/app/linux/exports/hicolor/*/apps/*; do
    install -Dpm644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/${icon#assets/icons/app/linux/exports/hicolor/}"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop
# headless CLI smoke test (usage text exits 0)
target/release/%{name}-cli --help >/dev/null

%files
%license LICENSE-APACHE LICENSE-MIT NOTICE
%doc README.md
%{_bindir}/solidcraft
%{_bindir}/solidcraft-cli
%{_datadir}/applications/*.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/*

%changelog
