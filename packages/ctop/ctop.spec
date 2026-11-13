Name:           ctop
Version:        0.7.7
Release:        0
Summary:        Top-like interface for container metrics
License:        MIT
URL:            https://github.com/bcicen/ctop
Source0:        ctop-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64 aarch64
BuildRequires:  golang(API) >= 1.18

%description
ctop provides a concise and condensed overview of real-time container
metrics (CPU, memory, network) in a top-like terminal interface. It
supports Docker, runC, and containerd backends, with filtering, sorting,
and a per-container log and inspect view.

%prep
%autosetup -a 1

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
