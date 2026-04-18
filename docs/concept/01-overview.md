# Overview — Principles & Mental Model

> **Version:** 0.1 | **Last updated:** 2026-04-18

`agentic-kb` is a **five-layer knowledge management system** driven by AI agents. Individuals, teams, and organizations keep their knowledge lean, decision-ready, and auto-routed, using only Git, Markdown, and a small set of portable skills.

## The Core Idea

Most knowledge bases accumulate. `agentic-kb` curates. Every piece of material passes a five-question gate before it persists. Themes, decisions, and stakeholders drive what is kept and what is discarded. Agents do the bookkeeping so humans do the thinking.

## Core Principles

1. **Lean by default.**
   Every piece of content earns its place. The agent applies a critical evaluation gate at capture, digest, promote, and publish. Growing KBs become growing context windows become slower agents.

2. **Signal over noise.**
   Relevance is assessed against declared themes and open decisions. "Interesting" is not enough. The bar is: *would you reference this again?*

3. **Decisions as first-class objects.**
   Strategic, tactical, and technical decisions are tracked explicitly — not buried in prose. Open decisions drive TODOs. Decided items ground future processing. Each decision lives in its own file.

4. **Stakeholders inform action.**
   Knowing who cares about what enables the agent to suggest meetings, messages, and reviews. Not a CRM — just enough to connect decisions to people. Outside the personal KB, TODOs carry RACIs.

5. **Always offer next steps.**
   After every operation, the agent suggests concrete follow-up actions. Never leave the user staring at output without a path forward.

6. **Multiple workstreams.**
   A personal KB can track multiple parallel workstreams. The agent auto-routes content to the right workstream and reveals cross-workstream connections, synergies, and dependencies.

7. **Presentation-ready.**
   When work needs to be communicated, the agent generates versioned HTML artifacts (presentations, reports, pitches) with light/dark themes and subtle version watermarks. See [HTML artifacts spec](../spec/html-artifacts.md).

## Mental Model — One Picture

```
          ┌───────────────┐  promote   ┌───────────────┐  promote   ┌───────────────┐
   You →  │   L1 Personal │ ─────────► │    L2 Team    │ ─────────► │  L3 Org-Unit  │
          │  (required)   │ ◄───────── │  (optional)   │ ◄───────── │  (optional)   │
          └───────────────┘   digest   └───────────────┘   digest   └───────────────┘
                  │                                                        │
                  │ publish                                                │ publish
                  ▼                                                        ▼
          ┌─────────────────────────────────────────────────────────────────┐
          │                    L4  Skills Marketplace                       │
          │        (reusable AI capabilities shared across teams)           │
          └─────────────────────────────────────────────────────────────────┘
                  ▲
                  │  consume
                  │
          ┌─────────────────────────────────────────────────────────────────┐
          │       L5  Company-wide signals (strategy, OKRs, directives)     │
          │                   → propagated top-down                         │
          └─────────────────────────────────────────────────────────────────┘
```

- Only **L1 (Personal)** is required. All higher layers are optional and declared in the personal KB's configuration.
- Content flows **up** via *promote* / *publish*, and flows **down** via *digest* / *propagate*.
- **L5 is consumption-only** from an individual's perspective — you don't push to L5, you ingest from it.

## What the Agent Does (and Doesn't Do)

| Agent does | Agent does not |
|------------|----------------|
| Route captures to the right workstream and layer | Decide what's strategically important |
| Apply the critical evaluation gate | Silently discard material — always logs why |
| Maintain topic files, findings, decisions, todos | Auto-commit to team or org without confirmation |
| Generate digests, summaries, presentations | Send messages to stakeholders on the user's behalf |
| Suggest next steps | Execute risky next steps without approval |

Full behavior contract: [`docs/spec/commands.md`](../spec/commands.md).

## Example Framing (Illustrative)

Throughout this spec, examples use the framing of an *observability platform R&D organization* — engineers writing code, running services, capturing runtime evidence, coordinating across teams, and shipping incremental changes. The framing is illustrative only. None of the rules, structures, or commands are specific to that domain.

## Where Next

- [02-architecture.md](02-architecture.md) — the five layers in detail
- [03-memory-model.md](03-memory-model.md) — findings vs topics vs foundation
- [08-evaluation-gate.md](08-evaluation-gate.md) — the five-question filter
- [../spec/commands.md](../spec/commands.md) — the full `/kb` surface

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Spec bootstrapping |
