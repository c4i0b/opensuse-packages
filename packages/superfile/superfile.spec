Name:           superfile
Version:        1.6.0
Release:        0
Summary:        Pretty fancy and modern terminal file manager
License:        MIT
URL:            https://github.com/yorukot/superfile
Source0:        superfile-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64 aarch64
BuildRequires:  golang(API) >= 1.25

%description
A pretty fancy and modern terminal file manager written in Go.

%prep
%autosetup -a 1

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -o spf .

%install
install -Dpm 0755 spf %{buildroot}%{_bindir}/spf

%files
%doc README.md
%license LICENSE
%{_bindir}/spf

%changelog
