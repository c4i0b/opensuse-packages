# Bin-only crate: do not install sources into the cargo registry
%global cargo_install_lib false

# single definition of the desktop-file id (%install/%check/%files)
%global desktop_id ai.storyteller.%{name}

# Release profile strips the binary and vendor sources trip the shebang BRP
%global debug_package %{nil}

# aarch64 OOM red: distro RUSTFLAGS inject debuginfo and the release
# profile uses thin-LTO + codegen-units=1, so one rustc needs >4 GB;
# relax both
%global build_rustflags -Clink-arg=-Wl,-z,relro,-z,now -C codegen-units=16 -C debuginfo=0

ExclusiveArch:  x86_64 aarch64

Name:           soundcraft
Version:        0.20.1
Release:        0
Summary:        Digital audio workstation with multitrack editing, mixer and MIDI

License:        MIT OR Apache-2.0
URL:            https://github.com/storytold/soundcraft
Source0:        soundcraft-%{version}.tar.zst
Source1:        vendor.tar.zst
Source2:        %{name}.desktop
BuildRequires:  cargo-packaging
BuildRequires:  gcc
# cpal -> alsa -> alsa-sys resolves libasound via pkg-config
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
SoundCraft is an open-source digital audio workstation built in pure Rust.
It offers multitrack recording and editing, a full mixer with plugins, sends
and automation, MIDI sequencing, bouncing, and scriptability from the command
line or by an AI agent.

%prep
%autosetup -p1 -a1

# cargo eagerly validates every [patch.crates-io] git entry against its
# source: crates outside the dependency graph are never vendored and the
# offline build dies on them — drop patch lines with no vendor/ crate dir
for crate in $(awk '/^\[patch\.crates-io\]/{f=1;next} /^\[/{f=0} f && /= \{ git/{print $1}' Cargo.toml); do
    ls -d vendor/"$crate"-* >/dev/null 2>&1 || sed -i "/^$crate = { git = /d" Cargo.toml
done

%build
# zbus-lockstep's validate macro resolves ../xml relative to the compiled
# crate: in a vendored tree that lands on the vendored "xml" crate (whose
# extensionless LICENSE panics the macro) instead of atspi-common's D-Bus XML dir
[ -d vendor/atspi-common/xml ] && export LOCKSTEP_XML_PATH="$(pwd)/vendor/atspi-common/xml"
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
%{cargo_build}

%install
install -Dpm755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

install -Dpm644 %{SOURCE2} %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

# ship whatever sizes upstream provides (they change between releases)
for icon in assets/app-icon/hicolor/*/apps/*; do
    install -Dpm644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/${icon#assets/app-icon/hicolor/}"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{desktop_id}.desktop

%files
%license LICENSE-APACHE LICENSE-MIT NOTICE
%doc README.md
%{_bindir}/soundcraft
%{_datadir}/applications/%{desktop_id}.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/%{desktop_id}.*

%changelog
