# Collaboration Guide

> **Version:** 5.0.0 | **Last updated:** 2026-04-25

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
| 2026-04-25 | Clarified that consumer layers can receive digest updates and host read-down guidance locally, while still refusing promote/publish as a source of new shared truth | Deep spec-audit follow-up |
| 2026-04-25 | Reworked the collaboration contract for 5.0.0: replaced L1-L4 language with contributor/shared/consumer roles, clarified consumer-only behavior, and updated promotion/publish review points for named layers and per-layer marketplaces | v5.0.0 flexible layer model |
| 2026-04-20 | Initial collaboration guide defining shared-workspace operating norms, review points, and failure recovery | Issue #7 |
