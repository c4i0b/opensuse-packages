Name:           superfile-bin
Version:        1.6.0
Release:        0
Summary:        Pretty fancy and modern terminal file manager
License:        MIT
URL:            https://github.com/yorukot/superfile
Source0:        superfile-linux-v1.6.0-amd64.tar.gz
ExclusiveArch:  x86_64

%description
A pretty fancy and modern terminal file manager written in Go.

%prep
%setup -T -c -D
tar -xzf %{SOURCE0}

%build

%install
install -Dpm 0755 dist/superfile-linux-v1.6.0-amd64/spf %{buildroot}%{_bindir}/spf

%files
%{_bindir}/spf

%changelog
