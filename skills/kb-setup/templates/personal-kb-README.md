# {{KB_NAME}}

{{USER_NAME}}'s personal knowledge base, built on the `agentic-kb` specification.

## Structure

```
.
├── .inputs/             THE INBOX — drop anything here
├── references/
│   ├── topics/          living positions (updated in place)
│   ├── findings/        dated snapshots (immutable)
│   ├── foundation/      identity: me, context, stakeholders, sources
│   └── reports/         generated HTML artifacts
├── .decisions/
│   ├── active/          open decisions (one file each)
│   └── archive/         resolved or superseded
├── .tasks/
│   ├── focus.md         max 3 items — what you're doing NOW
│   ├── backlog.md       queued up
│   └── archive/         monthly done archives
├── .log/             dated processing log
├── .kb-scripts/         optional utility scripts
└── workstreams/         parallel tracks
```

## Commands

Everything runs through `/kb`. See `AGENTS.md` for rules; see the spec at <https://github.com/wlfghdr/agentic-kb> for the full command surface.

## Configuration

- `.kb-config.yaml` — layer declaration
- `.kb-automation.yaml` — automation level + schedules
- `.kb-artifacts.yaml` — HTML artifact styling

## Quickstart

- `/kb start-day` — morning briefing
- `/kb [paste text or URL]` — capture
- `/kb review` — process pending inputs
- `/kb end-day` — wrap and commit
