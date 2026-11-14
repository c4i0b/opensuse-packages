# Bin-only crate: do not install sources into the cargo registry
%global cargo_install_lib false

# single definition of the desktop-file id (%install/%check/%files)
%global desktop_id ai.storyteller.%{name}

# OOM red: distro RUSTFLAGS inject debuginfo and the release
# profile uses thin-LTO + codegen-units=1, so one rustc needs >4 GB;
# relax both
%global build_rustflags -Clink-arg=-Wl,-z,relro,-z,now -C codegen-units=16 -C debuginfo=0

# Release profile strips the binary and vendor sources trip the shebang BRP
%global debug_package %{nil}

ExclusiveArch:  x86_64

Name:           wordcraft
Version:        0.18.1
Release:        0
Summary:        Word processor with docx support, track changes and mail merge

License:        MIT OR Apache-2.0
URL:            https://github.com/storytold/wordcraft
Source0:        wordcraft-%{version}.tar.zst
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
WordCraft is an open-source, pure-Rust word processor with a familiar
workflow: the ribbon, styles, tables, track changes, references and mail
merge. It reads and writes .docx documents and runs natively on Linux.

%prep
%autosetup -p1 -a1

# cargo eagerly validates every [patch.crates-io] git entry against its
# source: crates outside the dependency graph are never vendored and the
# offline build dies on them — drop patch lines with no vendor/ crate dir
for crate in $(awk '/^\[patch\.crates-io\]/{f=1;next} /^\[/{f=0} f && /= \{ git/{print $1}' Cargo.toml); do
    ls -d vendor/"$crate"-* >/dev/null 2>&1 || sed -i "/^$crate = { git = /d" Cargo.toml
done

%build
# zbus-lockstep's validate macro looks for ../xml relative to the crate
# being compiled: in a vendored tree that resolves to the vendored "xml"
# crate (whose extensionless LICENSE panics the macro) instead of
# atspi-common's D-Bus XML dir
[ -d vendor/atspi-common/xml ] && export LOCKSTEP_XML_PATH="$(pwd)/vendor/atspi-common/xml"
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
%{cargo_build}

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
%{_bindir}/wordcraft
%{_datadir}/applications/%{desktop_id}.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/%{desktop_id}.*

%changelog
