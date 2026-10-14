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

- **Tracker adapter hardening** — broader canonical CRUD fixtures for tracker-backed decisions, tasks, ideas, feedback, and feature intake after the ownership/capability/authentication/confirmation contract is tested with adopter repos. Connection-digest write-back remains a separate reserved capability.
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
