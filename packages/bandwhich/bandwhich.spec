Name:           bandwhich
Version:        0.23.1
Release:        0
Summary:        Terminal bandwidth utilization tool by process, connection and remote IP
License:        MIT
URL:            https://github.com/imsnif/bandwhich
Source0:        bandwhich-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging
BuildRequires:  libpcap-devel

%description
CLI utility for displaying the current network utilization by process,
connection and remote IP/hostname. It sniffs packets on a network interface
(via libpcap), resolves them to the owning processes through /proc, and
renders a live terminal UI with upload/download rates per process,
connection and remote address. Requires root at runtime.

%prep
%autosetup -p1 -a1

%build
# build.rs writes the manpage and shell completions to this dir (it falls
# back to OUT_DIR otherwise, which is a moving target); it never mkdirs it
export BANDWHICH_GEN_DIR="${PWD}/gen"
mkdir -p "${BANDWHICH_GEN_DIR}"
%{cargo_build}

%install
install -Dpm 0755 target/release/bandwhich %{buildroot}%{_bindir}/bandwhich
install -Dpm 0644 gen/bandwhich.1 %{buildroot}%{_mandir}/man1/bandwhich.1
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions %{buildroot}%{_datadir}/zsh/site-functions %{buildroot}%{_datadir}/fish/vendor_completions.d
install -pm 0644 gen/bandwhich.bash %{buildroot}%{_datadir}/bash-completion/completions/bandwhich
install -pm 0644 gen/_bandwhich %{buildroot}%{_datadir}/zsh/site-functions/_bandwhich
install -pm 0644 gen/bandwhich.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/bandwhich.fish

%files
%license LICENSE.md
%doc CHANGELOG.md README.md
%{_bindir}/bandwhich
%{_mandir}/man1/bandwhich.1%{?ext_man}
%{_datadir}/bash-completion/completions/bandwhich
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_bandwhich
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/bandwhich.fish

%changelog
