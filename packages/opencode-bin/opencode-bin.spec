%global __os_install_post %{nil}

Name:           opencode-bin
Version:        1.18.15
Release:        0
Summary:        The open source AI coding agent
License:        MIT
URL:            https://github.com/anomalyco/opencode
Source0:        opencode-linux-x64.tar.gz
Source1:        LICENSE
ExclusiveArch:  x86_64

BuildRequires:  tar
Provides:       opencode = %{version}-%{release}
Obsoletes:      opencode < %{version}-%{release}
Recommends:     bash-completion

%description
OpenCode is the open source AI coding agent.

%prep
%setup -T -c -D
tar -xzf %{SOURCE0}

%build

%install
install -Ddm755 %{buildroot}%{_bindir}
install -pm 0755 opencode %{buildroot}%{_bindir}/opencode

./opencode completion bash > opencode.bash
./opencode completion zsh  > _opencode
./opencode completion fish > opencode.fish
install -Dpm 0644 opencode.bash %{buildroot}%{_datadir}/bash-completion/completions/opencode
install -Dpm 0644 _opencode     %{buildroot}%{_datadir}/zsh/site-functions/_opencode
install -Dpm 0644 opencode.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/opencode.fish

install -pm 0644 %{SOURCE1} LICENSE

%files
%license LICENSE
%{_bindir}/opencode
%{_datadir}/bash-completion/completions/opencode
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_opencode
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/opencode.fish

%changelog
