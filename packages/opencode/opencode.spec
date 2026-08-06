%global debug_package %{nil}
# bun build --compile appends the OpenCode payload to a Bun runtime ELF; GNU
# strip removes the payload, leaving a plain Bun CLI. Same rule as the
# prebuilt opencode-bin: skip all brp post-install processing.
%global __os_install_post %{nil}

Name:           opencode
Version:        1.18.14
Release:        0
Summary:        The open source AI coding agent
License:        MIT
URL:            https://github.com/anomalyco/opencode
Source0:        %{name}-%{version}.tar.gz
Source1:        vendor-node_modules.tar.zst
Source2:        bun-linux-x64.zip
Source3:        models-api.json
ExclusiveArch:  x86_64

BuildRequires:  tar
BuildRequires:  unzip
BuildRequires:  zstd
Requires:       git-core
Requires:       ripgrep

%description
OpenCode is the open source AI coding agent.

Source build: compiled from the opencode upstream repository using the
bundled Bun runtime and included package dependencies.

%prep
%setup -q -n %{name}-%{version}
zstd -dc %{SOURCE1} | tar -x

%build
mkdir -p %{_builddir}/bun
unzip -q %{SOURCE2} -d %{_builddir}/bun
export PATH=%{_builddir}/bun/bun-linux-x64:$PATH
export OPENCODE_VERSION=%{version}
export OPENCODE_CHANNEL=latest
export MODELS_DEV_API_JSON=%{SOURCE3}
bun ./packages/opencode/script/build.ts --single --skip-install

%install
install -Dpm 0755 packages/opencode/dist/opencode-linux-x64/bin/opencode %{buildroot}%{_bindir}/opencode

%check
test "$(%{buildroot}%{_bindir}/opencode --version)" = "%{version}"

%files
%license LICENSE
%{_bindir}/opencode

%changelog
