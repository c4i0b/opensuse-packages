Name:           rathole
Version:        0.5.0
Release:        0
Summary:        Lightweight and high-performance reverse proxy for NAT traversal
License:        Apache-2.0
URL:            https://github.com/rathole-org/rathole
Source0:        rathole-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging
# tokio-native-tls links the system OpenSSL
BuildRequires:  openssl-devel

%description
A secure, stable and high-performance reverse proxy for NAT traversal,
written in Rust and similar to frp and ngrok. It exposes services on
devices behind a NAT via a server with a public IP, with mandatory
per-service tokens and optional Noise Protocol or TLS encryption,
websocket transport and configuration hot-reloading.

%prep
%autosetup -p1 -a1

%build
# OOM mitigation (docs/packaging/rust.md): upstream release profile
# is fat-LTO with codegen-units=1
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
%{cargo_build}

%install
install -Dpm 0755 target/release/rathole %{buildroot}%{_bindir}/rathole

%check
%{buildroot}%{_bindir}/rathole --version

%files
%license LICENSE
%doc README.md
%{_bindir}/rathole

%changelog
