# {{ORG_UNIT_NAME}} — Org-Unit KB

Org-unit knowledge base for {{ORG_UNIT_NAME}}, built on the `agentic-kb` specification.

## Structure

```
.
├── decisions/
│   ├── active/          org-level decisions with cross-team RACIs
│   └── archive/
├── todo/
│   ├── focus.md         org focus (with RACIs)
│   └── backlog.md
├── workstreams/         org-level workstream coordination
└── log/
```

## How it aggregates

- Team KBs promote mature topics/findings via `/kb promote org`.
- The org-unit processes incoming items with the same evaluation gate.
- Org-level decisions cascade back down to affected teams as RACI-Informed references.
