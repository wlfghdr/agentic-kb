# Flows — Promotion, Digest, Publish, Propagate

> **Version:** 0.1 | **Last updated:** 2026-04-18

Content moves between layers via a small set of named flows. Every flow passes through the [evaluation gate](08-evaluation-gate.md).

## Summary

| Flow | Direction | Command | Gate |
|------|-----------|---------|------|
| **Capture** | external → L1 | `/kb [text/URL/path]` | Relevance to declared themes |
| **Promote** | L1 → L2 | `/kb promote [file]` | Team-relevant, decision-ready |
| **Promote org** | L2 → L3 | `/kb promote org [file]` | Cross-team relevance |
| **Publish** | L1/L2/L3 → L4 | `/kb publish [file]` | Generalizable, safe, reusable |
| **Digest team** | L2 → L1 | `/kb digest team` | Position-changing signal |
| **Digest org** | L3 → L1 | `/kb digest org` | Position-changing signal |
| **Install** | L4 → harness | `/kb install [skill]` | Marketplace-approved |
| **Propagate** | L5 → L1 | `/kb [capture]` | Relevance to themes |
| **Develop** | within layer | `/kb develop [idea]` | Sparring: assumptions, contradictions, gaps |

## Personal → Team (promote)

```
my-kb/references/findings/2026-04-15-coordination-patterns.md
  → /kb promote
    → team-kb/alice/inputs/2026-04-15-coordination-patterns.md
```

**Gate**: Is this decision-ready? Evidence-backed? Relevant to the team's mandate? Would it change someone's position or inform an open decision?

## Team → Personal (digest)

```
team-kb/bob/outputs/findings/*   (new since last digest)
team-kb/bob/outputs/topics/*     (changed since last digest)
  → /kb digest team
    → my-kb/references/findings/2026-04-18-strategy-contrib-digest.md
```

**Mechanism**: git diff since the watermark commit. Per-contributor breakdown. The agent flags new or changed decisions, position shifts, and stakeholder implications.

## Team → Org-Unit (promote)

```
team-kb/alice/outputs/topics/governance-framework.md  (mature)
  → /kb promote org
    → org-unit-kb/inputs/2026-04-18-governance-framework.md
```

**Gate**: Cross-team relevance? Multiple teams affected? Needs org-level decision or coordination?

## Personal/Team → Marketplace (publish)

```
my-kb/references/topics/incident-investigation-workflow.md  (mature)
  → /kb publish
    → Extract reusable instructions
    → marketplace/skills/<name>/SKILL.md  (opens a PR)
```

**Gate**: Generalizable beyond the contributor's personal context? Would others benefit? Does it follow skill safety rules? Only marketplace-available tools referenced?

Details of the packaging format: [../spec/marketplace-and-skills.md](../spec/marketplace-and-skills.md).

## Marketplace → Personal (install)

```
marketplace/plugins/<name>/
  → /kb install <name>
    → Harness-specific install target (VS Code, Claude Code, OpenCode)
```

This is handled by the marketplace's install mechanism (see [../spec/marketplace-and-skills.md](../spec/marketplace-and-skills.md)). No new flow is needed on the KB side.

## Company → Personal (propagate)

```
Company strategy deck / directive / OKR update
  → /kb capture (paste or link)
    → my-kb/inputs/2026-04-18-company-strategy-update.md
    → Agent processes against themes, flags relevant signals
```

L5 content flows **down**. The user captures it like any other input; the agent assesses relevance to workstreams, open decisions, and themes.

## Why Flows Are Named and Small

- Named flows make intent auditable in the `log/`.
- A small set (8 total) keeps the mental model light.
- Each flow has exactly one gate invocation — no hidden logic.
- Undoing a flow is always possible: the source never disappears; the destination is just an additional file.

## See Also

- [../spec/commands.md](../spec/commands.md) — the command surface in full.
- [../spec/rituals.md](../spec/rituals.md) — how daily/weekly rituals invoke these flows.
- [../spec/logging.md](../spec/logging.md) — how flows are recorded.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §2 |
