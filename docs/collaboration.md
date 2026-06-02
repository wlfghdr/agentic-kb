# Collaboration Guide

> **Version:** 6.3.0 | **Last updated:** 2026-06-02

This guide defines the human collaboration contract for `agentic-kb` workspaces. The structural spec explains where files live. This guide explains how people and their agents should behave so shared KB work stays trustworthy.

## Why this guide exists

`agentic-kb` only works in teams if humans can predict:

- what an agent may do on its own,
- what must stay a human decision,
- what shared artifacts mean,
- and how to recover when interpretations diverge.

Without that, the file structure may be clean while the collaboration model is not.

## Core principle

**Contributor speed, shared caution.**

In a contributor-owned anchor layer, the agent should help the user move fast. In shared team, org, or company-facing layers, the agent should optimize for clarity, traceability, and low surprise for other humans.

## Agent execution policy

For meaningful repo-changing work, Engineering and Quality should run as separate dedicated sessions.

- **Engineering** implements with a clear scope, explicit artifact targets, and auditable output.
- **Quality** reviews independently and returns an explicit verdict such as `merge-ready`, `needs-fix`, or `blocked`.
- **Handoffs are mandatory.** Quality findings become the next Engineering scope when fixes are needed.
- **No self-certification.** The same session that implemented a meaningful change should not certify that change as quality-complete.

This separation matters most for KB model changes, roadmap/journey behavior, report/runtime logic, and other collaboration-critical surfaces.

## Minimal automation pattern

The preferred automation model is intentionally small:

1. One standing orchestrator watches assigned issues and starts Engineering work.
2. Engineering works the issue, pushes or updates the branch/PR, and requests review.
3. That review request directly triggers Quality.
4. Quality either returns `merge-ready` or sends explicit findings back to Engineering.
5. Engineering responds only to those findings or change requests.
6. When Quality says `merge-ready`, checks are green, and no unresolved findings remain, merge.

This keeps the continuous worker footprint minimal and uses the PR review loop itself as the trigger chain between Engineering and Quality.

## Layer responsibilities

### Contributor-owned layer

Purpose: individual sense-making, preparation, and early shaping.

Agent may:

- capture findings,
- update topics,
- open decisions,
- suggest tasks,
- generate reports and presentations,
- prepare promotion candidates.

Agent must not assume contributor-owned truth is already shared truth.

Human responsibility:

- decide what is mature enough to promote,
- remove or redact sensitive material before promotion,
- review promoted material for clarity outside personal context.

### Shared team layer

Purpose: shared team memory and coordination.

Agent may:

- place promoted material into the correct contributor or shared area,
- digest team changes into contributor-owned layers,
- open or update team decisions when explicitly requested or clearly implied by agreed process,
- suggest conflicts, duplicates, and missing evidence.

Agent should default to **suggest + surface**, not silent restructuring, when multiple humans depend on the result.

Human responsibility:

- confirm team-relevant promotions,
- review shared decisions and RACI,
- resolve conflicts between contributor interpretations,
- keep shared foundation material current enough that agents can align against it.

### Shared org or company-facing layer

Purpose: cross-team synthesis, steering, or top-down guidance.

Agent may:

- digest higher-layer changes downward,
- package mature shared outputs upward,
- highlight contradictions and dependency signals across teams.

Agent must be more conservative here than in a contributor-owned layer. Cross-team meaning is easier to distort than local context.

Human responsibility:

- validate framing before broad publication,
- assign decision authority explicitly,
- treat synthesis layers as curated outputs, not raw dumping grounds.

### Consumer-only layer

Purpose: read-down guidance, not local authoring.

Agent may:

- read and digest,
- compare local state to published guidance,
- flag mismatches.

Agent must not promote or publish into a `role: consumer` layer.
Consumer layers may still receive downward digest updates and expose shared guidance locally, but they are not where new shared truth originates.

Human responsibility:

- keep the consuming boundary clear,
- name the correct upstream contributor layer when contribution is actually needed.

## Shared-workspace rules

### 1. Distinguish three action modes

Every meaningful agent response in shared contexts should make clear whether it is:

- **Read-only analysis**: inspected and summarized, no files changed.
- **Proposed mutation**: recommends a change, but has not applied it.
- **Applied mutation**: changed files and should say where.

Humans should never need to infer this from tone.

### 2. Promotions are social, not just technical

A promotion is not just moving a file upward. It is a claim that the content is ready for a broader audience.

Before promotion, the human or agent should confirm:

