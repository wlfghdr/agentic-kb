# Role Handbook

> **Version:** 0.1.0 | **Last updated:** 2026-05-14

A role-by-role companion to [`docs/operating-model.md`](./operating-model.md). The operating model explains *which loops exist* and *which artifacts make them legible*; this handbook flips that view so each role can find its own daily reality, top commands, and primary artifacts in one place.

This document is descriptive, not prescriptive. Real titles vary; real teams blend roles. Use the closest match and adapt.

---

## How to read this

For each role:

- **Daily reality** — the concrete shape of a working day, not a job description.
- **Primary loop** — which of the five operating-model loops the role lives in most.
- **Top commands** — the `/kb` flows the role reaches for first.
- **Reads** — artifacts the role consumes daily or weekly.
- **Writes** — artifacts the role authors directly.
- **Typical example** — one realistic chain through the artifact graph.

The artifact chain that grounds everything is:

```text
goal/workstream -> journey/brief -> roadmap/spec -> decision/task -> release -> incident -> retro/finding/topic/report
```

Every role touches some prefix or suffix of that chain. Knowing which prefix or suffix you live in is the point of this handbook.

---

## Product manager (PM)

**Daily reality.** Customer interviews, roadmap maintenance, backlog grooming, stakeholder updates, spec/PRD drafting, cross-functional alignment (engineering, design, sales, support), metrics review, problem framing.

**Primary loop.** Direction. Secondary: Learning.

**Top commands.**

- `/kb start-day` — focus + decision + connection deltas
- `/kb journeys [...]` — author or refresh a journey when the active layer has a `journeys:` block
- `/kb roadmap [...]` — reconcile plan-vs-delivery when the active layer has a `roadmap:` block
- `/kb brief [title]` — frame the next piece of work
- `/kb report status [scope]` / `/kb report roadmap-change [scope]` — stakeholder readouts
- `/kb decide [description]` — open prioritization or scope decisions

**Reads.** journeys, roadmaps, briefs, specs, status reports, release records, customer findings, decisions.

**Writes.** journeys, briefs, decisions, roadmap-change reports, status reports, meeting notes.

**Typical example.** A customer call surfaces a new pain point → `/kb https://transcript/...` captures it as a finding → the finding informs an existing journey → the PM updates the journey, opens a brief framing the new outcome window, and adds a roadmap-change report explaining why the next phase is moving up.

---

## Engineering manager (EM)

**Daily reality.** 1:1s with reports, capacity and staffing decisions, escalation handling, performance management, hiring loops, budget conversations, status reports to leadership, incident review participation, unblocking.

**Primary loop.** Direction + Delivery + Operations (the EM is the role most spread across loops).

**Top commands.**

- `/kb start-day` — focus + open decisions + blockers across reports
- `/kb start-week` — full digest before Monday planning
- `/kb decide [description]` — open staffing, escalation, or scope decisions with explicit RACI
- `/kb report status [scope]` / `/kb report delivery [scope]` — leadership readouts
- `/kb task` — review what's blocked across the team
- `/kb audit` — surface contradictions, stale workstreams, missing owners

**Reads.** workstreams, briefs, specs, task views, incidents, weekly reports, decisions, foundation (stakeholders).

**Writes.** decisions (with RACI), workstream status updates, status/delivery reports, escalation notes, meeting notes.

**Typical example.** A team is missing a target → EM digests parent strategy with `/kb digest engineering-org` → opens a decision with explicit stakeholders and due date → captures the unblocking discussion in a meeting note → archives the decision once resolved → adds the outcome to the next delivery report.

**Note on people-management artifacts.** 1:1 stewardship, career conversations, and performance documentation sit outside the spec's first-class primitives (see `operating-model.md` §8). Many EMs keep these in private contributor-scoped meeting notes or in a separate HR system; the KB is not a replacement for either.

---

## Staff / principal engineer

**Daily reality.** Architecture work, cross-team alignment, design reviews, mentoring senior engineers, escalations on technical risk, roadmap inputs, deep technical investigation, occasional implementation on critical paths.

**Primary loop.** Design. Secondary: Direction.

**Top commands.**

- `/kb spec [title]` — turn briefs into design contracts
- `/kb decide [description]` — open architecture decisions with linked evidence
- `/kb [text/URL]` — capture papers, prototypes, and post-mortems as findings
- `/kb promote [file] [layer]` — surface durable findings or specs upward
- `/kb report progress [scope]` — synthesize across workstreams
- `/kb audit` — surface drift between specs and reality

**Reads.** briefs, specs, decisions, incidents, findings, journeys, parent-layer strategy digests.

**Writes.** specs, decisions, findings, design notes.

