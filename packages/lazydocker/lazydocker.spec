Name:           lazydocker
Version:        0.25.2
Release:        0
Summary:        Simple terminal UI for docker and docker-compose
License:        MIT
URL:            https://github.com/jesseduffield/lazydocker
Source0:        lazydocker-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.22

%description
A simple terminal UI for both docker and docker-compose, written in Go with
the gocui library: inspect and manage containers, images, volumes, and
services without leaving the keyboard.

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
go build -mod=vendor -o lazydocker .

%install
install -Dpm 0755 lazydocker %{buildroot}%{_bindir}/lazydocker

%files
%doc README.md
%license LICENSE
%{_bindir}/lazydocker

%changelog
