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

## Dependabot

Dependabot keeps GitHub Actions updated; its PRs auto-merge after a
workflow-YAML gate (the YAML must still parse and the workflows must be
valid).
