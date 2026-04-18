# Security & Privacy

> **Version:** 0.1 | **Last updated:** 2026-04-18

`agentic-kb` is designed to handle content of varying sensitivity. The spec is conservative by default: personal KBs are private, team and org-unit KBs are shared only within their scope, and marketplace skills are fully reviewed before publication.

## Classification by Layer

| Layer | Default sensitivity | Rule |
|-------|---------------------|------|
| L1 Personal | Private | Never reference personal-KB content in public repos or public artifacts. |
| L2 Team | Team-private | Visible within the team only; team members opt in by being granted repo access. |
| L3 Org-Unit | Org-private | Visible within the org unit; aggregates from team KBs. |
| L4 Marketplace | Shared (internal or public) | Safe-for-audience: no PII, no credentials, no hidden URLs. |
| L5 Company-wide | Top-down | Consumed into L1; treated as any other input, handled with the same gate. |

## Promotion Gates Enforce Safety

Every upward promotion passes an automated safety check:

- **L1 → L2 (`promote`)**: warn if the file references secrets, tokens, API keys, or URLs in `sources.md` that are marked private.
- **L1/L2/L3 → L4 (`publish`)**: hard block if any of the above are present. Additionally:
  - No PII in the skill body or in referenced templates.
  - No hardcoded external URLs — use aliases.
  - No shell commands that modify system state outside the workspace.
  - Only tools available via the marketplace may be referenced.

The block is enforced by the `publish` flow itself, then re-checked in the marketplace's CI (see [marketplace-and-skills.md](marketplace-and-skills.md) §Safety Rules).

## What Not to Put in a KB

- **Secrets**: API keys, passwords, tokens, private keys, connection strings. Use a secret manager.
- **Raw PII**: employee personal details, customer data, regulated records. Reference by alias or opaque identifier.
- **Legal material without review**: contracts, NDAs, privileged communications — usually out of scope.

The agent should **decline** to capture content that triggers any of these patterns and inform the user why.

## Task Items Are Sensitive Too

Personal `tasks/focus.md` items often include unreleased plans, stakeholder concerns, or in-progress negotiations. The agent MUST NOT:

- Include full task content in published artifacts without explicit user confirmation.
- Promote `tasks/` files themselves (they stay per-layer).

## Audit Trail

Every sensitive operation is logged (see [logging.md](logging.md)):

- Captures that the gate blocked or partially accepted.
- Promotions with the destination layer and contributor.
- Publishes with the skill name and the safety-check outcome.
- External integrations invoked.

## External Services

The spec treats external services as third parties:

- URLs in `sources.md` are checked for reachability, not content.
- The agent MUST inform the user when it is about to fetch an external URL, with the URL visible.
- External tool invocations (MCP, HTTP, CLI) are logged.

## Data Residency

`agentic-kb` doesn't require any external service. Everything is Git + Markdown + local agent. If the user wishes to keep data entirely offline, they MAY:

- Use a local Git remote (even `file://`).
- Disable marketplace auto-install (consume skills via a local clone).
- Disable L5 propagation (no polling of external sources).

## Incident Response

If a user discovers that sensitive content was inadvertently captured or promoted:

1. **Rotate any leaked credentials** immediately.
2. **Rewrite history** on affected repos (`git filter-repo` or equivalent) if the content is secrets; otherwise, commit a correction and a log entry.
3. **Notify** anyone who may have pulled the affected commits (team repos) or installed the affected skill (marketplace).
4. **Retrospect** in a finding in `references/findings/` so the failure mode is remembered.

## Related

- [marketplace-and-skills.md](marketplace-and-skills.md) §Safety Rules — per-skill rules.
- [../concept/08-evaluation-gate.md](../concept/08-evaluation-gate.md) — the gate that catches many safety issues early.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §15 |
