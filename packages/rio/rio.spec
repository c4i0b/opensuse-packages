%global cargo_install_lib false

# OOM mitigation: relax distro debuginfo + thin-LTO defaults
%global build_rustflags -Clink-arg=-Wl,-z,relro,-z,now -C codegen-units=16 -C debuginfo=0

%global debug_package %{nil}

ExclusiveArch:  x86_64

Name:           rio
Version:        0.5.30
Release:        0
Summary:        Hardware-accelerated terminal emulator built with Rust
License:        MIT
URL:            https://github.com/raphamorim/rio
Source0:        rio-%{version}.tar.zst
Source1:        vendor.tar.zst

BuildRequires:  cargo-packaging
BuildRequires:  gcc-c++
BuildRequires:  desktop-file-utils
# sugarloof compiles its GLSL shaders to SPIR-V at build time (glslc
# preferred, glslangValidator fallback — on Tumbleweed the validator ships
# in glslang-devel)
BuildRequires:  glslang-devel
# font-kit probes system libraries via pkg-config instead of bundling
BuildRequires:  pkg-config
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
# tic (terminfo compiler) for misc/rio.terminfo — the ncurses tools ship in
# the -devel package on openSUSE
BuildRequires:  ncurses-devel

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
Rio is a hardware-accelerated terminal emulator built on the wgpu graphics
API, focusing on performance and simplicity. It supports Wayland and X11,
ligatures, and configuration via TOML.

%prep
%autosetup -p1 -a1

%build
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
# default features only: wayland + x11 backends; no --all-features (pulls
# audio deps a terminal does not need)
# upstream pins rustc 1.99.1 while Tumbleweed ships 1.99.0 (patch delta,
# no 1.99.1-only feature is used); drop the flag when the distro catches up
%{cargo_build} -p rioterm --ignore-rust-version

%install
install -Dpm 0755 target/release/rio %{buildroot}%{_bindir}/rio

install -Dpm 0644 misc/rio.desktop \
  %{buildroot}%{_datadir}/applications/rio.desktop
install -Dpm 0644 misc/com.rioterm.Rio.metainfo.xml \
  %{buildroot}%{_datadir}/metainfo/com.rioterm.Rio.metainfo.xml
install -Dpm 0644 misc/logo.svg \
  %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/rio.svg
tic -x -o %{buildroot}%{_datadir}/terminfo misc/rio.terminfo

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/rio.desktop
target/release/rio --version

%files
%license LICENSE
%doc README.md
%{_bindir}/rio
%{_datadir}/applications/rio.desktop
%{_datadir}/metainfo/com.rioterm.Rio.metainfo.xml
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/scalable/apps/rio.svg
%dir %{_datadir}/terminfo
%dir %{_datadir}/terminfo/r
%{_datadir}/terminfo/r/*
%dir %{_datadir}/terminfo/x
%{_datadir}/terminfo/x/xterm-rio

%changelog
