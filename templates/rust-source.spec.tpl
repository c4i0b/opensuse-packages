# Template: Rust from-source build (validated by packages/television).
# Changelog lives in <name>.changes (OBS merges it into %changelog).
#
# Pair with this _service (placeholders in __UPSTREAM__/<v>); the tag tarball
# is fetched server-side, vendoring is CLIENT-side:
#
#   <services>
#     <service name="tar_scm" mode="serveronly">
#       <param name="url">https://github.com/__UPSTREAM__.git</param>
#       <param name="scm">git</param>
#       <param name="revision">__VERSION__</param>
#       <param name="versionformat">@PARENT_TAG@</param>
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
# Hard-won lessons encoded here:
# - api.opensuse.org runs only services in its server-side allowlist; `tar` and
#   `cargo_vendor` are NOT among them (only tar_scm/obs_scm/recompress/
#   set_version/download_url/...). obs_scm + tar fails "No such file or
#   directory"; use tar_scm alone.
# - cargo_vendor must be mode="manual" and run client-side. Regenerate
#   vendor.tar.zst (gitignored, but rsynced by push — *.tar.zst is not excluded)
#   in a tumbleweed container:
#     podman run --rm -v $PWD:/work:Z registry.opensuse.org/opensuse/tumbleweed:latest \
#       bash -c 'zypper -qn in --no-recommends obs-service-cargo_vendor &&
#                /usr/lib/obs/service/cargo_vendor --src __NAME__-__VERSION__ \
#                  --outdir /work --compression zst \
#                  --respect-lockfile true --update false'
#   Two hard-won flags/requirements (2026-11 mise/oxker/atac/ludusavi fleet):
#   the --src glob needs the extracted source tree present in the package dir
#   (extract the tag tarball there first, delete it after), and the default
#   --update true rewrites Cargo.lock and then aborts under --locked.
#   The archive carries vendor/ + .cargo/config.toml + Cargo.lock at its root,
#   exactly what %autosetup -a1 + %cargo_build (offline) expect.
# - %cargo_build comes from cargo-packaging (linter enforces the BuildRequires).
# - rust-toolchain.toml upstream is harmless: OBS cargo is not rustup-wrapped.
# - From-source builds are strip-safe and need no ExclusiveArch: plain
#   `cargo build --release` builds wherever rustc exists.
# - Completion dirs: zsh/fish parents must be %dir-owned or check-filelist FAILs.
# - %{?ext_man} on the manpage: brp compresses it and OBS owns the extension.
Name:           __NAME__
Version:        __VERSION__
Release:        0
Summary:        __SUMMARY__
License:        __LICENSE__
URL:            __URL__
Source0:        __NAME__-%{version}.tar.zst
Source1:        vendor.tar.zst
BuildRequires:  cargo-packaging
#   - worker OOM mitigation when a single rustc exceeds worker RAM
#     (see docs/packaging/rust.md): build_rustflags with
#     -C codegen-units=16 -C debuginfo=0 + CARGO_PROFILE_RELEASE_LTO=false.
#   - rpm expands macros inside comments — never write a literal macro
#     call in a comment; unbraced `%cargo_build -p` parses -p as a macro
#     option (use the braced %{cargo_build} form to forward flags).

%description
__DESCRIPTION__

%prep
%autosetup -p1 -a1

%build
%{cargo_build}

%install
install -Dpm 0755 target/release/__BIN__ %{buildroot}%{_bindir}/__BIN__
# Only if the tag ships a manpage (television keeps it in man/):
install -Dpm 0644 man/__BIN__.1 %{buildroot}%{_mandir}/man1/__BIN__.1
mkdir -p %{buildroot}%{_datadir}/bash-completion/completions %{buildroot}%{_datadir}/zsh/site-functions %{buildroot}%{_datadir}/fish/vendor_completions.d
# Only if the CLI generates completions (drop the shells it doesn't):
target/release/__BIN__ __INITCMD__ bash > %{buildroot}%{_datadir}/bash-completion/completions/__BIN__
target/release/__BIN__ __INITCMD__ zsh  > %{buildroot}%{_datadir}/zsh/site-functions/___BIN__
target/release/__BIN__ __INITCMD__ fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/__BIN__.fish

%files
%license LICENSE
%doc CHANGELOG.md README.md
%{_bindir}/__BIN__
%{_mandir}/man1/__BIN__.1%{?ext_man}
%{_datadir}/bash-completion/completions/__BIN__
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/___BIN__
%dir %{_datadir}/fish
%dir %{_datadir}/fish/vendor_completions.d
%{_datadir}/fish/vendor_completions.d/__BIN__.fish

%changelog
