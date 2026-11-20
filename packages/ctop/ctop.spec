Name:           ctop
Version:        0.7.7
Release:        0
Summary:        Top-like interface for container metrics
License:        MIT
URL:            https://github.com/bcicen/ctop
Source0:        ctop-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.18

%description
ctop provides a concise and condensed overview of real-time container
metrics (CPU, memory, network) in a top-like terminal interface. It
supports Docker, runC, and containerd backends, with filtering, sorting,
and a per-container log and inspect view.

%prep
%autosetup -a 1
# slowroll's Go lags upstream's go.mod floor (GOTOOLCHAIN=local, offline
# workers); clamp the directive to the buildroot toolchain. A real
# newer-language-feature need still fails loud in `go build` below.
gover="$(go env GOVERSION | cut -c3-)"
sed -i "s/^go .*/go $gover/" go.mod
# deps' floors in vendor/modules.txt are checked too; clamp them as well
sed -i -E "s/^(## (explicit; )?)go .*/\1go $gover/" vendor/modules.txt

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -o ctop .

%install
install -Dpm 0755 ctop %{buildroot}%{_bindir}/ctop

%files
%doc README.md
%license LICENSE
%{_bindir}/ctop

%changelog
