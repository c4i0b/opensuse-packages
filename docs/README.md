# opensuse-packages docs

Evergreen reference. Start here; the lean rule list agents must follow every
session lives in [AGENTS.md](../AGENTS.md). Trust labels: `live` documents
maintained truth, `reference` stable background.

- [environment.md](environment.md) — live: ephemeral tooling container,
  credentials, the `just` runner, hooks
- [obs.md](obs.md) — live: the OBS contract, `_service` source fetch, push
  and build validation policy
- [autoupdate.md](autoupdate.md) — live: Renovate regex managers, the
  validate-bump gate, Dependabot
- [conventions.md](conventions.md) — live: package layout, `-bin`-only
  policy, versioning, repo hygiene
- [workflow.md](workflow.md) — live: optional beads task tracking and
  parallel orchestration of the bd task graph
- packaging quirks by ecosystem — reference:
  [general](packaging/general.md) ·
  [python](packaging/python.md)