- context is understandable outside the source layer,
- the artifact does not depend on hidden chat history,
- sensitive material is removed,
- the target layer is the right audience,
- the target layer is contributor-capable.

Decision and task promotion have one extra check: determine whether the target layer now owns the same decision question or work item and accountable decider/owner. If yes, the target record becomes canonical and the source-layer record is closed, archived, or replaced with a backlink. Keep two active records only when their scopes, recommendations, accountable owners, or sub-task responsibilities genuinely differ.

### 2a. Direct cross-layer capture: explicit OR confirmed

Captures do not have to land in the private/anchor layer first and propagate upward through `/kb promote`. Some material is shared-layer truth from the moment it is written (a meeting note about a team decision, a task that belongs on the team backlog by definition, a retro commitment). The framework supports three routing modes per capture: **default** (active layer), **explicit** (user named a target layer or a `capture-routing:` rule in `.kb-config/layers.yaml` matches), and **reflection-driven** (agent inferred a non-default target from content/source/context).

The shared-workspace contract is the same on every mode: the human stays accountable for the placement decision. Concretely:

- **Default mode** proceeds without an extra prompt — the active layer is the standing destination.
- **Explicit mode** proceeds without an extra prompt — the user already declared the routing in the invocation or in config. The agent cites the matching instruction in the response.
- **Reflection-driven mode** is **proposed mutation**, never applied. The agent presents the target with a one-line reason and offers the default as a one-word fallback. The mutation is gated on an explicit confirmation; no soft-write to a staging area as a fallback. A previous confirmation does not give the agent standing permission for future captures — the supported way to make a target sticky is a `capture-routing:` rule.

This protects two failure modes: (a) a contributor's private finding being silently written into a team-visible location because the agent over-interpreted the input, and (b) routine team intake being framed as private sense-making and then needing a redundant promote hop. Full contract: `plugins/kb/skills/kb-management/references/capture-routing.md`.

### 3. Digests are summaries, not overrides

A digest should inform the receiving layer. It should not silently rewrite the receiving layer's priorities or positions.

If upstream material conflicts with the current local view, the agent should:

- capture the conflict,
- point to both sides,
- suggest a decision or review,
- avoid pretending convergence already happened.

### 4. Shared decisions need explicit humans

In team, org, and company-facing contributor layers, decisions must name the humans around the decision clearly enough that others can act on them.

Minimum expectation:

- stakeholders named,
- due date present,
- status explicit,
- RACI present where the layer requires it.

If these are missing, the agent should flag the decision as structurally weak.

### 5. Team trust beats automation cleverness

If there is a tradeoff between automation elegance and human confidence, prefer the option that a teammate can review in under two minutes.

## Minimum operating discipline for teams

A team using `agentic-kb` seriously should agree on at least these norms:

1. One canonical contributor-owned layer per person or clearly bounded working context.
2. One shared team layer per real working team.
3. Promotions include a destination-layer review before being treated as shared truth.
4. Shared decisions are not left without owners or dates.
5. Conflicts are captured explicitly, not flattened away.
6. Agents log what they changed.
7. Humans remain accountable for shared meaning.

### Ownership and approval boundaries

For the shared report family, ownership and approval should be explicit before the artifact is treated as shared truth:

- **status** reports are usually owned by the reporting lead or ritual owner;
- **delivery** reports are usually owned by engineering or delivery leadership;
- **roadmap-change** reports are only approved by the accountable roadmap owner or PM, even when the report was opened automatically from detected baseline drift.

The markdown source is the review surface. HTML is the consumption surface.

### Deterministic triggers

The most useful triggers are predictable and reviewable:

- recurring cadence for status and delivery reports,
- event-driven opening for roadmap-change reports when sequencing, dates, scope, or ownership shifts,
- explicit refresh after major demos, customer learning, or delivery surprises that materially change the operating picture.

Teams should prefer named triggers over vague "update when needed" expectations.

### Feedback intake and KB loop

Shared reports should not be terminal outputs. They should feed the KB back into action:

- stakeholder questions become decisions, findings, or follow-up tasks,
- delivery drift feeds roadmap review,
- roadmap changes feed journey review when product behavior is affected,
- new customer or prototype evidence feeds both journey refinement and the next delivery/status cycle.

That loop is what keeps roadmap, journeys, decisions, and delivery reports from drifting into parallel narratives.

## Recommended review points

### Before promoting into a shared team layer

- Is the artifact understandable without source-layer background?
- Did the gate score reflect real team relevance?
- Are next steps clear for another human?

