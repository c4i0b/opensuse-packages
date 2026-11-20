Name:           httpx
Version:        1.12.0
Release:        0
Summary:        Fast and multi-purpose HTTP toolkit
License:        MIT
URL:            https://github.com/projectdiscovery/httpx
Source0:        httpx-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.26

%description
httpx is a fast and multi-purpose HTTP toolkit that allows running multiple
probes using the retryablehttp library. It returns the status code, response
time, title, tech stack, and other information for a list of URLs, with
support for probing over HTTP(S), following redirects, and customizable
output formats.

%prep
%autosetup -a 1
# slowroll's Go lags upstream's go.mod floor (GOTOOLCHAIN=local, offline
# workers); clamp the directive to the buildroot toolchain. A real
# newer-language-feature need still fails loud in `go build` below.
sed -i "s/^go .*/go $(go env GOVERSION | cut -c3-)/" go.mod

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -o httpx ./cmd/httpx

%install
install -Dpm 0755 httpx %{buildroot}%{_bindir}/httpx

%files
%doc README.md
%license LICENSE.md
%{_bindir}/httpx

%changelog
