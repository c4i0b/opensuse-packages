# Bin-only crate: do not install sources into the cargo registry
%global cargo_install_lib false

# Release profile strips the binary and vendor sources trip the shebang BRP
%global debug_package %{nil}

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
# [patch.crates-io] pins the whole egui fork workspace, but cargo vendor only
# emits crates that are actually depended on: patch locations for the rest
# fail to resolve offline, so drop the entries with no vendored crate
while read -r crate; do
    ls vendor | grep -q "^${crate}" || sed -i "/^${crate} = { git =/d" Cargo.toml
done < <(awk '/^\[patch.crates-io\]/{f=1;next} /^\[/{f=0} f && /=/ {print $1}' Cargo.toml)

%build
# zbus-lockstep's validate macro resolves ../xml relative to the compiled
# crate: in a vendored tree that lands on the vendored "xml" crate (whose
# extensionless LICENSE panics the macro) instead of atspi-common's D-Bus XML dir
[ -d vendor/atspi-common/xml ] && export LOCKSTEP_XML_PATH="$(pwd)/vendor/atspi-common/xml"
%{cargo_build}

%install
install -Dpm755 target/release/%{name} %{buildroot}%{_bindir}/%{name}

install -Dpm644 %{SOURCE2} %{buildroot}%{_datadir}/applications/ai.storyteller.soundcraft.desktop

# ship whatever sizes upstream provides (they change between releases)
for icon in assets/app-icon/hicolor/*/apps/*; do
    install -Dpm644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/${icon#assets/app-icon/hicolor/}"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/ai.storyteller.soundcraft.desktop

%files
%license LICENSE-APACHE LICENSE-MIT NOTICE
%doc README.md
%{_bindir}/soundcraft
%{_datadir}/applications/ai.storyteller.soundcraft.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/ai.storyteller.soundcraft.*

%changelog
