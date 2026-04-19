# The Evaluation Gate — kb-management

Applied at **every persistence boundary**. The gate is the system's immune system.

## The five questions

1. **Does this strengthen a position?** (topic update?)
2. **Does this inform a decision?** (open or emerging?)
3. **Would the user reference this again?** (durable signal or passing observation?)
4. **Is this actionable?** (TODO, meeting, promotion?)
5. **Does this already exist?** (topic already covers it?)

## Scoring

| Matches | Outcome | Log op |
|---------|---------|--------|
| 0 | Discard; log reason | `skipped` |
| 1–2 | Finding only | `capture` |
| 3+ | Finding + topic update + possibly decision | `capture` + `update-topic` (+ optional `decide`) |

## Applied per stage

| Stage | Focus |
|-------|-------|
| Capture (`/kb [input]`) | Relevance to declared themes |
| Digest (`/kb digest team`) | What changed the user's position? |
| Promote (`/kb promote`) | Team-relevant? Evidence-backed? Decision-ready? |
| Review in team context | Strategic value, wrong-direction risk, cross-reference |
| Publish (`/kb publish`) | Generalizable? Safe? Reusable? Marketplace-tools only? |

## Transparency rules

For every gate decision, log:

- Which questions matched (e.g., "1,3,4").
- Action taken.
- One-sentence rationale.

Example log line:

```
14:22:11Z | skipped | personal | _kb-inputs/2026-04-18-meeting-notes.md | gate 1/5 — strengthens position but not actionable, already captured in topic
```

## User override

The gate is **not a hard blocker**. If the user insists after being told the rationale, persist with a `low-confidence` note in the finding. Log the override.

## Examples

### 5/5 — clear accept

*"Paper proposes 3-phase coordination protocol for multi-agent systems."*

- ✅ strengthens deployment-strategy topic
- ✅ informs D-2026-04-18 (coordination model)
- ✅ durable signal
- ✅ actionable ("update topic")
- ❌ not already captured

→ Finding + topic update + decision evidence trail entry.

### 1/5 — finding only

*"Interesting tweet about a vendor launching a new CLI."*

- ❌ no direct position change
- ❌ no decision impact
- ✅ might be worth revisiting
- ❌ not actionable today
- ❌ not already captured

→ Finding only, low signal.

### 0/5 — discard

*"Meeting was rescheduled."*

- ❌ all five

→ Skipped. Log: `gate 0/5 — logistical noise`.
