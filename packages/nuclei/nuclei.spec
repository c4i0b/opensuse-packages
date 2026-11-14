Name:           nuclei
Version:        3.11.1
Release:        0
Summary:        Fast and customizable vulnerability scanner based on simple YAML based DSL
License:        MIT
URL:            https://github.com/projectdiscovery/nuclei
Source0:        nuclei-%{version}.tar.gz
Source1:        vendor.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  golang(API) >= 1.26

%description
Nuclei is a fast, customizable vulnerability scanner powered by a simple
YAML-based DSL. It supports prototyping, reconnaissance, fuzzing and
scanning across templates for DNS, files, HTTP, TCP and more, with
community-driven template collaboration.

%prep
%autosetup -a 1

%build
export GOFLAGS="-buildmode=pie"
# upstream main package lives in cmd/nuclei, not the repo root
go build -mod=vendor -o nuclei ./cmd/nuclei

%install
install -Dpm 0755 nuclei %{buildroot}%{_bindir}/nuclei

%files
%doc README.md
%license LICENSE.md
%{_bindir}/nuclei

%changelog
