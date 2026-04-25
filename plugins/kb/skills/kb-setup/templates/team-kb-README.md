# {{TEAM_NAME}} — Team KB

Shared knowledge base for the {{TEAM_NAME}} team, built on the `agentic-kb` specification.

## Structure

```
.
├── _kb-notes/
├── _kb-decisions/
│   ├── D-YYYY-MM-DD-slug.md  open decisions with RACIs
│   └── archive/
├── _kb-tasks/
│   ├── focus.md              team focus (with RACIs)
│   └── backlog.md
├── .kb-log/                  team processing log
└── <contributor>/
    ├── _kb-inputs/
    │   └── digested/YYYY-MM/
    └── _kb-references/
        ├── topics/           living team-facing positions
        └── findings/         dated analyses / reviews
```

## Contributor workflow

1. Add material directly in the team repo by dropping it into your own `<contributor>/_kb-inputs/`.
2. Run `/kb review` in the team KB context only for material that originated inside the team repo.
3. When a finding or topic comes from another contributor-capable layer, use `/kb promote <file> {{TEAM_NAME}}`. That command stages the intake, performs the team-layer review immediately, archives the staged copy under `digested/YYYY/MM/`, and leaves the reviewed result in `_kb-references/`.
4. Cross-reference other contributors via `/kb sync {{TEAM_NAME}}`.
5. Promote mature topics or findings upward with `/kb promote <file> <parent-layer>` when the layer graph defines one.

## Decisions & Tasks

Every team decision and task carries a RACI (Responsible, Accountable, Consulted, Informed).