**Typical example.** A new initiative lands as a brief → staff engineer writes a spec linking it, opens an architecture decision with options A/B/C, gathers evidence findings from prototypes and prior incidents → resolves the decision, marks the spec `accepted`, and promotes it to the team layer.

---

## Tech lead

**Daily reality.** Turn intent into implementable plans, run refinement and design discussions, review PRs, mentor engineers, own a workstream end-to-end, coordinate rollouts.

**Primary loop.** Design + Delivery.

**Top commands.**

- `/kb spec [title]` — design contracts
- `/kb brief [title]` — when intent needs to be sharpened before spec work
- `/kb release [title]` — own the rollout record for the team's changes
- `/kb decide [description]` — design forks and rollout choices
- `/kb note meeting [topic]` — refinement and review sessions
- `/kb start-week` / `/kb end-week` — keep the workstream legible

**Reads.** briefs, specs, tasks, release records, parent decisions, journeys covering the workstream.

**Writes.** specs, decisions, release records, meeting notes, focus task updates.

**Typical example.** Brief lands → tech lead writes spec → opens release record with rollout/rollback/verification plan → ships → release record links the follow-up finding when a small regression appears → finding informs the next spec revision.

---

## Engineer (IC)

**Daily reality.** Standup, PR review (giving and receiving), implementing against specs/tickets, writing tests, debugging, async chat clarifications, occasional on-call rotation, learning time.

**Primary loop.** Delivery. Secondary: Learning.

**Top commands.**

- `/kb start-day` — see today's focus task
- `/kb task` / `/kb task done [item]` — drive personal focus
- `/kb [text/URL/path]` — capture a paper, post, or code-review insight worth keeping
- `/kb note [text]` — quick working notes during debugging
- `/kb idea [text]` / `/kb develop [idea]` — seed and spar on improvements
- `/kb end-day` — wrap, archive done items, commit

**Reads.** specs, tasks, decisions linked to active work, recent incidents, runbooks, parent strategy digests.

**Writes.** findings, working notes, tasks, idea seeds, occasional decision evidence.

**Typical example.** Hits an unfamiliar failure mode while debugging → `/kb` the relevant doc and the stack trace → finding gets `Gate 3/5` and updates the reliability topic → adds a follow-up task to harden the test → the test PR closes the task, end-of-day archives it.

---

## Designer / researcher

**Daily reality.** User interviews and synthesis, wireframes and prototypes, design reviews and critique, design-system upkeep, working alongside PM and engineering, usability testing, handoff.

**Primary loop.** Direction + Learning.

**Top commands.**

- `/kb journeys [...]` — author or refresh persona journeys on the layer that owns them
- `/kb [text/URL]` — capture interview snippets, synthesis, references
- `/kb note meeting [topic]` — design reviews and research debriefs
- `/kb brief [title]` — frame design problems when ownership warrants it
- `/kb report progress [scope]` — research roll-ups for a workstream
- `/kb develop [idea]` — sparring on design directions

**Reads.** briefs, specs, journey artifacts, research findings, customer feedback reports.

**Writes.** journeys, briefs (collaboratively with PM), findings, design notes, meeting notes.

**Typical example.** Three user interviews surface the same friction → `/kb` captures each as a finding tagged to the persona journey → the journey gets a readiness drop on the affected step → PM and designer co-author a brief; designer prototypes; finding chain feeds the spec.

---

## QA / test engineer

**Daily reality.** Test plan writing, manual and exploratory testing, test automation, bug triage and reporting, release verification and sign-off, regression maintenance.

**Primary loop.** Delivery + Learning.

**Top commands.**

