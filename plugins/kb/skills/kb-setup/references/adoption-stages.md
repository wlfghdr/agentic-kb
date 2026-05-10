# Adoption Stages

> **Version:** 0.1.0 | **Last updated:** 2026-04-27

This reference defines the three adoption stages `agentic-kb` is designed for, the graduation criteria between them, and how the stages relate to automation levels.

It is normative for `kb-setup`: phase 1 question 8 ("operating context today") asks the user which stage they are at, and phase 3 question 12 labels the proposed scaffold with the matching stage so the user can see what the wizard inferred.

## Why staged adoption

Knowledge-ops fails the same way every time when teams skip stages: an audit-vacuum opens before the artifact chain is steady, agents act on stale or contradictory context, and humans rubber-stamp at gates because they never built the muscle to challenge agent output. The stages are not marketing levels; they are the order in which the failure modes are addressed.

The contract is the same at every stage. The agent simply does more of the filing work the higher you go.

## Stage 1 — Capture discipline (human-only baseline)

What it is: the team writes findings, decisions, briefs, specs, releases, and incidents into the `agentic-kb` directory contract by hand. No `/kb` agent is invoked in the loop. Markdown + git is the entire stack.

What it scaffolds:

- one contributor anchor layer,
- the minimum feature set the team actually authors today (typically `findings`, `topics`, `decisions`, `notes`, `tasks`, `foundation`),
- automation level **1** (manual only),
- no `connections:` write-back, no `auto-promote`, no draft features.

What it gives the team that they did not have before:

- a single durable place for decisions and findings that survives chat history,
- a foundation document (`me.md`, `context.md`, `vmg.md`, `stakeholders.md`, `sources.md`) that any future agent will be grounded by,
- audit trail in `.kb-log/` and git history for every change, before any agent ever runs,
- the same artifact shapes (`brief`, `spec`, `release`, `incident`) the team will use later when agents are added — so the upgrade is purely behavioral, not structural.

What it does not yet do:

- no evaluation gate firing on the user's behalf,
- no automatic promotion or digestion,
- no scheduled briefings.

Stage 1 is a valid stop. A team that wants the file contract and nothing else has finished, not half-installed the product.

## Stage 2 — Agent-assisted triage

What it is: the team turns on the `/kb` evaluation gate. Captures, promotions, and digests are routed through the agent, which proposes the action and waits for confirmation before persisting anything.

What it scaffolds:

- the Stage 1 baseline plus,
- automation level **1** kept, but the `/kb` slash command and feature-keyword triggers are wired into the harness,
- the kb-management "When to invoke" rule applies: any feature keyword without `/kb` still names the inferred flow and asks for confirmation,
- optionally, `connections:` for tracker exports if the team is reading from external sources.

What it gives the team:

- agent-proposed routing to topics, workstreams, and decisions,
- consistent evaluation gate scoring instead of ad-hoc filing,
- audit trail of every accept and reject with rationale.

What it still does not do:

- no scheduled rituals,
- no auto-promote,
- no autonomous loop.

## Stage 3 — Bounded autonomous knowledge ops

What it is: the team accepts that the agent runs the routine knowledge-ops on a schedule and only escalates to humans on exception. Promotion can fire on confidence threshold; digests run when parent layers move ahead of the local watermark; ritual artifacts (`start-day`, `end-week`) generate without being asked.

What it scaffolds:

- the Stage 2 baseline plus,
- automation level **2** (scheduled rituals/digests) or **3** (scheduled flows plus guarded auto-promote),
- `auto-promote` configuration with confidence threshold and excluded workstreams,
- exception escalation path declared (`notifications.channel` if applicable),
- live-overview regeneration treated as part of every mutation, not as a manual step.

What it gives the team:

- knowledge-ops as background work,
- humans review only flagged items, not every line,
- the human-decision surface narrows to scope, policy, risk, and exceptions.

What it requires before it is safe:

- the foundation, decision, and finding flows from Stage 1–2 must already be quiet, well-routed, and trusted,
- the team must have a reliable exception path (someone reads the escalations).

## Graduation criteria

A team is ready to advance to the next stage when all of the following are true. `kb-setup` phase 3 question 14 surfaces this list as informational defaults; the team can adjust it.

### Stage 1 → Stage 2

- four or more weeks of clean `.kb-log/` entries with no recurring auto-failure logs,
- at least one cross-layer promote completed by hand and reviewed by another contributor,
- `foundation/vmg.md` confirmed by at least one stakeholder,
- the team has agreed which feature keywords should fire the agent and which should not.

### Stage 2 → Stage 3

- four or more weeks at Stage 2 with the evaluation gate firing at least daily,
- decision lifecycle is healthy: nothing stuck in `under-discussion` longer than its declared due date without a human update,
- the team has run at least one full digest from a parent layer and at least one promote into a parent layer with explicit human approval,
- the exception channel (`notifications.channel` or its equivalent) has at least one named human owner.

## Mapping to automation levels

Adoption stage and automation level are related but not identical. Adoption stage describes the team's posture toward the agent; automation level is the configuration knob that enacts it.

| Stage | Typical automation level | Why |
|-------|--------------------------|-----|
| 1 | **1** (manual only) | The agent is not in the loop yet. |
| 2 | **1** (manual only) | The agent is in the loop, but every persistence step still waits for human confirmation. |
| 3 | **2** or **3** | Scheduled rituals/digests (level 2) or scheduled rituals plus guarded auto-promote on confidence (level 3). |

A Stage 1 team should never be configured at automation level 2 or 3, because there is no `/kb` invocation pattern for a schedule to fire from. A Stage 3 team should not be configured at automation level 1, because the autonomous-loop benefits never materialize. `kb-setup` phase 3 question 12 enforces this consistency in the proposal it shows the user.

## Mapping to repo-as-OS frameworks

`agentic-kb` is the knowledge-ops layer of an agentic enterprise. It owns Strategy, Design, and Learning artifacts (foundation, briefs, specs, decisions, findings, topics, reports). The work-flow primitives that surround it — signals, missions, pull requests, releases — belong to a separate, complementary framework that owns the Build / Ship / Operate side of the operating model.

When a repo-as-OS structure is detected during phase 2 question 11 (typical signals: `work/signals/`, `work/missions/`, `org/<layer>/`, `CONFIG.yaml`, `CODEOWNERS` plus a policy directory), the wizard:

- proposes a `connections.product-repos[]` entry rather than scaffolding a parallel structure,
- biases artifact suggestions toward the bridge: a finding becomes a candidate signal; an open decision references the originating mission; a release record cross-references the framework's release artifact rather than duplicating it,
- still scaffolds the standalone capture-discipline baseline so the team can rip out either side without losing the other.

This mapping is intentionally generic. `agentic-kb` does not depend on any specific repo-as-OS framework, and is not packaged with one. Adopters running such a framework get the bridge defaults; adopters who do not still get a fully usable knowledge-ops scaffold.

## Related

- `automation-levels.md` — the configuration knob for stage 3.
- `setup-flow.md` — where in the interview these stages are asked and applied.
- `../../../../docs/operating-model.md` — the artifact chain (briefs, specs, releases, incidents) the stages instantiate.
- `../../kb-management/SKILL.md` — the "When to invoke" rule that governs Stage 2 confirmation behavior.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-27 | Initial reference: three-stage adoption ladder, graduation criteria, mapping to automation levels and to repo-as-OS frameworks | Soft-transition extension |
