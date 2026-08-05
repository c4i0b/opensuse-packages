Name:           opencode
Version:        1.18.13
Release:        0
Summary:        Launcher that runs the OpenCode container image via podman
License:        MIT
URL:            https://opencode.ai
Source0:        opencode.sh
BuildArch:      noarch
Requires:       podman

%description
opencode installs a /usr/bin/opencode launcher that runs the OpenCode AI
coding agent from its companion container image using podman. The agent
binary ships in the container image, not in this package.

%prep
%setup -T -c -D

%build

%install
install -Dpm 0755 %{SOURCE0} %{buildroot}%{_bindir}/opencode

%files
%{_bindir}/opencode

%changelog