### Before promoting into an org or company-facing contributor layer

- Is this a shared team position or only one contributor's view?
- Are dependencies and implications stated?
- Is there a named human owner for follow-up?

### Before publishing to a layer marketplace

- Is the pattern truly reusable beyond the originating context?
- Has local or company-specific material been removed?
- Would another team understand the skill without private history?

## Failure modes and recovery

### Silent structure drift

Symptom: different people use slightly different file meanings or folder habits.

Recovery:

- audit against the spec,
- fix the structure explicitly,
- document the correction in changelogs or issue discussion,
- avoid hidden cleanup in shared branches.

### False convergence

Symptom: the workspace looks aligned, but contributors actually disagree.

Recovery:

- create or reopen a decision,
- capture conflicting evidence separately,
- assign a human owner,
- do not resolve by summary wording alone.

### Parallel mutations on shared layers

Symptom: two contributors promote the same artifact, edit the same topic, or revise a source after promote — all on the same day.

These are concurrency cases, not collaboration habits, and they have deterministic resolution rules in [`docs/concurrency.md`](./concurrency.md):

- **Promote collisions** resolve via author-id suffix on the second promote plus a `_kb-log/promote-conflicts.md` entry. The human reconciles via `/kb sync`.
- **Backlink mutation** (editing a `status: promoted` source after promote) is refused by `/kb` and surfaced as a diverged-backlink warning on the next `/kb sync` or `/kb audit`.
- **Topic merges** use the author-sectioned format (`## Position — @<author> <date>`) so concurrent edits land as coexisting sections; convergence is an explicit operation that opens a decision.

The collaboration goal is the same as for the other failure modes: surface disagreement, do not flatten it.

### Automation surprise

Symptom: a human cannot tell what the agent changed or why.

Recovery:

- require the response to classify itself as read-only, proposed, or applied,
- point to exact files,
- reduce automation scope until the team trusts the pattern again.

### Promotion without audience fit

Symptom: content was technically valid but wrong for the receiving layer.

Recovery:

- move it back or archive it with a note,
- create a narrower summary for the real audience,
- clarify promotion criteria in the team workflow.

## Practical recommendation

For real teams, start with this posture:

- contributor-owned layers: fast and flexible
- shared team layers: reviewable and explicit
- shared org/company-facing contributor layers: conservative and synthesis-oriented
- consumer-only layers: read-only and high signal

That is the safest path to getting value without trust erosion.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-06-02 | Version aligned to 6.3.0 after the shared process/operational primitive default moved to GitHub Issues-backed storage in the setup and reference specs. Collaboration semantics unchanged | Issue #145 |
| 2026-05-24 | Version aligned to 6.2.0 | Version alignment |
| 2026-05-23 | Added shared-workspace rule 2a "Direct cross-layer capture: explicit OR confirmed" covering the three capture-routing modes (default / explicit / reflection-driven) and the human-confirmation contract that protects against (a) silent agent-inferred shared writes and (b) routine team intake being misframed as private sense-making | Artifact layer routing |
| 2026-05-22 | "Failure modes and recovery" now includes "Parallel mutations on shared layers" pointing at the new `docs/concurrency.md` (promote collisions, backlink mutation, topic merges). Collaboration semantics unchanged; the parallel-mutation failure mode is named explicitly instead of left as the implicit Git-conflict assumption. Closes audit finding #106 | Audit-tracker closeout |
| 2026-05-15 | Version aligned to 6.1.0 after the release-readiness audit. Collaboration semantics unchanged; this guide now tracks the released retro/role-handbook/delivery-operations surface carried by the rest of the spec | Release-readiness audit |
| 2026-05-10 | Added the recommended shared artifact set for engineering collaboration and clarified roadmap → delivery → status interplay | Adoption-oriented engineering pass |
| 2026-05-06 | Added the decision/task promotion ownership rule so shared promotions create one canonical record instead of parallel active source and target decisions/tasks | Decision/task ownership follow-up |
| 2026-04-25 | Clarified that consumer layers can receive digest updates and host read-down guidance locally, while still refusing promote/publish as a source of new shared truth | Deep spec-audit follow-up |
| 2026-04-25 | Reworked the collaboration contract for 5.0.0: replaced L1-L4 language with contributor/shared/consumer roles, clarified consumer-only behavior, and updated promotion/publish review points for named layers and per-layer marketplaces | v5.0.0 flexible layer model |
| 2026-04-20 | Initial collaboration guide defining shared-workspace operating norms, review points, and failure recovery | Issue #7 |
