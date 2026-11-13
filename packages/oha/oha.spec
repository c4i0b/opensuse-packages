Name:           oha
Version:        1.16.0
Release:        0
Summary:        Tiny HTTP load generator, inspired by rakyll/hey with tui animation
License:        MIT
URL:            https://github.com/hatoo/oha
Source0:        oha-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging
# aws-lc-sys (rustls default crypto provider) builds via cmake
BuildRequires:  cmake

%description
oha is a tiny program that sends some load to a web application and shows
realtime tui, inspired by rakyll/hey. It is written in Rust, powered by tokio,
and supports HTTP/2, connections limits, latency distributions, and a live
chart of the response times while the load runs.

%prep
%autosetup -p1 -a1

%build
%{cargo_build}

%install
install -Dpm 0755 target/release/oha %{buildroot}%{_bindir}/oha
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions %{buildroot}%{_datadir}/zsh/site-functions %{buildroot}%{_datadir}/fish/vendor_completions.d
target/release/oha --completions bash > %{buildroot}%{_datadir}/bash-completion/completions/oha
target/release/oha --completions zsh  > %{buildroot}%{_datadir}/zsh/site-functions/_oha
target/release/oha --completions fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/oha.fish

%files
%license LICENSE
%doc CHANGELOG.md README.md
%{_bindir}/oha
%{_datadir}/bash-completion/completions/oha
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_oha
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/oha.fish

%changelog
