---
description: Use when an OBS build of a package in this repo fails and the buildlog is needed to diagnose it. Covers fetching the log via osc, where errors hide, and repo-specific traps.
name: diagnose-obs-failure
---

# Diagnosing a failed OBS build

Find the package's build status and log from the repo root:

```sh
just results packages/<name>   # per-repo build status
just log packages/<name>       # osc buildlog for opensuse_tumbleweed x86_64
```

`just log` streams the live buildlog. If the build is still running, wait for
it to finish or read what has printed so far. Redirect to a file when the log
is long, then work on the file.

## Where the error hides

- rpmbuild failures are near the end. Grep for `Bad exit status`,
  `RPM build errors`, `Installed (but unpackaged)` and `error:` and read
  ~30 lines of context above the match.
- OBS appends its own checks after rpmbuild. `check-filelist` failures
  (unowned directories) appear after the `%files` processing, not in the
  rpmbuild section.
- A source fetch failure never reaches rpmbuild. It fails in the `_service`
  stage at the top of the log with a 404 or a "not a gzip file" tar error.

## OBS-specific traps

- **brp strip corrupts bun prebuilts.** The stripped ELF loses its appended
  payload and the binary falls back to the Bun CLI at runtime. Symptom: the
  build succeeds but the installed command behaves like `bun --help`. Fix:
  `%global __os_install_post %{nil}` at the top of the spec. Go, Rust and
  Electron prebuilts are strip-safe and must NOT have the macro.
- **check-filelist FAILs on unowned dirs.** Any dir under
  `%{_datadir}/icons/hicolor/*/apps/`, `%{_datadir}/zsh/` or
  `%{_datadir}/fish/` needs a `%dir` line in `%files`. OBS enforces this
  even when the parent package owns the tree.
- **_service fetch failures.** A bad URL or a version mismatch between the
  spec `Version:` and the `_service` download URL returns an error page
  instead of a tarball. The validate CI job catches these on PRs, so a
  fetch failure on main means the two files drifted. Fix both together.
- **go_modules vs a too-new go.mod.** Status `broken` with no logfile and
  `ERROR:obs-service-go_modules:go mod download failed` means the go.mod
  `go` directive exceeds the Go on the OBS source-service host
  (`GOTOOLCHAIN=local`, no toolchain download). The linter's
  `go-modules-toolchain` FAIL guards this (`OBS_GO_MODULES_GO` ceiling).
  Fix: client-side `vendor.tar.zst` + `BuildRequires: zstd`, drop
  go_modules from `_service` (reference: dnscontrol, nexttrace).
- **BuildRequires present locally but missing on OBS.** Rare for `-bin`
  packages (nothing compiles). The build image installs BuildRequires on
  demand, OBS resolves them itself. Symptom of the gap: the OBS build fails
  in `%install` on a missing tool the local build had.

## After fixing

`just lint`, commit, then `just push packages/<name> "<msg>"` (the push
re-runs the lint gate first). Watch the rebuild with
`just results packages/<name>` and pull the log again if it fails.
