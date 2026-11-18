# Template: npm bundle — official npm tarball + offline dependency install
# (validated by packages/openclaw, packages/rea-agents).
# Changelog lives in <name>.changes (OBS merges it into %changelog).
#
# `upstream` file allowed: the autoupdate bot runs `tools/revendor.sh`,
# which executes `fetch.sh --vendor` in a tumbleweed container on every
# bump (and reverts the bump if the re-vendor fails; opensuse-lint.py
# keeps gating upstream-on-unmodelable-vendored).
#
# This is the OBS-canonical npm model: the cockpit family in
# openSUSE:Factory uses the same local-npm-registry + client-side
# node_modules vendoring (obs-service-node_modules); their update flow
# (npm install --package-lock-only, then `osc service manualrun`) is our
# `fetch.sh --vendor`. If the release tarball ships a prebuilt dist/
# (cockpit route, our devcontainers-cli), skip this template — no
# build-time npm is needed at all.
#
# MODEL
# - Source0 is the registry.npmjs.org tarball (fetched server-side via
#   download_url in _service — see below).
# - The dependency closure is vendored CLIENT-side by each package's
#   `fetch.sh --vendor` as:
#     * package-lock.json (Source10, committed — the reviewable pin set),
#     * node_modules.spec.inc (Source11, committed — lists every tarball as
#       a Source10000+ registry URL with a flat rename, url#/<flat>.tgz:
#       SRPM provenance, the cockpit shape — nothing is fetched from
#       them),
#     * node_modules.obscpio (gitignored; the transport: the OBS worker
#       auto-unpacks any *.obscpio source flat into %%{_sourcedir}.
#       Uploaded per-bump by a local `just push`; the P filter in
#       tools/obs-rsync.sh protects it from --delete on CI pushes, whose
#       checkouts never have one — a bump without a local push builds
#       against the stale container. Doubles as the local-only cache
#       fetch.sh expands for the pre-flight build).
#   `local-npm-registry %%{_sourcedir}` then serves the unpacked tarballs
#   to npm as a localhost registry.
#
# INVARIANTS (break loudly if violated — see opensuse-lint.py checks):
# - %build must not run a bare `npm install` without local-npm-registry:
#   OBS build workers are offline.
# - package-lock.json, node_modules.obscpio and node_modules.spec.inc are
#   regenerated TOGETHER by fetch.sh --vendor on every bump.
# - If the upstream npm tarball ships bundleDependencies ("inBundle": true
#   lock entries), those have no registry tarball: fetch.sh npm-packs them
#   from the tarball's own node_modules/.
# - If the npm tarball ships an npm-shrinkwrap.json, that IS the lockfile
#   (npm never writes a package-lock.json next to one) — reuse it as
#   package-lock.json and REMOVE it in %prep: its resolved URLs point at
#   registry.npmjs.org and would bypass the local registry.
# - env-node shebangs across the payload: keep
#   %%global __brp_mangle_shebangs %%{nil} and filter env-script-interpreter
#   et al. in <name>.rpmlintrc; the /usr/bin/<name> wrapper is the
#   entrypoint and calls node24 directly.
#
# Pair with this _service:
#
#   <services>
#     <service name="download_url">
#       <param name="protocol">https</param>
#       <param name="host">registry.npmjs.org</param>
#       <param name="path">/__NAME__/-/__NAME__-__VERSION__.tgz</param>
#       <param name="filename">__NAME__-__VERSION__.tgz</param>
#     </service>
#   </services>
#
# openSUSE vs Fedora: the npm CLI comes from `npm-default` (nodejs24 alone
# has no usable /usr/bin/npm) and the interpreter binary is /usr/bin/node24
# (Fedora's node-24/npm-24 do not exist here).

# noarch variant: strip arch payloads in %install like openclaw (ELF, wasm,
# per-platform dirs). Archful variant (native addon prebuilds, e.g.
# rea-agents): add %%global debug_package %%{nil},
# %global _missing_build_ids_terminate_build 0 and ExclusiveArch.
Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            https://github.com/__UPSTREAM__
Source0:        __NAME__-%{version}.tgz
Source10:       package-lock.json
Source11:       node_modules.spec.inc
%include %_sourcedir/node_modules.spec.inc
BuildArch:      noarch

BuildRequires:  nodejs24
BuildRequires:  npm-default
BuildRequires:  local-npm-registry
Requires:       nodejs24

# env-node shebangs across the npm payload; the wrapper is the entrypoint
%global __brp_mangle_shebangs %{nil}

%description
__DESCRIPTION__

%prep
%autosetup -n package
# local-npm-registry serves the vendored tarballs (expanded flat into
# %%{_sourcedir} from node_modules.obscpio) as a local npm registry — OBS
# build workers are offline. Adapt the npm flags to the upstream package:
# --legacy-peer-deps for conflicting peerOptionals, --omit=optional to drop
# arch-specific native addons (noarch), --os=linux to skip foreign payloads.
local-npm-registry %{_sourcedir} install \
    --omit=dev --ignore-scripts --no-audit --no-fund

%build
# postinstall completion steps, if upstream needs any, run here (node24 ...)

%install
install -d -m755 %{buildroot}%{_prefix}/lib/node_modules/%{name}
cp -a . %{buildroot}%{_prefix}/lib/node_modules/%{name}/

install -Dpm755 /dev/null %{buildroot}%{_bindir}/__BIN__
cat > %{buildroot}%{_bindir}/__BIN__ <<'EOF'
#!/bin/sh
exec /usr/bin/node24 /usr/lib/node_modules/__NAME__/__ENTRY__ "$@"
EOF

%check
# Scratch HOME: first run writes user-level state
HOME=%{_builddir} node24 \
    %{buildroot}%{_prefix}/lib/node_modules/%{name}/__ENTRY__ --version

%files
%license LICENSE
%doc README.md
%{_bindir}/__BIN__
%dir %{_prefix}/lib/node_modules
%{_prefix}/lib/node_modules/%{name}/

%changelog
