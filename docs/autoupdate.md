# Automatic updates

Updates must stay fully automatic: a human should never need to touch a
package to get its next version. This requirement is why the repo is
`-bin`-only (see the source-builds-rejected section in
[conventions.md](conventions.md)).

## Renovate

- Renovate (hosted GitHub App) bumps packages through **regex managers**:
  each package's spec `Version:` and `_service` download URL are bumped
  **together in one PR** (same `depName` + `datasource`, one dependency,
  both files updated).
- `requiredStatusChecks: ["validate-bump"]` gates auto-merge: a bump PR only
  merges when `validate-bump` passes.

## validate-bump

The generic `validate-bump.yml` workflow runs on any PR touching
`packages/**`. It:

1. detects which packages changed,
2. checks the spec `Version:` is referenced in the `_service` URL (guards
   against version drift between the two files),
3. HEADs the release asset URL (must return 2xx/3xx, catching dead or
   not-yet-published assets).

## push-to-obs

On merge to `main`, `push-to-obs.yml` syncs changed packages to OBS. It is
self-contained: it drives `osc` inline, mirroring `just push`, with no
dependency on the local tooling. Secrets: `OBS_USER`, `OBS_PASSWORD`.

It triggers twice: on `push` to `main` (human commits), and on `workflow_run`
after `auto-merge` completes — bot merges are performed with `GITHUB_TOKEN`,
and pushes created with `GITHUB_TOKEN` fire no `push` events (without the
`workflow_run` trigger, no Renovate/Dependabot bump ever reached OBS; that
was the state from 2026-08 to 2026-11).

## auto-merge

`dependabot-automerge.yml` (name: `auto-merge`) merges bot PRs after the
required checks pass: it watches `gh pr checks --watch --fail-fast` before
merging (red: ytm-player 2.2.0 was merged while validate-bump was red over a
404 asset).

Known Renovate limitation behind the ytm-player red: the `_service` regex
bumps only the version in the download **directory** (`.../v2.2.0/`), not in
the **filename** (`ytm_player-2.0.0.tar.gz`). When an upstream names its
asset with the version, the filename must be fixed by hand in the bump PR —
validate-bump catches the 404 and (with the check-watching above) blocks the
merge until fixed.

## Dependabot

Dependabot keeps GitHub Actions updated; its PRs auto-merge after a
workflow-YAML gate (the YAML must still parse and the workflows must be
valid).
