Name:           lazydocker
Version:        0.25.2
Release:        0
Summary:        Simple terminal UI for docker and docker-compose
License:        MIT
URL:            https://github.com/jesseduffield/lazydocker
Source0:        lazydocker-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64 aarch64
BuildRequires:  golang(API) >= 1.22

%description
A simple terminal UI for both docker and docker-compose, written in Go with
the gocui library: inspect and manage containers, images, volumes, and
services without leaving the keyboard.

%prep
%autosetup -a 1

%build
export GOFLAGS="-buildmode=pie"
go build -mod=vendor -o lazydocker .

%install
install -Dpm 0755 lazydocker %{buildroot}%{_bindir}/lazydocker

%files
%doc README.md
%license LICENSE
%{_bindir}/lazydocker

%changelog
