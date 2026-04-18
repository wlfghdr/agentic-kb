# External Links — Referencing the World Outside the KB

> **Version:** 0.1 | **Last updated:** 2026-04-18

KBs are not islands. A topic about *service reliability* is grounded in real dashboards. A decision about a *migration* points to an asset registry entry, a ticket, a PR. Repos that hold product outcomes, runbooks, configuration, or CMDB records are authoritative **outside** the KB — the KB references them; it does not duplicate them.

This concept defines **how** external sources are linked from the KB in a consistent, auditable way.

## Principle

> **Link, don't copy.** If the information lives somewhere else that is authoritative, keep the link. Copy only the conclusion, position, or summary that belongs in the KB.

Copying invites drift. A runbook that gets pasted into a topic file becomes stale the moment the runbook is updated. A link stays fresh by construction.

## Where External Links Live

External links can appear in any long-lived file:

- **Topic files** — *"Current position on progressive delivery, grounded in [dashboard-x] and [runbook-y]."*
- **Decision files** — *"Option (b) supported by evidence in [asset-registry#svc-123]."*
- **Foundation files** — *"See `references/foundation/sources.md` for the canonical list of durable references."*
- **Workstream files** — *"Depends on [platform-roadmap-repo]."*
- **Stakeholder entries** — *"@alice's team maintains [runbook-y]."*

## The Sources Index

`references/foundation/sources.md` is the canonical index of durable external references. Each entry carries:

```markdown
| Alias | URL / Path | Kind | Description |
|-------|-----------|------|-------------|
| dashboard-x | https://example.org/dashboards/reliability-overview | dashboard | Team-wide reliability overview |
| runbook-y | ../runbooks-repo/payment-service.md | runbook | Canonical payment service runbook |
| asset-registry | https://example.org/assets | cmdb | Authoritative asset inventory |
| platform-roadmap | ../platform-roadmap-repo | repo | Roadmap artifacts for the platform workstream |
```

Once an alias is defined here, topic and decision files can reference it as `[dashboard-x]` — the full URL only has to be maintained in one place.

### Kinds of External Sources

The `Kind` column is loosely typed but conventionally one of:

| Kind | Examples |
|------|----------|
| `repo` | Asset, product, outcome, runbook, config repos |
| `dashboard` | Metrics, SLOs, service health, operational overviews |
| `website` | Internal or external documentation, vendor docs |
| `cmdb` | Asset registry, service registry, ownership catalog |
| `ticket-system` | Issue tracker, PR tracker |
| `wiki` | Team or org wiki pages |
| `communication` | Slack channels, email lists, chat rooms |
| `artifact-store` | Registries for build artifacts, skill marketplaces |

## External Links in Topic Files

A topic file may list its most-relevant external anchors at the top:

```markdown
# Topic: Service Reliability

**External anchors**:
- Dashboard: [dashboard-x] — team-wide overview
- Runbook: [runbook-y] — canonical payment service runbook
- Asset registry: [asset-registry#svc-123] — payment service entry

[... main content ...]
```

This gives the agent (and humans) a fast lookup of ground-truth sources when re-reading a topic.

## Health of External Links

External links can rot too. CI for a personal KB should include dead-link checks (see [../spec/security-privacy.md](../spec/security-privacy.md) and the reference CI script in the spec repo). Broken links in `sources.md` or in topic headers are treated the same as broken internal links: red CI, fix before merging.

Because external services rate-limit, the dead-link check should:

- Respect `robots.txt` where applicable,
- Cache results per-run,
- Allow per-host exclusions for services known to be unreachable from CI (private intranet hosts, for example).

## External Sources in Team and Org-Unit KBs

Team and org-unit KBs maintain their **own** `sources.md` (typically in `foundation/` or at the root). They follow the same format. Agent tooling reads the applicable `sources.md` for the layer being operated on — team-level links are not automatically inherited into the personal KB.

## Why Define This Explicitly

Without a convention, external references scatter across inline URLs with no metadata, no alias, no description. Maintaining them becomes impossible. With the convention:

- Aliases decouple content from URL changes.
- `sources.md` gives a single place to audit what the KB depends on.
- CI can check link health automatically.
- Agents can *suggest* adding an entry to `sources.md` when they notice a URL appearing in ≥3 places.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | New concept — adds first-class external link handling |
