# Decisions

> **Version:** 0.1 | **Last updated:** 2026-04-18

Decisions are **first-class objects** in personal, team, and org-unit KBs. They surface whenever KB processing reveals a choice point — a strategic direction, a tactical move, a technical question that needs an answer.

Each decision lives in its own file. Each has a lifecycle, stakeholders (and, outside personal, a RACI), an evidence trail, and an outcome on resolution.

## Structure: `decisions/`

```
decisions/
├── active/                     # open decisions — one file each
│   ├── D-2026-04-18-agent-coordination.md
│   └── D-2026-04-15-pricing-model.md
└── archive/                    # two-stage archive
    ├── D-2026-04-trust-model.md   # resolved: outcome recorded
    ├── D-2026-03-lane2-scope.md   # resolved
    └── D-2026-02-old-api.md       # outdated/superseded
```

## Individual Decision File

Path: `decisions/active/D-YYYY-MM-DD-slug.md`

```markdown
# D-2026-04-18: Agent coordination model

- **Context**: Two competing approaches found (findings/2026-04-18-agent-coordination.md)
- **Options**: (a) hierarchical delegation, (b) peer-to-peer negotiation
- **Stakeholders**: @alice (architecture), @bob (incident-agent)
- **Blocking**: topic update to agentic-enterprise, sprint planning
- **Due**: 2026-04-25
- **Status**: gathering-evidence

## Evidence Trail
- 2026-04-18: Initial trigger — findings/2026-04-18-agent-coordination.md
- 2026-04-20: @alice favors option (b), cites scalability concerns
```

### Decision states

```
gathering-evidence  →  under-discussion  →  proposed  →  decided
                                                             │
                                                             ▼
                                                   revisiting (rare)
```

### Two-stage archive

When a decision is **resolved**:

1. Move from `active/` to `archive/` with the outcome + rationale appended.
2. Add a `## Resolution` section: outcome, rationale, date.
3. Update all affected topic files with a changelog entry: *"Decision D-YYYY-MM-DD resolved: [outcome]"*.
4. Remove or complete related TODOs.
5. Suggest next steps (e.g., "announce the decision to stakeholder X?").

When a decision becomes **outdated** (overruled, no longer relevant, superseded):

1. Move from `active/` to `archive/` with a `## Superseded` note.
2. No topic updates needed — the decision was never resolved, just became irrelevant.

## How Decisions Are Created

Decisions are **not manually drafted in isolation** — they emerge from KB processing:

| Trigger | Decision created when… |
|---------|------------------------|
| `/kb review` | An input contains competing options or an unresolved question |
| `/kb digest team` | Contributor positions contradict or a new direction is proposed |
| `/kb sync team` | Cross-referencing reveals conflicting stances on the same topic |
| `/kb audit` | A topic has ambiguous language ("we could", "TBD", "open question") |
| Manual | User says "this needs a decision" or runs `/kb decide [description]` |

## Decisions in Team and Org-Unit KBs — RACIs

Team and org-unit decisions follow the same structure but **require a RACI**:

```markdown
# D-2026-04-18: API versioning strategy

- **Context**: Breaking change needed for v3 API
- **RACI**:
  - Responsible: @alice
  - Accountable: @bob
  - Consulted: @carol, @dave
  - Informed: @eve (downstream consumer)
- **Options**: (a) version header, (b) URL versioning, (c) content negotiation
- **Due**: 2026-05-01
- **Status**: under-discussion
```

In the personal KB, stakeholders are listed but a formal RACI is not mandatory — it's your own decision space.

## Why Individual Files?

An earlier design kept all open decisions in a single `open.md`. That model does not scale:

- Search is awkward (grep inside a large file vs. list files).
- Archival is awkward (moving a section vs. moving a file).
- Git history is noisy (every change to any decision touches the same file).
- Multiple agents cannot work on different decisions concurrently without conflicts.

One-file-per-decision keeps history clean, makes the RACI machine-readable, and makes the archive meaningful.

## See Also

- [05-todos.md](05-todos.md) — open decisions generate TODOs for evidence-gathering and stakeholder follow-up.
- [07-stakeholders.md](07-stakeholders.md) — how the people map drives RACI suggestions.
- [09-flows.md](09-flows.md) — how decisions propagate from `active/` → topic updates → archive.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §3f |