- `/kb spec [title]` — sometimes co-authored to capture verification approach
- `/kb release [title]` — own or co-own the release verification section
- `/kb [text/URL]` — capture flaky-test patterns, regression evidence
- `/kb note retro [topic]` — post-release retros (see [retro](#retrospective-pattern) pattern below)
- `/kb task` — track verification items
- `/kb report delivery [scope]` — readiness summary alongside engineering owners

**Reads.** specs, release records, recent incidents, findings tagged to flaky areas.

**Writes.** test plan notes, verification entries on release records, findings, retros.

**Typical example.** Spec lands with a verification section → QA writes test plan as a working note → executes; one failure mode becomes a finding → release record's verification section links the finding and proceeds with mitigation noted in the rollout plan.

---

## SRE / on-call engineer

**Daily reality.** Dashboard and alert monitoring, incident response, postmortems, capacity planning, reliability work (SLOs, error budgets), on-call rotation handoff, runbook upkeep.

**Primary loop.** Operations + Learning.

**Top commands.**

- `/kb incident [title]` — open the timeline record at first sign of degradation
- `/kb start-day` — review overnight alerts and any active incidents
- `/kb note retro [topic]` — run the post-incident retro
- `/kb [text/URL]` — capture symptom patterns, change correlations, runbook gaps as findings
- `/kb decide [description]` — open follow-up decisions surfaced by incidents
- `/kb report status [scope]` — communicate to stakeholders during incidents and after

**Reads.** incidents (open + recent), release records (especially in the last 24 hours), runbooks, decisions tagged to reliability, parent operations digests.

**Writes.** incidents (live updates → append-only after resolution), retros, findings, runbook updates, follow-up tasks.

**Typical example.** Alert fires → `/kb incident db-latency-spike` opened with severity and owner → timeline updated as mitigations land → resolved → `/kb note retro db-latency-spike` runs the team retro → action items become tasks linked back to the incident; one becomes a spec for a permanent fix.

---

## Security / compliance engineer

**Daily reality.** Threat modeling, vulnerability triage, security review of changes, audit and compliance evidence collection, incident response participation, policy upkeep.

**Primary loop.** Operations + Design + Learning.

**Top commands.**

- `/kb [text/URL]` — capture advisories, threat-intel notes, audit findings
- `/kb decide [description]` — open control or risk-acceptance decisions
- `/kb spec [title]` — co-author specs that need security-review sections
- `/kb incident [title]` — open security incidents
- `/kb audit` — surface drift between policy and observed state
- `/kb report status [scope]` — security posture readouts

**Reads.** specs (especially "Risks and trade-offs"), incidents, release records, decisions tagged to security, compliance digests from parent layers.

**Writes.** findings (threat intel, vuln advisories), decisions (control changes), review notes, security incident records.

**Typical example.** New advisory matches a dependency in the workstream → capture as finding → open decision: patch now vs. compensating control → resolution links spec changes and a release record describing the rollout.

---

## Data / analytics

**Daily reality.** Metric definitions, dashboard authoring, A/B test analysis, data quality investigations, insight reports for product and leadership.

**Primary loop.** Learning + Direction.

**Top commands.**

- `/kb [text/URL]` — capture analyses, anomaly reports, A/B results
- `/kb decide [description]` — when a metric definition or experiment outcome should be canonized
- `/kb report progress [scope]` — insight roll-ups
- `/kb note meeting [topic]` — metric review meetings

**Reads.** journeys (to ground metrics in user behavior), briefs (success signals), recent releases (to attribute movement).

**Writes.** findings (insights), decisions (metric definitions), reports, occasional spec contributions.

**Typical example.** A/B test resolves → finding captures the result with linked dashboards → existing decision on feature rollout moves from `under-discussion` to `decided` citing the finding → product brief's success signals section is updated.

---

## Retrospective pattern

Retrospectives are the most common learning ritual that previously had no canonical shape in the spec. Use the `retro` note variant when a recurring team reflection or a one-off project debrief needs to be durable:

- **Sprint / iteration retros** — recurring team reflection
- **Project / launch retros** — at the end of a bounded effort
- **Post-incident retros** — within days of incident resolution, paired with the incident record
- **Quarterly or annual retros** — broader cadences for leadership or whole-team learning

Mechanically, a retro is a meeting note with a known structure:

| Section | Question it answers |
|---------|--------------------|
| Context | What period or event are we reviewing? |
| What went well | What should we keep doing? |
| What didn't | What hurt us? |
| What we changed already | Mid-flight corrections worth preserving |
| What we will change | Concrete commitments — these become tasks or decisions |
| Open questions | Things we couldn't resolve in the session |
| Linked artifacts | Incidents, releases, briefs, specs the retro reflects on |

Open one with `/kb note retro [topic]`. The template lives at [`plugins/kb/skills/kb-management/templates/retro.md`](../plugins/kb/skills/kb-management/templates/retro.md). Action items in *What we will change* should be promoted into the team layer's `_kb-tasks/backlog.md` or `_kb-decisions/` immediately — a retro that produces no tracked commitments is one of the failure modes [collaboration.md](./collaboration.md) flags as "false convergence".

---

## Reading this back into the operating model

| Operating-model loop | Roles primarily here |
|----------------------|----------------------|
| Direction | PM, EM, staff engineer, designer |
| Design | Staff engineer, tech lead, designer (for UX contracts), security |
| Delivery | Engineer, tech lead, QA, EM |
| Operations | SRE / on-call, EM, security, support |
| Learning | Everyone — the retro pattern, findings, and topic updates are the connective tissue |

No role lives in one loop. The handbook lists where each role spends the most time, not where it is restricted to.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-14 | Initial role handbook covering PM, EM, staff/principal engineer, tech lead, engineer, designer, QA, SRE/on-call, security, data; introduced the retrospective pattern as a note variant tied to `_kb-notes/` with a dedicated template | Daily-reality gap audit across software-company roles |
