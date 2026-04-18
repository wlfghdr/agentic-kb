# File Formats — Templates & Conventions

> **Version:** 0.1 | **Last updated:** 2026-04-18

This document lists the canonical file formats for every file type the agent creates. Implementations are free to ship their own templates — they just have to produce files that match these shapes.

## Finding

Path: `references/findings/YYYY-MM-DD-slug.md`

```markdown
# Finding: <short title>

**Date**: 2026-04-18
**Workstream**: reliability
**Source**: https://example.org/paper-xyz  (or: "Meeting: 2026-04-18 architecture review")
**Gate**: 3/5 (informs a position + strengthens a decision + actionable)

## TL;DR

One to three sentences.

## Details

[... the distilled content ...]

## Implications

- Updates topic: `../topics/deployment-strategy.md`
- Advances decision: D-2026-04-18
- Adds TODO: "Integrate pattern into core-topics"

## Stakeholders

- @alice — architecture implication
- @bob — ops implication
```

**Rules**: immutable after creation. Any correction creates a new finding that references this one.

## Topic

Path: `references/topics/<slug>.md`

```markdown
# Topic: <theme name>

**External anchors**:
- Dashboard: [dashboard-x]
- Runbook: [runbook-y]

[... living prose, updated in place ...]

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Added coordination-patterns evidence | findings/2026-04-18-coordination-patterns.md |
| 2026-04-10 | Initial position | findings/2026-04-10-initial.md |
```

**Rules**: one file per topic; never duplicate; inline changelog required; read up to the final `---` when only the current position is needed.

## Foundation File (me, context, stakeholders, sources, naming)

Same inline-changelog convention as topics.

## Decision

Path: `decisions/active/D-YYYY-MM-DD-slug.md`

```markdown
# D-2026-04-18: <decision title>

- **Context**: <why this choice is open>
- **Options**: (a) …, (b) …, (c) …
- **Stakeholders**: @alice, @bob
- **RACI** (team/org only):
  - Responsible: @alice
  - Accountable: @bob
  - Consulted: @carol
  - Informed: @dave
- **Blocking**: topic updates, sprint planning, …
- **Due**: 2026-04-25
- **Status**: gathering-evidence | under-discussion | proposed | decided | revisiting

## Evidence Trail

- 2026-04-18: Initial trigger — findings/2026-04-18-xxx.md
- 2026-04-20: @alice favors (b), cites findings/2026-04-20-yyy.md

## Resolution (on archive only)

- **Outcome**: (b) peer-to-peer negotiation
- **Rationale**: scales to >5 agents without central bottleneck
- **Date**: 2026-04-25
```

## Workstream

Path: `workstreams/<name>.md`

```markdown
# Workstream: <name>

**Themes**: <keyword list>
**Active decisions**: <D-id list>
**Key topics**: <file list>

## Current State
<one short paragraph>

## Active Threads
- <thread>: <short line>

## Cross-Workstream Dependencies
- Depends on <other>: <reason>
- Informs <other>: <reason>
```

## Focus / Backlog

Path: `todo/focus.md`, `todo/backlog.md`

```markdown
# Focus

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Waiting

- [ ] @person: what they owe you
```

Team/org variant uses the RACI prefix — see [../concept/05-todos.md](../concept/05-todos.md).

## Log

Path: `log/YYYY-MM-DD.log`

Each line:

```
HH:MM:SSZ | operation | scope | target | details
```

See [logging.md](logging.md) for the full field spec.

## Configuration Files

### `.kb-config.yaml`

See [../concept/02-architecture.md](../concept/02-architecture.md).

### `.kb-automation.yaml`

See [automation.md](automation.md).

### `.kb-artifacts.yaml`

See [html-artifacts.md](html-artifacts.md).

## Templates Shipped by the Skill

The `kb-setup` skill ships minimal templates for every file type above, plus:

- `workspace-AGENTS.md` (the root index)
- `personal-kb-AGENTS.md`
- `personal-kb-README.md`
- `team-kb-AGENTS.md`
- `team-kb-README.md`
- `org-kb-AGENTS.md`
- `org-kb-README.md`
- `kb.prompt.md`
- `kb.instructions.md`

Template content is the skill's responsibility; the shape is this spec's.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec — templates section |
