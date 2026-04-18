# Processing Log

> **Version:** 0.1 | **Last updated:** 2026-04-18

Every KB operation is recorded in a dated log file. The log is the **primary source of truth** for "what happened and when" — it is what the agent reads on `start-day` to pick up where yesterday left off.

## Structure

```
log/
├── 2026-04-18.log     # current day — always in context
├── 2026-04-17.log     # yesterday — in context
└── 2026-04-16.log     # older — on disk, NOT loaded
```

**Retention**: the current day and the previous day are loaded into the agent's context. Older files remain on disk for audit and search but don't consume context tokens.

## Line Format

```
HH:MM:SSZ | operation | scope | target | details
```

All timestamps are UTC.

### Example

```
09:15:00Z | digest    | team-kb       | alice/outputs/backend-v9.md         | 3 new files since 2026-04-16
08:30:00Z | capture   | personal      | inputs/2026-04-18-patterns.md       | from URL
17:00:00Z | promote   | personal→team | findings/2026-04-17-patterns.md     | → team-kb/me/inputs/
17:30:00Z | skipped   | personal      | inputs/2026-04-18-random-quote.md   | gate: 0/5 — no theme match
```

## Field Dictionary

| # | Field | Description |
|---|-------|-------------|
| 1 | Time | `HH:MM:SSZ` (date is in the filename) |
| 2 | Operation | `capture`, `digest`, `publish`, `promote`, `update-topic`, `todo-add`, `todo-done`, `decide`, `decide-resolve`, `audit`, `report`, `presentation`, `skipped`, `install`, `ritual-start-day`, `ritual-end-day`, `ritual-start-week`, `ritual-end-week`, `automation-failure` |
| 3 | Scope | `personal`, `team-kb`, `org-unit`, `marketplace`, `personal→team`, `team→personal`, `personal→marketplace`, `team-kb/<contributor>`, `workspace` |
| 4 | Target | File path or short description |
| 5 | Details | Free-form context, including gate rationale for `skipped` operations |

## How the Agent Uses the Log

| Invocation | Log usage |
|-----------|-----------|
| `/kb status` | Reads current day's log for recent activity. |
| `/kb start-day` | Compares log timestamps with git log to find unprocessed changes. |
| `/kb digest team` | Uses log + git diff to determine what's new since last processing. |
| `/kb todo` auto-feed | New items are logged as `todo-add`. |
| `/kb audit` | Searches log for patterns (failed gates, skipped items, stale topics). |

## Append-Only

Log files are append-only. Corrections go into a new line with `operation = correction` and a reference to the incorrect line's timestamp.

## Watermarks

The log is the primary watermark for "what's new" computations. Secondary watermarks:

| Watermark | Location | Tracks |
|-----------|----------|--------|
| `log/YYYY-MM-DD.log` last entry | Personal KB `log/` | Last processing of any kind |
| `.last-digest` | Personal KB `references/strategy-digests/` | Last team → personal digest |
| Git commit timestamps | Each repo | Ground truth for all diffs |

## Size Management

- Logs are never rotated or deleted automatically.
- The agent only reads the current and previous day's files — old logs have no context cost.
- If a user wants to archive very old logs (e.g., >1 year), they MAY move them to `log/archive/` manually.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §5 |
