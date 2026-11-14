# Packaging quirks: Rust

Lessons from the 2026-11 storytold fleet (14 GUI Rust packages) plus
television. The templates carry the mechanics:
[rust-gui](../../templates/rust-gui.spec.tpl) (winit/wgpu apps) and
[rust-source](../../templates/rust-source.spec.tpl) (CLI).

## Vendoring is client-side

`cargo_vendor` is NOT in the OBS server-side service allowlist: the
`_service` fetches the tag server-side (`tar_scm`), and `vendor.tar.zst`
is generated on a dev machine with the template one-liner (tumbleweed
container + `obs-service-cargo_vendor`) and rides `just push` (the rsync
`--filter=P *.tar.zst` uploads it when present, never deletes it). Rust
packages have no `upstream` file — bumps regenerate the vendor archive
manually until that is automated.

Upstreams shipping their own `vendor/` (path-patched forks) need the
custom overlay scripts (`tools/pinvendor-*.py`, pdfcraft/photocraft).

## `_service` version detection

- `v`-prefixed tags break `set_version` ("unable to detect the version"):
  add `<param name="versionrewrite-pattern">v(.*)</param>` +
  `<param name="versionrewrite-replacement">\1</param>`.
- The parameter is `versionrewrite-pattern` (dash); the gateway rejects
  `versionrewrite_regex`/`versionrewriteregix` spellings.

## `%cargo_build` is parametric — brace it

- Unbraced `%cargo_build -p name` makes the macro parse `-p` as its own
  option: `Unknown option p in cargo_build()`. Pass cargo flags through
  the braced form `%{cargo_build} -p %{name}`, or `cd` into the workspace
  member directory, or call `%{__cargo} build` directly.
- rpm expands macros **inside comments**: a comment mentioning
  `%cargo_build(...)` triggers the same failure. Never write a literal
  macro call in a comment — describe it in words.

## Unvendored `[patch.crates-io]` entries

cargo validates every `[patch.crates-io]` entry offline, but
`cargo vendor` only emits depended-on crates: unused patch pins
(egui_demo_lib, egui_inspection, ...) abort the build with
"patch location ... does not contain packages matching". Drop them in
`%prep` — one canonical guarded loop (the `ls -d vendor/"$crate"-*`
vendor-dir check; a plain prefix grep over `ls vendor` can false-positive
on crates sharing a prefix), carried by the rust-gui template and every
craft spec.

## Worker OOM (rustc)

The distro RUSTFLAGS inject `-C debuginfo=2` and release profiles use
thin-LTO + `codegen-units=1`: a single rustc can need >4 GB (or >9 GB)
and the worker OOM-kills it (boa_engine is the usual victim; first seen
on aarch64 workers). The canonical mitigation is the **default** in the
rust-gui template and in every craft spec — keep it even where the build
survives without it:

```spec
%global build_rustflags -Clink-arg=-Wl,-z,relro,-z,now -C codegen-units=16 -C debuginfo=0
```

plus, in `%build` before the cargo invocation:

```spec
export CARGO_PROFILE_RELEASE_LTO=false
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=16
```

## Misc

- winit/wgpu dlopen their platform libs: Rust binaries declare no
  automatic rpm deps, so list libX11/libXcursor/libXi/libXrandr/
  libxkbcommon(+x11)/libwayland-client/vulkan-loader as explicit
  `Requires:` (the rust-gui template has the set).
- `%global cargo_install_lib false` for bin-only crates;
  `%global debug_package %{nil}` when the release profile strips.
- `LOCKSTEP_XML_PATH` (zbus lockstep) points at the vendored
  `atspi-common-*/xml` glob — vendor dirs are version-suffixed.
