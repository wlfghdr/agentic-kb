# Vision, Mission & Goals — Strategic Steering Across Layers

> **Version:** 0.1 | **Last updated:** 2026-04-18

Every KB layer can declare a **vision**, **mission**, and **goals**. These are not decorative — they are active filters that shape how the evaluation gate scores material, how the agent prioritizes tasks, and how content flows between layers.

## The Three Levels

| Level | What it answers | Cadence |
|-------|----------------|---------|
| **Vision** | Where are we heading? (north star) | Rarely changes — years |
| **Mission** | What do we do to get there? | Changes with strategy shifts — quarters |
| **Goals** | What are the measurable targets? | Changes with planning cycles — weeks to quarters |

## How VMG Differs per Layer

| Layer | Vision | Mission | Goals |
|-------|--------|---------|-------|
| **L1 Personal** | Personal north star — what you want to achieve | Your role and contribution | Personal OKRs, quarterly targets, skill development |
| **L2 Team** | Team purpose — why this team exists | Team mandate — what the team delivers | Team OKRs, sprint goals, delivery milestones |
| **L3 Org-Unit** | Org-unit strategic direction | Org-unit mandate across teams | Cross-team OKRs, roadmap milestones |
| **L4 Marketplace** | N/A (distribution layer) | N/A | N/A |
| **L5 Company** | Company vision (consumed, not authored) | Company mission | Company OKRs, strategic initiatives |

L5 is **reference-only** — lower layers consume L5's VMG to ground their own, but never write to L5.

## Where VMG Lives

### In `.kb-config.yaml`

```yaml
vmg:
  vision: "Build the knowledge infrastructure that makes AI-native work the default."
  mission: "Curate evidence, formalize positions, and surface decisions so agents and humans stay aligned."
  goals:
    - id: G-2026-Q2-01
      description: "Ship agentic-kb v3 with idea incubation and VMG"
      target-date: 2026-06-30
      status: active          # active | achieved | deferred | dropped
    - id: G-2026-Q2-02
      description: "Onboard 3 teams onto L2 team KBs"
      target-date: 2026-06-30
      status: active
```

### In `references/foundation/context.md`

The vision and mission are echoed in the foundation file so they're always in the agent's context:

```markdown
## Vision & Mission

**Vision**: Build the knowledge infrastructure that makes AI-native work the default.
**Mission**: Curate evidence, formalize positions, and surface decisions so agents and humans stay aligned.
```

### For Team and Org-Unit KBs

Team and org-unit KBs declare VMG in their own `AGENTS.md` or equivalent config file.

## How VMG Steers the KB

### 1. Evaluation Gate Enhancement

The five evaluation questions remain — but VMG adds a **strategic alignment check**:

> *"Does this input align with the declared vision/mission/goals? If it contradicts a goal, is it a signal worth capturing as a challenge?"*

Scoring impact:
- Input aligned with an active goal → +1 to gate score (treated as "actionable").
- Input contradicting a goal → captured as a finding + flagged for decision ("do we adjust the goal or reject the signal?").
- Input orthogonal to all goals → standard gate scoring (no bonus, no penalty).

### 2. Task Prioritization

When the agent suggests tasks or orders the backlog, goal alignment is a primary sort key:
- Tasks linked to active goals surface first.
- Tasks with no goal alignment drop in priority (not removed — just ranked lower).

### 3. Cross-Layer Coherence

The agent checks alignment when promoting across layers:
- **L1 → L2 promote**: "Does this align with the team's mission?"
- **L2 → L3 promote**: "Does this serve the org-unit's strategic direction?"
- **Any layer**: "Is this grounded in L5's company goals?" (when L5 is configured)

Misalignment is not a blocker — it's a signal. The agent flags it: *"This contradicts team goal G-2026-Q2-01 — promote anyway?"*

### 4. Ritual Integration

| Ritual | VMG role |
|--------|---------|
| `start-day` | Briefing opens with goal progress summary |
| `end-week` | Weekly summary includes goal status + delta |
| `start-week` | Planning checks: any goals at risk? any goals achieved? |
| `/kb audit` | Flags goals past target-date without achievement or deferral |

### 5. Idea Alignment

When an idea is created, the agent checks: *"Does this idea serve an active goal?"* If yes, it's flagged as goal-aligned (higher priority for development). If it opens a direction not covered by any goal, it may suggest a new goal.

## Goal Lifecycle

```
active  →  achieved | deferred | dropped
```

- **Achieved**: target met — the agent logs the achievement as a finding and updates relevant topics.
- **Deferred**: postponed — reason required, new target date.
- **Dropped**: abandoned — reason required, affected tasks moved to archive.

## L5 Referencing

Lower layers reference L5 material via external anchors (see [10-external-links.md](10-external-links.md)):

```yaml
company:
  enabled: true
  sources:
    - alias: company-okrs
      url: https://intranet.example.com/okrs/2026-Q2
      type: strategy
    - alias: company-vision
      path: ../company-signals/vision-2026.md
      type: directive
```

The agent pulls these on `start-week` and checks for changes. New or changed L5 signals are captured as findings and assessed for impact on personal/team/org goals.

## Relationship to Other Objects

| Object | How VMG interacts |
|--------|------------------|
| **Topics** | Topics ground the "how" — VMG provides the "why" and "where" |
| **Decisions** | Major decisions should reference which goals they serve |
| **Ideas** | Ideas that serve active goals get development priority |
| **Tasks** | Tasks linked to goals are prioritized in focus selection |
| **Workstreams** | Each workstream aligns to one or more goals |
| **Findings** | Findings that challenge goals are escalated as signals |

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version — VMG as strategic steering across layers | Research: agentic-enterprise CONFIG.yaml, strategic beliefs, signal triage |
