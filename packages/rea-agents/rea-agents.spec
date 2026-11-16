# npm-bundle model: official npm tarball + offline dependency install.
# The dependency closure travels as node_modules.obscpio, which the OBS
# worker auto-unpacks flat into %{_sourcedir} (cockpit legacy-container
# model); local-npm-registry then serves it to npm as a localhost
# registry — OBS build workers are offline.
# Archful: @lydell/node-pty ships prebuilt Linux ELF prebuilds for the
# process-capture feature, so the payload is not noarch.
%global debug_package %{nil}
%global _missing_build_ids_terminate_build 0

Name:           rea-agents
Version:        6.9.0
Release:        0
Summary:        Reverse-engineering CLI and MCP server for AI agents
License:        MIT
URL:            https://github.com/morluto/rea
Source0:        rea-agents-%{version}.tgz
Source10:       package-lock.json
Source11:       node_modules.spec.inc
%include %_sourcedir/node_modules.spec.inc
ExclusiveArch:  x86_64

BuildRequires:  nodejs24
BuildRequires:  npm-default
BuildRequires:  local-npm-registry
# rea refuses to start on Node below its engines floor; the check section
# re-derives the floor from package.json, this macro is only the Requires
# fallback
%global node_floor 24.22.1
Requires:       nodejs24 >= 1:%{node_floor}

# env-node shebangs across the npm payload; the wrapper is the entrypoint
%global __brp_mangle_shebangs %{nil}

%description
REA (Reverse Engineer Anything) is one CLI and MCP server that lets agents
inspect native binaries, JavaScript and Electron apps, .NET assemblies and
websites, with evidence-backed results. Analysis runs locally; native
analysis can use an existing Hopper, Ghidra, IDA or Kuna installation.

%prep
%autosetup -n package
# The tarball ships an npm-shrinkwrap.json whose resolved URLs point at
# registry.npmjs.org — npm would bypass the local registry and fail on the
# offline build worker. Resolution happens against package.json instead.
rm -f npm-shrinkwrap.json

%build
# local-npm-registry serves the dependency tarballs (Source10000+: the
# OBS worker auto-unpacks node_modules.obscpio flat into %{_sourcedir})
# as a local npm registry — OBS build workers are offline.
# --ignore-scripts: prebuilt payloads only; frida (root optionalDependency)
# is nonfunctional without its network install script and rea treats it as
# optional, so drop it after the install
local-npm-registry %{_sourcedir} install \
    --omit=dev --ignore-scripts --os=linux \
    --no-audit --no-fund
rm -rf node_modules/frida

# Windows-only native payload from the npm tarball
rm -f native/windows/build/rea-windows-x64.node
# foreign-platform leftovers, if any
for plat in darwin-arm64 darwin-x64 win32-arm64 win32-x64 linux-ia32; do
    find node_modules -type d -name "$plat" -exec rm -rf {} +
done

%install
install -d -m755 %{buildroot}%{_prefix}/lib/node_modules/%{name}
cp -a . %{buildroot}%{_prefix}/lib/node_modules/%{name}/

for b in rea rea-agents; do
    install -Dpm755 /dev/null %{buildroot}%{_bindir}/$b
    cat > %{buildroot}%{_bindir}/$b <<'EOF'
#!/bin/sh
exec /usr/bin/node24 /usr/lib/node_modules/rea-agents/scripts/rea.mjs "$@"
EOF
done

%check
# Scratch HOME: first run writes user-level state.
# rea hard-exits on Node below its engines floor; smoke-run only where the
# buildroot nodejs24 meets it. The floor comes from package.json engines for
# the nodejs24 major we wrap (survives version bumps without spec edits),
# falling back to the node_floor macro when engines has no match.
runtime=$(rpm -q --qf '%%{version}' nodejs24)
floor=$(sed -n 's/.*"nod[e]": *"\([^"]*\)".*/\1/p' package.json \
    | grep -oE '\b24\.[0-9]+\.[0-9]+' | sort -V | tail -1)
floor=${floor:-%%{node_floor}}
if [ "$(printf '%%s\n%s\n' "$floor" "$runtime" | sort -V | tail -1)" = "$runtime" ]; then
    HOME=%{_builddir} node24 scripts/rea.mjs --version
    HOME=%{_builddir} node24 scripts/rea.mjs --help >/dev/null
else
    echo "distro nodejs24 $runtime below rea's $floor floor; skipping smoke run"
fi

%files
%license LICENSE
%doc README.md DISCLAIMER.md
%{_bindir}/rea
%{_bindir}/rea-agents
%dir %{_prefix}/lib/node_modules
%{_prefix}/lib/node_modules/%{name}/

%changelog
