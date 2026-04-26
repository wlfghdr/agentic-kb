# Software Engineering Operating Model

> **Version:** 0.1.0 | **Last updated:** 2026-04-26

This document describes what day-to-day software engineering work looks like across the main roles in a software company, which artifacts make that work legible, and which parts of that operating model `agentic-kb` did not model explicitly before this operating-model extension.

It is partly analytical and partly prescriptive:

- analytical, because it names the recurring loops real teams run every day and week,
- prescriptive, because it defines the minimum artifact chain `agentic-kb` should standardize so those loops stay traceable.

## 1. The Daily Work Is Not One Loop

In a software company, "daily work" is a mesh of five loops that happen in parallel:

| Loop | Primary question | Typical roles | Typical cadence | Minimum durable artifacts |
|------|------------------|---------------|-----------------|---------------------------|
| Direction | What problem matters now? | product manager, engineering manager, staff engineer, design lead | weekly to monthly | VMG, workstreams, briefs, decisions, roadmap reports |
| Design | What should we build and how should it work? | tech lead, staff engineer, senior engineer, designer, security, QA | daily to weekly | specs, decisions, notes, linked findings |
| Delivery | What is being built, by whom, and what is blocked? | engineers, tech leads, QA, program managers, EMs | daily | tasks, backlog, focus, release records, progress reports |
| Operations | Is the system healthy in production, and what do we do when it is not? | SRE, on-call engineers, EMs, support, security | continuous | incidents, release records, findings, runbooks, follow-up decisions |
| Learning | What did we learn, and how does it change future work? | everyone | continuous | findings, topics, post-incident notes, reports, updated briefs/specs |

The important point is that knowledge systems fail when they model only the learning loop. Real engineering organizations also need the design, delivery, and operations loops to stay visible.

## 2. Role-Centric View

The same company day looks different depending on role.

| Role | Daily reality | Questions they answer | Artifacts they read most | Artifacts they author most |
|------|---------------|-----------------------|--------------------------|----------------------------|
| Product manager | clarifies problem, scope, trade-offs, sequencing | Why this? Why now? For whom? | briefs, specs, roadmap reports, release records | briefs, decisions, status reports |
| Engineering manager | aligns people, capacity, risk, escalation | Are we staffed correctly? What is blocked? What needs escalation? | briefs, specs, task views, incidents, weekly reports | decisions, task priorities, escalation notes, reports |
| Staff or principal engineer | shapes architecture and cross-team alignment | What must stay true across teams? | briefs, specs, decisions, incidents, findings | specs, decisions, findings, design notes |
| Tech lead | turns intent into implementable plans | What is the next safe design and rollout step? | briefs, specs, tasks, release records | specs, decisions, release records, meeting notes |
| Engineer | implements, reviews, tests, debugs | What do I build next and how do I verify it? | specs, tasks, decisions, incidents, runbooks | findings, notes, tasks, incident follow-ups |
| Designer or researcher | shapes experience and validates fit | What user problem are we solving and what evidence supports it? | briefs, specs, journey artifacts, reports | briefs, notes, findings, specs |
| QA or test engineer | validates behavior and release safety | What must be true before we ship? | specs, release records, incidents | test notes, release verification, findings |
| SRE or on-call engineer | protects production health | What is broken, what changed, what is the rollback path? | incidents, release records, runbooks, decisions | incidents, findings, runbooks, follow-up tasks |
| Security or compliance engineer | reduces risk and verifies controls | What changed in risk, exposure, or required controls? | specs, incidents, release records, decisions | findings, decisions, review notes |

No single artifact serves all of these roles well. That is why a useful KB needs a chain of linked artifact types, not just one generic note format.

## 3. A Typical Cross-Role Day

One realistic working day in a software company often looks like this:

1. Product and engineering leadership sharpen a problem into a brief.
2. A tech lead and staff engineer turn that brief into a spec and identify the open decisions.
3. Engineers implement against the spec, while QA and security review the risky parts.
4. A release owner records rollout, verification, and rollback details before shipping.
5. If production degrades, on-call opens an incident record and captures the timeline and mitigations.
6. After stabilization, the team distills findings, updates the spec or brief, and creates follow-up decisions or tasks.

