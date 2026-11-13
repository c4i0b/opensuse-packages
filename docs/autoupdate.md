# Automatic updates

Updates must stay fully automatic: a human should never need to touch a
package to get its next version. This requirement is why the repo is
`-bin`-only (see the source-builds-rejected section in
[conventions.md](conventions.md)).

## autoupdate (the bot)

Scheduled workflow (`.github/workflows/autoupdate.yml`, every 4 hours +
manual dispatch), ported from the fedora-packages model. Per package,
`packages/<name>/upstream` selects the tracker:

- `owner/repo` → GitHub Releases latest (leading `v` stripped; falls back
  to the latest tag when the repo has no Releases)
- `tags:owner/repo` → latest git tag via `ls-remote` (tags-only repos,
  zero API quota)
- `npm:<package>` → npm dist-tag `latest`

A package without an `upstream` file is opt-out: `television` has none —
its Rust vendor archive is regenerated client-side (see
[conventions.md](conventions.md)), so its bumps are manual until vendor
regeneration is automated.

The bot commits each bump straight to `main` (`chore(<pkg>): update to
<ver>`). Commits made with GITHUB_TOKEN fire no `push` events, so
push-to-obs picks them up through its `workflow_run` trigger on the
autoupdate workflow completing.

Bumping goes through `packages/<name>/bump.sh` when the package has one,
else the central `tools/bump.sh`: spec `Version:`, **every** old-version
occurrence in `_service` (download directory AND asset filename), plus a
`.changes` entry. (Red: the Renovate regex manager bumped only the first
match, freezing ytm-player's asset name at 2.0.0 while the directory said
v2.2.0 — 404 since the 2.1.0 bump.)

To skip or downgrade a release: push a commit whose message is
`autoupdate: override <version>` touching the package dir; the bot
respects the latest override.

## Manual bumps: vendored Rust packages

Rust packages with a client-side vendor archive carry no `upstream`
file, so the bot skips them (see the note on `television` above). A
manual bump must touch all four, in one commit:

1. spec `Version:` (`bump.sh` covers the spec + `_service` + `.changes`
   part),
2. `_service` — **every** old-version occurrence,
3. regenerate `vendor.tar.zst` (the `cargo_vendor` command lives in
   `templates/rust-source.spec.tpl`; the archive is gitignored and
   rsynced to OBS by `push`),
4. prepend the `.changes` entry (`just vc packages/<name>`).

The drift to avoid: bumping only the spec leaves a stale `vendor.tar.zst`
— `%cargo_build` runs offline against the old crates, so the build
passes silently with outdated dependencies. Verify the vendored crates
match the new spec `Version:` before pushing.

## Why not Renovate (rejected 2026-11, app uninstalled)

Renovate + regex managers + an auto-merge workflow ran this repo from
2026-08 to 2026-11 and produced three real failures: the asset-filename
freeze above; bot merges done with GITHUB_TOKEN whose pushes fire no
`push` events (no bump reached OBS in three months); and a PR merged
while validate-bump was red. fedora-packages had rejected Renovate for
the same class of problems. Reintroducing it needs a NEW observed
failure of autoupdate, not a better argument.

## validate-bump (manual PR gate)

The generic `validate-bump.yml` workflow runs on any PR touching
`packages/**`. It:

1. detects which packages changed,
2. checks the spec `Version:` is referenced in the `_service` URL (guards
   against version drift between the two files),
3. HEADs the release asset URL (must return 2xx/3xx, catching dead or
   not-yet-published assets).

## push-to-obs

On merge to `main` (or an autoupdate commit), `push-to-obs.yml` syncs
changed packages to OBS. It is self-contained: it drives `osc` inline,
mirroring `just push`, with no dependency on the local tooling. Secrets:
`OBS_USER`, `OBS_PASSWORD`.

It triggers on `push` to `main` (human commits) and on `workflow_run`
after `auto-merge` or `autoupdate` complete — bot actions run on
GITHUB_TOKEN, and pushes created with GITHUB_TOKEN fire no `push` events.

## auto-merge

`dependabot-automerge.yml` (name: `auto-merge`) merges bot PRs after the
required checks pass: it watches `gh pr checks --watch --fail-fast` before
merging (red: ytm-player 2.2.0 was merged while validate-bump was red over
a 404 asset). It no longer handles version bumps (autoupdate does); what
remains for it is Dependabot keeping GitHub Actions updated.

## Dependabot

Dependabot keeps GitHub Actions updated; its PRs auto-merge after the
workflow-YAML gate above.
