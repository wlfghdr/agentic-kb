# Collaboration Guide

> **Version:** 0.1 | **Last updated:** 2026-04-20

This guide defines the **human collaboration contract** for `agentic-kb` workspaces. The structural spec explains where files live. This guide explains how people and their agents should behave so shared KB work stays trustworthy.

## Why this guide exists

`agentic-kb` only works in teams if humans can predict:

- what an agent may do on its own,
- what must stay a human decision,
- what shared artifacts mean,
- and how to recover when interpretations diverge.

Without that, the file structure may be clean while the collaboration model is not.

## Core principle

**Personal speed, shared caution.**

At L1, the agent should help the user move fast. At L2 and L3, the agent should optimize for clarity, traceability, and low surprise for other humans.

## Layer responsibilities

### L1 Personal

Purpose: individual sense-making and preparation.

Agent may:

- capture findings,
- update personal topics,
- open personal decisions,
- suggest tasks,
- generate reports and presentations,
- prepare promotion candidates.

Agent must not assume L1 truth is shared truth.

Human responsibility:

- decide what is mature enough to promote,
- remove or redact sensitive material before promotion,
- review promoted material for clarity outside personal context.

### L2 Team

Purpose: shared team memory and team coordination.

Agent may:

- place promoted material into the correct contributor area,
- digest team changes into personal KBs,
- open or update team decisions when explicitly requested or clearly implied by agreed process,
- suggest conflicts, duplicates, and missing evidence.

Agent should default to **suggest + surface**, not silent restructuring, when multiple humans depend on the result.

Human responsibility:

- confirm team-relevant promotions,
- review shared decisions and RACI,
- resolve conflicts between contributor interpretations,
- keep team VMG current enough that agents can align against it.

### L3 Org-Unit

Purpose: cross-team synthesis and steering.

Agent may:

- digest org-level changes downward,
- package mature team outputs upward,
- highlight cross-team contradictions and dependency signals.

Agent must be more conservative here than at L2. Cross-team meaning is easier to distort than personal meaning.

Human responsibility:

- validate framing before broad publication,
- assign decision authority explicitly,
- treat L3 as synthesis, not raw dumping.

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
- the target layer is the right audience.

### 3. Digests are summaries, not overrides

A digest should inform the receiving layer. It should not silently rewrite the receiving layer's priorities or positions.

If upstream material conflicts with the current local view, the agent should:

- capture the conflict,
- point to both sides,
- suggest a decision or review,
- avoid pretending convergence already happened.

### 4. Shared decisions need explicit humans

In team and org layers, decisions must name the humans around the decision clearly enough that others can act on them.

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

1. **One canonical personal KB per person.**
2. **One shared team KB per actual working team.**
3. **Promotions are reviewed before being treated as team truth.**
4. **Team decisions are not left without owners or dates.**
5. **Conflicts are captured explicitly, not flattened away.**
6. **Agents log what they changed.**
7. **Humans remain accountable for shared meaning.**

## Recommended review points

### Before promoting L1 → L2

- Is the artifact understandable without personal background?
- Did the gate score reflect real team relevance?
- Are next steps clear for another human?

### Before promoting L2 → L3

- Is this a team position or only one contributor's view?
- Are dependencies and implications stated?
- Is there a named human owner for follow-up?

### Before publishing to L4

- Is the pattern truly reusable beyond the originating context?
- Has personal/company-specific material been removed?
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

- L1: fast and flexible
- L2: reviewable and explicit
- L3: conservative and synthesis-oriented
- L4: manual and high bar

That is the safest path to getting value without trust erosion.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-20 | Initial collaboration guide defining shared-workspace operating norms, review points, and failure recovery | Issue #7 |
