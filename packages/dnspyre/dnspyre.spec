Name:           dnspyre
Version:        3.12.0
Release:        0
Summary:        High performance DNS benchmark tool
License:        MIT
URL:            https://github.com/Tantalor93/dnspyre
Source0:        dnspyre-%{version}.tar.gz
Source1:        vendor.tar.gz
# %{go_arches} is NOT defined in Tumbleweed's prjconf anymore: an empty
# expansion makes OBS exclude every arch. List the arches explicitly.
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.25

%description
dnspyre is a high performance DNS benchmark tool written in Go. It sends DNS
queries to a server at a configurable rate and reports latency percentiles,
throughput, timing and error statistics, with support for TCP, DoT, DoH and
DoQ transports and cached vs non-cached response measurement.

# -a 1 unpacks Source1 (vendor/) into the same dir as Source0.
%prep
%autosetup -a 1

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -ldflags "-X 'github.com/tantalor93/dnspyre/v3/cmd.Version=%{version}'" -o dnspyre .

./dnspyre completion bash > dnspyre.bash
./dnspyre completion zsh  > _dnspyre
./dnspyre completion fish > dnspyre.fish

%install
install -Dpm 0755 dnspyre %{buildroot}%{_bindir}/dnspyre
install -Dpm644 dnspyre.bash %{buildroot}%{_datadir}/bash-completion/completions/dnspyre
install -Dpm644 _dnspyre %{buildroot}%{_datadir}/zsh/site-functions/_dnspyre
install -Dpm644 dnspyre.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/dnspyre.fish

%files
%doc README.md
%license LICENSE
%{_bindir}/dnspyre
%{_datadir}/bash-completion/completions/dnspyre
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_dnspyre
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/dnspyre.fish

%changelog
