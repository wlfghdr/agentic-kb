# {{KB_NAME}}

{{USER_NAME}}'s personal knowledge base, built on the `agentic-kb` specification.

## Structure

```
.
├── _kb-inputs/             THE INBOX — drop anything here
├── _kb-references/
│   ├── topics/          living positions (updated in place)
│   ├── findings/        dated snapshots (immutable)
│   ├── foundation/      identity: me, context, stakeholders, sources
│   └── reports/         generated HTML artifacts
├── _kb-decisions/
│   ├── D-YYYY-MM-DD-slug.md  open decisions (one file each)
│   └── archive/         resolved or superseded
├── _kb-tasks/
│   ├── focus.md         max 3 items — what you're doing NOW
│   ├── backlog.md       queued up
│   └── archive/         monthly done archives
├── .kb-log/             dated processing log
├── .kb-scripts/         optional utility scripts
└── _kb-workstreams/         parallel tracks
```

## Commands

Everything runs through `/kb`. See `AGENTS.md` for rules; see the spec at <https://github.com/wlfghdr/agentic-kb> for the full command surface.

## Configuration

- `.kb-config/layers.yaml` — layer declaration, workspace aliases, VMG
- `.kb-config/automation.yaml` — automation level + schedules
- `.kb-config/artifacts.yaml` — HTML artifact styling

## Quickstart

- `/kb start-day` — morning briefing
- `/kb [paste text or URL]` — capture
- `/kb review` — process pending inputs
- `/kb end-day` — wrap and commit
