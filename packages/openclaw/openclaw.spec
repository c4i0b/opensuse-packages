# npm-bundle model: official npm tarball + offline dependency install.
# node_modules.spec.inc lists the dependency tarballs as Source10000+
# registry URLs (flat rename) that the download_files _service fetches
# server-side; local-npm-registry then serves them to npm as a localhost
# registry — OBS build workers are offline.
Name:           openclaw
Version:        2026.11.3
Release:        0
Summary:        OpenClaw CLI, a personal AI assistant (npm bundle)
License:        MIT
URL:            https://github.com/openclaw/openclaw
Source0:        openclaw-%{version}.tgz
Source10:       package-lock.json
Source11:       node_modules.spec.inc
%include %_sourcedir/node_modules.spec.inc
BuildArch:      noarch

BuildRequires:  nodejs24
BuildRequires:  npm-default
BuildRequires:  local-npm-registry
Requires:       nodejs24

# env-node shebangs across the npm payload would be mangled to a nonexistent
# /usr/bin/node interpreter; /usr/bin/openclaw is the entrypoint and calls
# node24 directly
%global __brp_mangle_shebangs %{nil}

%description
OpenClaw is a personal AI assistant you run on your own devices: one agent,
persistent memory, and the channels you already use. This package ships the
official npm bundle with the openclaw CLI.

%prep
%autosetup -n package
# local-npm-registry serves the dependency tarballs (Source10000+,
# fetched server-side into %{_sourcedir} by the download_files service)
# as a local npm registry — OBS build workers are offline.
# --legacy-peer-deps: mistralai pins a conflicting peerOptional;
# --omit=optional drops the arch-specific fs-safe native addon (noarch)
local-npm-registry %{_sourcedir} install \
    --omit=dev --omit=optional --ignore-scripts \
    --no-audit --no-fund --legacy-peer-deps

%build
# Complete the postinstall lifecycle marker in-tree so users never trigger it
export HOME=%{_builddir}
OPENCLAW_FS_SAFE_NATIVE_MODE=off node24 ./openclaw.mjs --version

%install
install -d -m755 %{buildroot}%{_prefix}/lib/node_modules/openclaw
cp -a . %{buildroot}%{_prefix}/lib/node_modules/openclaw/
# The shipped lifecycle marker makes the CLI run postinstall scripts inside
# this (root-owned) tree on first run; completion above only happens when the
# chroot runtime passes the >=24.16 admission, so drop it unconditionally
rm -f %{buildroot}%{_prefix}/lib/node_modules/openclaw/.openclaw-lifecycle-pending

# Upstream tree ships arch payloads: prebuilt binaries in skills/, wasm and
# per-platform dirs in node_modules; drop them all to keep the payload noarch
find %{buildroot}%{_prefix}/lib/node_modules/openclaw -type f \
    -exec sh -c 'file -b "$1" | grep -qE "ELF|Mach-O|PE32|WebAssembly" && rm -f "$1"' _ {} \;
for plat in linux-arm64 linux-x64 linux-ia32 darwin-arm64 darwin-x64 win32-arm64 win32-x64; do
    find %{buildroot}%{_prefix}/lib/node_modules/openclaw -type d -name "$plat" \
        -exec rm -rf {} +
done

install -Dpm755 /dev/null %{buildroot}%{_bindir}/openclaw
cat > %{buildroot}%{_bindir}/openclaw <<'EOF'
#!/bin/sh
exec /usr/bin/node24 %{_prefix}/lib/node_modules/openclaw/openclaw.mjs "$@"
EOF

%check
# Invoke node24 directly: the wrapper hardcodes the installed path
HOME=%{_builddir} OPENCLAW_FS_SAFE_NATIVE_MODE=off \
    node24 %{buildroot}%{_prefix}/lib/node_modules/openclaw/openclaw.mjs --version

%files
%license LICENSE
%doc README.md
%{_bindir}/openclaw
%dir %{_prefix}/lib/node_modules
%{_prefix}/lib/node_modules/openclaw/

%changelog
