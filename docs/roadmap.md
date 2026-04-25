# Roadmap

What's next, what's deferred, what's out of scope.

## Next

- [x] Walk-through tests against a simulated workspace
- [x] HTML artifact CI validation (self-contained, dual theme, watermark)
- [x] Auto-regeneration of overview dashboards after every `/kb` mutation
- [x] Export-backed roadmap proof fixture and regression test
- [ ] Example marketplace repo that consumers can clone and extend

## Later

- **Issue-tracker backbone** — _kb-tasks/_decisions backed by GitHub Issues + Projects. Deferred until file-backed workflow is proven.
- **Cross-org coordination** — digest mechanism across multiple peer org-unit layers. Deferred until real deployments exist.
- **Company-source automation** — polling company channels for OKRs/strategy. Blocked on machine-readable company comms.
- **Knowledge graph visualization** — interactive rendering of the finding→topic→decision graph.
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
| 2026-04-24 | Marked the export-backed roadmap proof fixture as delivered via the new roadmap regression test | Roadmap proof hardening |
| 2026-04-20 | Marked simulated-workspace tests, HTML artifact CI validation, and automatic overview regeneration as delivered | v3.2.0 roadmap sync |
