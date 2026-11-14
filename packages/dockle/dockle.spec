Name:           dockle
Version:        0.4.15
Release:        0
Summary:        Container image linter for security, helping build best-practice Docker images
License:        Apache-2.0
URL:            https://github.com/goodwithtech/dockle
Source0:        dockle-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.22
# vendored containers/storage compiles its btrfs driver (cgo)
BuildRequires:  libbtrfs-devel

%description
Dockle scans container images for security issues and Dockerfile best
practices, including CIS Benchmarks checkpoints. It helps build the Best
Practice Docker Image and is suitable for CI pipelines.

%prep
%autosetup -a 1

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -o dockle ./cmd/dockle

%install
install -Dpm 0755 dockle %{buildroot}%{_bindir}/dockle

%files
%doc README.md CHECKPOINT.md
%license LICENSE
%{_bindir}/dockle

%changelog
