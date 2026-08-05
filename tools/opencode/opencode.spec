Name:           opencode
Version:        1.18.13
Release:        0
Summary:        Open source AI coding agent
License:        MIT
URL:            https://opencode.ai
Source0:        opencode-linux-x64.tar.gz
ExclusiveArch:  x86_64

%global debug_package %{nil}

%description
OpenCode is the open source AI coding agent. This package ships the upstream
prebuilt x86_64 binary.

%prep
%setup -T -c -D

%build

%install
install -Ddm755 %{buildroot}%{_bindir}
tar -xzf %{SOURCE0}
install -pm 0755 opencode %{buildroot}%{_bindir}/opencode

%files
%{_bindir}/opencode

%changelog
