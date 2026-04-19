# {{ORG_UNIT_NAME}} — Org-Unit KB

Org-unit knowledge base for {{ORG_UNIT_NAME}}, built on the `agentic-kb` specification.

## Structure

```
.
├── _kb-decisions/
│   ├── active/          org-level decisions with cross-team RACIs
│   └── archive/
├── _kb-tasks/
│   ├── focus.md         org focus (with RACIs)
│   └── backlog.md
├── _kb-workstreams/         org-level workstream coordination
└── .kb-log/
```

## How it aggregates

- Team KBs promote mature topics/findings via `/kb promote org`.
- The org-unit processes incoming items with the same evaluation gate.
- Org-level decisions cascade back down to affected teams as RACI-Informed references.
