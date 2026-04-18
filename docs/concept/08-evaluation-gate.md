# The Critical Evaluation Gate

> **Version:** 0.1 | **Last updated:** 2026-04-18

The single mechanism that keeps every KB from rotting. Applied at **every stage** — capture, digest, promote, process, publish — the gate is the KB's immune system.

## The Five Questions

Before persisting anything, the agent asks:

1. **Does this strengthen a position?** — Does it change or reinforce a topic file?
2. **Does this inform a decision?** — Does it provide evidence for an open or emerging decision?
3. **Would you reference this again?** — Is it durable signal, or a passing observation?
4. **Is this actionable?** — Does it lead to a concrete next step (TODO, meeting, promotion)?
5. **Does this already exist?** — Is the insight already captured in a topic or recent finding?

## Scoring

| Matches | Outcome |
|---------|---------|
| 0 of 5 | Discard. Log as `skipped` in today's log with the reason. |
| 1–2 of 5 | Finding only. Snapshot to `findings/`, no topic update. |
| 3+ of 5 | Finding + topic update + possibly a new decision. |

The gate is **not a blocker**. The agent can persist with a lower confidence note if the user insists — but it always tells the user *why* it thinks something is or isn't worth keeping.

## Applied at Each Stage

| Stage | What gets filtered | What the gate checks |
|-------|-------------------|----------------------|
| **Capture** (`/kb [input]`) | Raw material | Relevance to declared themes. Skip noise. |
| **Digest** (`/kb digest team`) | Others' contributions | What changed *your* position? Skip "more of the same". |
| **Promote** (`/kb promote`) | L1 → L2 | Team-relevant? Evidence-backed? Decision-ready? |
| **Team process** (`/kb review` in team context) | Your inputs in team space | Review gate: strategic value, wrong-direction risk, cross-reference. |
| **Publish** (`/kb publish`) | Team/personal → marketplace | Generalizable? Safe? Reusable? Only marketplace-available tools? |

## Why This Gate Exists

- **Growing KBs become growing context windows** — every extra doc slows agent reasoning and inflates cost.
- **Unfiltered capture breeds distrust** — if the KB contains noise, users stop trusting it, stop consulting it, and stop maintaining it.
- **Decisions require signal** — vague material doesn't resolve open decisions, it just extends them.

The gate is why `agentic-kb` is a knowledge **operations** framework, not a knowledge **archive**.

## Transparency

For every gate decision, the agent logs:

- Which of the five questions matched,
- What action was taken (finding / topic update / decision creation / skip),
- A one-sentence rationale.

See the `log/` format in [../spec/logging.md](../spec/logging.md).

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §3e |
