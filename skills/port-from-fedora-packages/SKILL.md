---
description: Use when porting a package (or batch) from the fedora-packages repo (github.com/c4i0b/fedora-packages) into this repo. Pre-flight checklist, openSUSE adaptations, and when to stop and ask the user before porting.
name: port-from-fedora-packages
---

# Porting a package from fedora-packages

Source repo (GitHub, source of truth): 
https://github.com/c4i0b/fedora-packages — spec at
`packages/<name>/<name>.spec`. Clone it as a sibling of this repo
(`../fedora-packages`) when porting; if already cloned, make sure it is
up to date on `main` first. In committed files and reports reference it by
the GitHub URL, never by an absolute local path.
The spec is the behavioral reference — build model, Requires, %install
layout, quirks. Reference the UPSTREAM project by its GitHub URL
(`URL:`/`Source0` already carry it) in specs, `_service` and reports.

## Checklist (all must be answered BEFORE writing any file)

1. **Gap check**: is `<name>` already in this repo (`ls packages/`)? Is it in
   `openSUSE:Factory` (the local snapshot `/tmp/opencode/factory.txt` if
   fresh, else re-fetch: `just osc api /source/openSUSE:Factory` and grep,
   or check https://software.opensuse.org)? If either is true → stop, report,
   do not port. Name variants count (e.g. `heroic` vs `heroic-games-launcher`).
2. **Build model classification** (from the fedora spec): rust-from-source /
   go / python-pyproject / C / fish-plugin / fonts / icon-theme /
   prebuilt-electron / prebuilt-rpm-repackage / deb-repack / other.
   Pick the matching `templates/*.spec.tpl`; if none fits, decide whether a
   NEW template is warranted (reusable pattern) before improvising.
3. **OBS-offline feasibility**: does the build need network (npm install,
   go mod download, crates.io fetch)? If yes, it must be vendored
   client-side (`vendor.tar.zst`) or the port is impossible → report skip.
4. **Prebuilt policy**: if any Source is a prebuilt binary, the package must
   be registered in `PREBUILT_ORIGIN` (opensuse-lint.py) with the right
   origin — `bun` needs `%global __os_install_post %{nil}`; `electron`
   bundles disable strip; `go`/`rust` prebuilts are strip-safe. Check
   docs/packaging/general.md.
5. **Dep mapping**: every `Requires`/`BuildRequires` must exist in
   Tumbleweed under an openSUSE name. Known renames: `fd-find` → `fd`;
   python PyPI names differ (`dbus-fast` → `python3-dbus_fast`). Unverified
   name → grep the Factory snapshot. A missing runtime dep that is itself
   portable is a SEPARATE port (do not inline it) — and a flag to ask (below).
   CAUTION: the Factory package list is SOURCE-level; binary package names
   can differ (e.g. source `libusb-1_0` builds binary `libusb-1_0-0`, and
   deps resolve against binaries). Confirm the BINARY name (zypper se,
   software.opensuse.org, or a published-binary search) before adding a
   dep that only matched as a source name.
6. **Legal/trademark**: repack of vendor binaries (.deb/.rpm from a browser
   vendor, etc.) → flag to ask (below). Upstream release artifacts of the
   project itself are fine.
7. **Versioning traps**: v-prefixed tags need `versionrewrite-pattern`/
   `replacement` in `_service`; no tags at all → pin commit + literal
   `versionformat` (see `packages/crunch`) and note it in the `.changes`
   entry; date tags → `tools/bump-date-tag.sh` model.
8. **Fedora-isms to drop**: `%{?dist}`, `%autochangelog`, SELinux,
   `%_fontbasedir`, `fonts-srpm-macros`, Fedora conditionals, bare
   `%pyproject_wheel` (use `%python3_*` macros), `%make_build`/`%make_install`
   are fine — check what the closest sibling package in this repo uses.

## Ask the user when the checklist leaves doubt

Stop and ask (do not guess) if:

- A **runtime dep is missing** from Tumbleweed and porting it is nontrivial
  (ask: port the dep too, or ship with the dep optional + comment?).
- The **build model is prebuilt/deb-repack** of a third party (trademark or
  redistribution terms unclear).
- The fedora spec **collapses or splits subpackages** and the openSUSE-side
  layout is a judgment call (variants, -data splits).
- The package is in Factory only under a **different name** and it is
  unclear whether that satisfies the user's request.
- A **new template** would be needed and its scope is ambiguous.

## Porting mechanics

Per package create `packages/<name>/`: `<name>.spec` (template skeleton +
fedora spec behavior), `_service` (server-side fetch; rust adds
`cargo_vendor` mode="manual" + client-side `vendor.tar.zst` via the tumbleweed
container one-liner in templates/rust-source.spec.tpl), and
`<name>.changes` with a single initial entry
(`- Initial package of <name> <version>.`).
Never commit archives. English only; comments only for non-obvious workarounds.

## Gate before handing over

- `just lint-all` — zero FAIL/WARN attributable to the new package(s).
- If a new template was created: its invariants are written in the template
  header and validated by at least one ported package.
- Do not commit/push unless the user asked; report files, build model,
  dep changes vs fedora (with reasons), lint result, and anything skipped.
