# Workstreams

> **Version:** 0.1 | **Last updated:** 2026-04-18

A personal KB can track multiple parallel **workstreams**. Each workstream has its own file in `workstreams/` that summarizes the current state, active threads, and dependencies.

Workstreams serve two purposes:

1. **Routing** — the agent auto-routes captured inputs to the right workstream based on theme keywords.
2. **Visibility** — the briefing groups signals, tasks, and decisions by workstream, so a user with three parallel tracks can see each one cleanly.

## File Layout

```
workstreams/
├── reliability.md         ← SLOs, incident management, postmortems
├── platform.md            ← deployment, pipeline, tooling
└── product-strategy.md    ← roadmap, positioning, stakeholder alignment
```

## Workstream File Format

```markdown
# Workstream: Reliability

**Themes**: slo, incident, postmortem, error-budget
**Active decisions**: D-2026-04-18-agent-coordination
**Key topics**: core-topics.md (§ Agentic Patterns), platform-direction.md

## Current State

Brief summary of where this workstream stands.

## Active Threads

- Thread A: investigating coordination protocols
- Thread B: drafting governance v5

## Cross-Workstream Dependencies

- Depends on product-strategy for roadmap positioning
- Informs platform for observability requirements
```

## Declared in Config

Workstreams are registered in `.kb-config.yaml`:

```yaml
layers:
  personal:
    path: .
    workstreams:
      - name: reliability
        themes: [slo, incident, postmortem]
      - name: platform
        themes: [deploy, pipeline, tooling]
```

The `themes` array drives routing: captured content is analyzed against these keywords (plus embeddings if available) to pick the workstream.

## How Workstreams Are Used

| When | What happens |
|------|--------------|
| **Input capture** | Agent analyzes content, routes to the matching workstream(s) based on themes |
| **Start-day** | Briefing groups signals by workstream |
| **Cross-workstream** | Agent surfaces connections: *"This finding affects both reliability AND platform"* |
| **Promote** | Agent suggests which team KB to promote to based on workstream alignment |
| **Weekly summary** | Per-workstream progress summary |

## Dynamic Workstream Suggestion

If the agent detects a cluster of inputs that don't fit any existing workstream — say, ≥3 findings on a new theme within two weeks — it suggests creating a new workstream. The user confirms; the agent scaffolds the new `workstreams/<name>.md` and updates `.kb-config.yaml`.

## Keeping Workstreams Lean

- One paragraph of "Current State" — more goes in topic files.
- "Active Threads" is a pointer list, not a narrative.
- "Cross-Workstream Dependencies" is a bulleted set of one-liners.
- When a workstream goes quiet (no updates for 60+ days), `/kb audit` flags it for possible archival to `workstreams/legacy/`.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §3h |
