# Bun-compiled standalone binary: OBS brp-strip removes the ELF section the
# appended JS payload hangs from, and the binary silently falls back to the
# Bun CLI at runtime — install-post stripping must be off
%global __os_install_post %{nil}

ExclusiveArch:  x86_64 aarch64

Name:           omo
Version:        5.1.69
Release:        0
Summary:        AI agent harness with multi-model orchestration and memory
License:        SUL-1.0
URL:            https://github.com/code-yeongyu/oh-my-openagent
Source0:        https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/v%{version}/LICENSE.md
Source1:        https://github.com/code-yeongyu/oh-my-openagent/releases/download/v%{version}/omo-linux-x64
Source2:        https://github.com/code-yeongyu/oh-my-openagent/releases/download/v%{version}/omo-linux-arm64

%description
OmO turns prompts into finished work: one "omo" command with multi-model
orchestration, parallel agents, persistent memory and a large skill library.
Standalone binary embedding the Bun runtime and its agent engine.

%prep
%setup -T -q -c

%build

%install
%ifarch x86_64
install -Dpm755 %{SOURCE1} %{buildroot}%{_bindir}/omo
%else
install -Dpm755 %{SOURCE2} %{buildroot}%{_bindir}/omo
%endif
install -Dpm644 %{SOURCE0} LICENSE.md

%check
# First run writes ~/.omo; keep it off the buildroot filesystem
HOME=%{_builddir}/omo-home %{buildroot}%{_bindir}/omo --version

%files
%license LICENSE.md
%{_bindir}/omo

%changelog
