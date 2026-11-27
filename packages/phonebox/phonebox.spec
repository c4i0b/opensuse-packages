# Repackage of the upstream single-file .NET publish: Source0 is the
# official release zip; %install re-bundles the payload under %_libdir with
# a wrapper in %_bindir (rpm-repackage.spec.tpl model, spotube analogue).
# The agent is one 107 MB ELF with the whole .NET 10 runtime and the managed
# payload appended (single-file bundle): the tree is kept byte-identical,
# strip off. Tumbleweed ships no dotnet-sdk and OBS workers are offline, so
# a source build is not possible in this ecosystem today.
%define debug_package %{nil}
%global __strip /bin/true

# %_userunitdir needs systemd-rpm-macros; hardcode once instead
%global userunitdir %{_prefix}/lib/systemd/user

ExclusiveArch:  x86_64

Name:           phonebox
Version:        0.9.31
Release:        0
Summary:        Desktop agent that turns an old Android phone into a desk panel
License:        MIT
URL:            https://github.com/ersinkoc/phonebox
Source0:        https://github.com/ersinkoc/phonebox/releases/download/v%{version}/PhoneBoxAgent-%{version}-linux-x64.zip
Source1:        https://raw.githubusercontent.com/ersinkoc/phonebox/v%{version}/LICENSE

BuildRequires:  unzip

# P/Invoke'd helpers (no DT_NEEDED, so nothing lands in autoreq):
# Now Playing + media controls | wpctl/pactl volume | adb for USB pairing
Recommends:     playerctl
Recommends:     pipewire-utils
Suggests:       pulseaudio-utils
Suggests:       android-tools

%description
PhoneBox pairs a full-screen Android app with a small desktop agent, turning
an old phone into a desk panel: PC stats, AI coding sessions, music, touch
controls and automation over USB or Wi-Fi.

This package ships the Linux desktop agent: a self-contained binary (the
.NET runtime is bundled, no extra runtime packages needed) that serves its settings
at http://127.0.0.1:8765 and runs as a systemd user service:

    systemctl --user enable --now phonebox

The Android app comes from the upstream release page (no RPM scope); GPU
stats additionally use nvidia-smi when an NVIDIA driver is installed.

%prep
%setup -T -q -c
unzip -q %{SOURCE0}
# zip external attrs do not survive %prep: restore the exec bit
chmod +x PhoneBoxAgent
# managed debug symbols: useless outside a debugger, 400 KB
rm -f PhoneBoxAgent.pdb

%build

%install
appdir=%{buildroot}%{_libdir}/phonebox
install -d "$appdir"
cp -a . "$appdir"/

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/phonebox <<EOF
#!/bin/sh
exec %{_libdir}/phonebox/PhoneBoxAgent "\$@"
EOF
chmod 755 %{buildroot}%{_bindir}/phonebox

# mirrors the unit upstream's setup.sh writes, pointed at the packaged binary
install -Dpm644 /dev/null %{buildroot}%{userunitdir}/phonebox.service
cat > %{buildroot}%{userunitdir}/phonebox.service <<EOF
[Unit]
Description=PhoneBox agent (desk panel for an Android phone)
After=graphical-session.target

[Service]
ExecStart=%{_bindir}/phonebox
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

install -pm644 %{SOURCE1} LICENSE

%files
%license LICENSE
%{_bindir}/phonebox
%{_libdir}/phonebox/
%{userunitdir}/phonebox.service

%changelog