That chain is the minimum durable memory of modern software delivery:

`goal/workstream -> brief -> spec -> decision/task -> release -> incident -> finding/topic/report`

If the KB cannot represent those hops explicitly, it loses the handoff surfaces between roles.

## 4. What `agentic-kb` Already Covered Well

Before v5.3.0, `agentic-kb` already modeled several important knowledge objects correctly:

- findings as immutable dated evidence,
- topics as living positions,
- decisions as first-class choice records,
- notes for meetings and working context,
- tasks and workstreams for local execution focus,
- reports and presentations for stakeholder communication,
- roadmaps and journeys as opt-in draft extensions.

This coverage was strong for individual sense-making, cross-layer promotion, and team knowledge synthesis.

## 5. The Gaps Before v5.3.0

The missing pieces were not random. They clustered around the parts of engineering work that create cross-role commitments.

### Gap A: No first-class delivery intent artifact

There was no canonical artifact between VMG or workstream direction and implementation detail.

- A topic was too broad.
- A note was too lightweight.
- A decision captured a choice, not the framed problem and intended outcome.

Missing artifact: **brief**.

### Gap B: No first-class design contract artifact

There was no canonical place for requirements, proposed shape, rollout constraints, and verification approach to live together.

- Topics were durable but too unstructured.
- Notes were structured for conversations, not for executable design contracts.
- Decisions captured forks, but not the design body around them.

Missing artifact: **spec**.

### Gap C: No first-class shipping record

The system had reports and notes, but no standard record for what shipped, to whom, under which rollout and rollback plan.

Missing artifact: **release record**.

### Gap D: No first-class operational interruption record

The system could capture findings about incidents, but it did not have a standard incident timeline and impact record for on-call, SRE, and follow-up work.

Missing artifact: **incident record**.

### Gap E: No explicit role-to-artifact mapping

The spec described layers and collaboration, but not the concrete artifact handoffs between product, design, engineering, QA, SRE, and management.

Missing concept: **software engineering operating model** as a named layer above the primitive list.

## 6. What This Extension Adds

This extension closes those gaps with two optional feature families and four standard artifacts.

| Feature family | New directories | Purpose |
|----------------|-----------------|---------|
| `delivery` | `_kb-delivery/briefs/`, `_kb-delivery/specs/` | Makes intent and design handoffs durable |
| `operations` | `_kb-operations/incidents/YYYY/`, `_kb-operations/releases/YYYY/` | Makes shipping and production response durable |

| Artifact | Why it exists | Primary authors | Primary readers |
|----------|---------------|-----------------|-----------------|
| Brief | Frames the problem, scope, non-goals, and success signals | product, EM, tech lead | engineering, design, leadership |
| Spec | Defines requirements, design shape, risks, rollout, and verification | tech lead, staff engineer, engineers | engineers, QA, security, release owners |
| Release record | Makes rollout, verification, rollback, and communications explicit | tech lead, release owner, QA | support, on-call, EM, stakeholders |
| Incident record | Makes impact, timeline, mitigations, and follow-up explicit | on-call, SRE, engineers | EM, support, security, leadership |

These additions do not replace findings, notes, decisions, or reports. They bridge them.

## 7. Modeling Rule of Thumb

Use the artifact that matches the question being answered:

- use a **brief** when aligning on the problem and intended outcome,
- use a **spec** when aligning on implementation shape and verification,
- use a **decision** when choosing between explicit options,
- use a **release record** when shipping or rolling back a change,
- use an **incident record** when runtime behavior degrades or breaks,
- use a **finding** when preserving dated evidence,
- use a **topic** when updating the living team position after learning.

## 8. What Is Still Out of Scope

This operating model is intentionally scoped to the software delivery loop. It does not try to standardize every artifact in a whole company.

Still out of scope:

- HR and recruiting operations,
- finance, procurement, and legal workflows,
- marketing and sales asset management,
- support systems that need their own external source of truth.

Those surfaces may still feed findings, briefs, specs, releases, or incidents through connections and reports, but they are not first-class KB primitives here.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-26 | Initial operating-model analysis and artifact-gap definition for company-wide software engineering work; introduced the delivery/operations gap narrative for briefs, specs, releases, and incidents | Gap analysis for software-engineering daily work |