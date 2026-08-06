Name:           superfile
Version:        1.6.0
Release:        0
Summary:        Pretty fancy and modern terminal file manager
License:        MIT
URL:            https://github.com/yorukot/superfile
Source0:        superfile-%{version}.tar.gz
Source1:        vendor.tar.gz
BuildRequires:  golang(API) >= 1.25

%description
A pretty fancy and modern terminal file manager written in Go.

%prep
%autosetup -a 1

%build
GOFLAGS="-buildmode=pie" go build -o bin/spf

%install
install -Dpm 0755 bin/spf %{buildroot}%{_bindir}/spf

%files
%{_bindir}/spf

%changelog
