# Roadmap

What's next, what's deferred, what's out of scope.

## Next

- [x] Walk-through tests against a simulated workspace
- [x] HTML artifact CI validation (self-contained, dual theme, watermark)
- [x] Auto-regeneration of overview dashboards after every `/kb` mutation
- [x] Export-backed roadmap proof fixture and regression test
- [ ] [Tracker-backed primitive onboarding](../plugins/kb/skills/kb-management/references/tracker-backed-primitives.md), including the [GitHub governance profile](../plugins/kb/skills/kb-setup/references/github-governance-profile.md), for teams using issue trackers as the operational backbone
- [ ] Example marketplace repo that consumers can clone and extend

## Later

- **Tracker write-back hardening** — broader write-back fixtures for tracker-backed decisions, tasks, ideas, feedback, and feature intake after the proposal is tested with adopter repos.
- **Cross-org coordination** — digest mechanism across multiple peer org-unit layers. Deferred until real deployments exist.
- **Company-source automation** — polling company channels for OKRs/strategy. Blocked on machine-readable company comms.
- **Knowledge graph visualization** — interactive rendering of the finding→topic→decision graph.
- **Layered roadmaps and journeys** — roll-ups, inheritance, and cross-layer readiness aggregation across roadmap and journey owners. Deferred until the single-owner setup path is proven in adopter KBs.
- **Contradiction detection** — automated surfacing of conflicting positions across team contributors.
- **Embedding-assisted routing** — semantic clustering instead of keyword-based workstream routing.

## Out of Scope

- A hosted product (this is implementation-agnostic)
- A UI (terminal- and editor-first)
- A proprietary file format (Markdown, YAML, generated HTML only)
- Billing, licensing, telemetry (open source)

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-17 | Expanded the open tracker-backed onboarding item to include the generic GitHub governance profile, not just primitive storage and provider mappings | Tracker-backed onboarding hardening |
| 2026-05-17 | Reworded the current tracker-backed work from proposal-only to onboarding: the open item now covers setup decisions, `primitive-storage`, and generic GitHub/Jira setup outcomes while broader write-back hardening remains later | Tracker-backed onboarding design |
| 2026-05-17 | Moved the issue-tracker backbone idea from a host-specific later item to a generic tracker-backed primitive proposal and named write-back hardening as the later implementation work | Cross-repo tracker-backbone review |
| 2026-04-30 | Added layered roadmap and journey roll-ups as a later enhancement, keeping the current product-management setup path focused on one confirmed owning layer | Product-management surface integration |
| 2026-04-24 | Marked the export-backed roadmap proof fixture as delivered via the new roadmap regression test | Roadmap proof hardening |
| 2026-04-20 | Marked simulated-workspace tests, HTML artifact CI validation, and automatic overview regeneration as delivered | v3.2.0 roadmap sync |
