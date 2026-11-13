Name:           cloudflare-speed-cli
Version:        1.0.12
Release:        0
Summary:        Cloudflare-based internet speed test with optional TUI
License:        GPL-3.0-only
URL:            https://github.com/kavehtehrani/cloudflare-speed-cli
Source0:        cloudflare-speed-cli-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging

%description
Internet speed test against Cloudflare's speed test endpoints: download and
upload throughput, idle and loaded latency, UDP quality (loss, jitter, MOS),
DNS and TLS timing, traceroute and proxy support. Renders a live ratatui TUI,
with headless --text/--json modes for scripting.

%prep
%autosetup -p1 -a1

%build
%{cargo_build}

%install
install -Dpm 0755 target/release/cloudflare-speed-cli %{buildroot}%{_bindir}/cloudflare-speed-cli

%files
%license LICENSE
%doc README.md
%{_bindir}/cloudflare-speed-cli

%changelog
