# Roadmap & Open Questions

> **Version:** 2.1 | **Last updated:** 2026-04-18

This document tracks the known open items, deferred decisions, and future improvements for the `agentic-kb` spec. It is intentionally **living** — contributors add items, the maintainers resolve them or mark them deferred.

## Near-Term (v2.1)

### Reference implementation completion

- [x] Skill `kb-management` scaffolded in this repo's `skills/kb-management/` — full processing logic.
- [x] Skill `kb-setup` scaffolded in this repo's `skills/kb-setup/` — full onboarding wizard.
- [x] Agent `kb-operator` scaffolded in `agents/kb-operator.md`.
- [x] Plugin generator scaffolded in `scripts/generate_plugins.py`.
- [ ] Walk-through tests against a simulated workspace.

### Template hardening

- [ ] Built-in HTML artifact template with light/dark + toggle + watermark + changelog appendix.
- [ ] Validation of HTML artifacts in CI (`scripts/check_html_artifacts.py` — placeholder provided).
- [ ] A minimal example marketplace repo consumers can clone and extend.

### Auto-regeneration of always-current overviews

- [ ] After every state-mutating `/kb` operation, regenerate `inventory.html`, `open-decisions.html`, `open-todos.html`, and `index.html` automatically (today: manual via `/kb status --refresh-overviews` or ritual commands).
- [ ] Automation-level behavior: Level 1 asks before regenerating; Level 2 bundles with the commit; Level 3 runs silently in the autonomous loop.
- [ ] Deterministic rendering contract so CI can diff against a fixture.

Blocks the full promise of `docs/spec/html-artifacts.md` §Family 1. Until this ships, the "refresh trigger" column there is aspirational.

## Medium-Term (v3)

### Issue-tracker backbone for tasks and decisions

Today, TODOs and decisions live as files. A future option is to back them with an issue-tracking system — GitHub Issues + Projects being the most common choice.

Goals:

- `todo/focus.md` and `todo/backlog.md` become views on top of issues with a specific label set.
- `decisions/active/*.md` back onto issues with a `decision` label and the decision state as a project field.
- RACI is preserved via issue assignees and `@` mentions in comments.
- Cross-layer references: team KB issues cross-link to personal KB issues via `parent:` syntax.

Open questions:

- How does offline work reconcile when the user is disconnected?
- Does the spec prescribe a specific project template, or stay tracker-agnostic?
- Do decision files remain the source of truth, or the issue body?

This is a **significant change** and will be MAJOR when added. It is deferred until the file-backed implementation is stable.

### Cross-org coordination

When multiple org-units (L3) need alignment, how does that propagate?

- **Today**: manual via L4 marketplace or shared meetings.
- **Future**: org-wide digest mechanism — a "meta-org" layer that aggregates across org-units.

Deferred until at least two real org-unit KBs exist in a production deployment.

### L5 automation

How to automatically detect and ingest company-wide signals (OKRs, strategy decks)?

- **Today**: manual capture.
- **Future**: polling integration with company communication channels; rule-based ingestion.

Blocked on standard formats for company comms — not every org publishes strategy in a machine-readable way.

## Long-Term

### Knowledge graph

Findings and topics form an implicit graph (topic → finding → stakeholder → decision). A visualization layer could render this graph interactively.

- No commitment yet. Interesting exploration.

### Conflict resolution across contributors

When team contributors' topic positions contradict, how does the agent surface this?

- **Today**: manual cross-reference via `/kb sync team`.
- **Future**: automated contradiction detection across `*/outputs/topics/`.

Requires reliable semantic similarity — adjacent to the work on topic embeddings.

### Embedding-assisted routing

Today, workstream routing is theme-keyword based. Embedding-assisted routing would:

- Cluster findings by similarity.
- Suggest new workstreams when a cluster emerges.
- Find cross-workstream connections automatically.

Adds a runtime dependency (an embedding model). Deferred until the keyword-based approach is proven insufficient.

## Explicitly Out of Scope

The following are **not** intended to be part of this spec:

- **A specific hosted product.** This spec is implementation-agnostic.
- **A UI.** The spec is terminal- and editor-first. Visualizations may come later as artifacts.
- **A proprietary file format.** Everything is Markdown, YAML, or generated HTML.
- **Billing, licensing, telemetry.** Spec repo and reference implementation are open source.

## How to Propose Additions

1. Open an issue with the `spec-proposal` label.
2. Describe the problem being solved, not the solution first.
3. Reference existing sections this would change.
4. State whether the change is PATCH, MINOR, or MAJOR.
5. If accepted, the change lands in an `Unreleased` section of [CHANGELOG.md](../CHANGELOG.md) and moves here when it ships.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version; tracks near/medium/long-term items including issue-tracker backbone deferred future | New |
| 2026-04-18 | v2.1 — added "Auto-regeneration of always-current overviews" to near-term items after the adopter feasibility review flagged it as a spec-ahead-of-implementation gap | Adopter feasibility review |
