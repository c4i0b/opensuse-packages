# Template: Rust from-source GUI app (winit/wgpu/egui), validated by
# packages/cadcraft and packages/designcraft. CLI apps: rust-source.spec.tpl.
# Changelog lives in <name>.changes (OBS merges it into %changelog).
#
# Pair with this _service (placeholders in __UPSTREAM__/<v>); the tag tarball
# is fetched server-side, vendoring is CLIENT-side:
#
#   <services>
#     <service name="tar_scm" mode="serveronly">
#       <param name="url">https://github.com/__UPSTREAM__.git</param>
#       <param name="scm">git</param>
#       <param name="revision">v__VERSION__</param>
#       <param name="versionformat">@PARENT_TAG@</param>
#       <param name="versionrewrite-pattern">v(.*)</param>
#       <param name="versionrewrite-replacement">\1</param>
#       <param name="exclude">.git</param>
#     </service>
#     <service name="recompress" mode="serveronly">
#       <param name="file">*.tar</param>
#       <param name="compression">zst</param>
#     </service>
#     <service name="set_version" mode="serveronly"/>
#     <service name="cargo_vendor" mode="manual">
#       <param name="srcdir">__NAME__</param>
#       <param name="compression">zst</param>
#     </service>
#   </services>
#
# Hard-won lessons encoded here (shared with rust-source.spec.tpl):
# - api.opensuse.org runs only services in its server-side allowlist; `tar` and
#   `cargo_vendor` are NOT among them (only tar_scm/obs_scm/recompress/
#   set_version/download_url/...). obs_scm + tar fails "No such file or
#   directory"; use tar_scm alone.
# - cargo_vendor must be mode="manual" and run client-side. Regenerate
#   vendor.tar.zst (gitignored, but rsynced by push — *.tar.zst is not excluded)
#   in a tumbleweed container (git is needed when the workspace pins git deps).
#   `--update false --respect-lockfile true` keeps the upstream Cargo.lock:
#   a `cargo update` can silently drop dev/unused crates whose [patch] entries
#   then fail to resolve offline. First push needs a one-time manual
#   `osc ci` of vendor.tar.zst (push.sh excludes archives from its rsync):
#     podman run --rm -v $PWD:/work:Z registry.opensuse.org/opensuse/tumbleweed:latest \
#       bash -c 'zypper -qn in --no-recommends obs-service-cargo_vendor git &&
#                cd /work &&
#                /usr/lib/obs/service/cargo_vendor --src __NAME__-__VERSION__ \
#                  --outdir /work --compression zst --update false --respect-lockfile true'
#   The archive carries vendor/ + .cargo/config.toml + Cargo.lock at its root,
#   exactly what %autosetup -a1 + %cargo_build (offline) expect. `cargo vendor`
#   emits the source-replacement blocks for git-pinned crates (crates-io
#   [patch] sections included) straight into .cargo/config.toml — no
#   git-sources.conf stitching like the fedora spec needed.
# - v-prefixed git tags: @PARENT_TAG@ yields "v0.20.1" and set_version FAILs
#   "unable to detect the version"; versionprefix PREPENDS (wrong tool).
#   Strip with versionrewrite-pattern/replacement (red: designcraft rev 1).
# - %cargo_build comes from cargo-packaging (linter enforces the BuildRequires).
# - GUI-specific lessons (validated by cadcraft/designcraft):
#   - Rust ELF binaries declare no automatic deps on the libs winit/wgpu
#     dlopen (libX11, libXcursor, libXi, libXrandr, libxkbcommon(-x11),
#     libwayland-client, vulkan-loader): without the explicit Requires the
#     package installs broken on a bare X11/Wayland system (window fails to
#     open / no Vulkan device). Keep the dlopen Requires set below — rpm
#     autodeps cannot see dlopened libraries.
#   - Virtual workspaces (members = ["crates/*", "apps/*", ...]) may include
#     wasm or extra app members that must not be built: pass the member to
#     %cargo_build, which forwards options via %*:
#       %{cargo_build} -p %{name}
#   - zbus-lockstep's validate macro resolves ../xml relative to the crate
#     being compiled: in a vendored tree that hits the vendored "xml" crate
#     (whose extensionless LICENSE panics the macro) instead of atspi-common's
#     D-Bus XML dir — export LOCKSTEP_XML_PATH before %cargo_build.
#   - wgpu has no 32-bit/ppc story: ExclusiveArch x86_64 aarch64 explicitly
#     (never %{go_arches}-style macros — see opensuse-lint check).
#   - Icons under icons/hicolor/<size>/apps need %dir ownership of the hicolor
#     tree or OBS check-filelist FAILs (linter rule "icon").
%global cargo_install_lib false
%global debug_package %{nil}

ExclusiveArch:  x86_64 aarch64

Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            __URL__
Source0:        __NAME__-%{version}.tar.zst
Source1:        vendor.tar.zst
Source2:        %{name}.desktop
BuildRequires:  cargo-packaging
BuildRequires:  gcc
BuildRequires:  desktop-file-utils

# winit/wgpu dlopen these at runtime; Rust binaries declare no auto-deps
Requires:       libX11
Requires:       libXcursor
Requires:       libXi
Requires:       libXrandr
Requires:       libxkbcommon
Requires:       libxkbcommon-x11
Requires:       libwayland-client
Requires:       vulkan-loader

%description
__DESCRIPTION__

%prep
%autosetup -p1 -a1
# drop if the vendored tree has no unused [patch] entries: crates that are
# patched but absent from the build graph are locked (Cargo.lock) yet NOT
# vendored, and offline cargo dies with "patch location ... does not contain
# packages matching X" (red: designcraft, egui_demo_lib et al.)
sed -i -e '/^__UNUSED_PATCH__ = /d' Cargo.toml

%build
# drop if the vendored tree has no atspi-common (no accessibility stack)
[ -d vendor/atspi-common/xml ] && export LOCKSTEP_XML_PATH="$(pwd)/vendor/atspi-common/xml"
# drop -p if the crate is not a virtual-workspace member
%{cargo_build} -p %{name}

%install
install -Dpm 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/__DESKTOPID__.desktop

# ship whatever sizes upstream provides (they change between releases);
# adjust the assets/ path to the upstream icon tree
for icon in assets/app-icon/hicolor/*/apps/*; do
    install -Dpm 0644 "$icon" "%{buildroot}%{_datadir}/icons/hicolor/${icon#assets/app-icon/hicolor/}"
done

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/__DESKTOPID__.desktop

%files
%license LICENSE-APACHE LICENSE-MIT NOTICE
%doc README.md
%{_bindir}/__NAME__
%{_datadir}/applications/__DESKTOPID__.desktop
# OBS check-filelist FAILs on unowned hicolor dirs
%dir %{_datadir}/icons/hicolor
%dir %{_datadir}/icons/hicolor/*
%dir %{_datadir}/icons/hicolor/*/apps
%{_datadir}/icons/hicolor/*/apps/__ICON__.*

%changelog
