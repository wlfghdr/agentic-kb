# First-Run Acceptance Path

> **Version:** 5.5.0 | **Last updated:** 2026-04-30

This document defines the canonical first-run acceptance path for `agentic-kb`.

Its purpose is narrow and practical:

**Can a human or team lead verify, step by step, that a fresh user reached the same working contract as everyone else?**

If the answer is not clearly yes, onboarding is not good enough yet.

## What this acceptance path covers

This path starts at nothing installed and ends at the first useful `/kb` outputs in a newly initialized workspace.

It is intentionally narrow:

- one user,
- one anchor contributor layer,
- one adjacent team layer to prove promotion and digestion,
- one documented harness path at a time,
- manual automation level,
- builtin HTML styling,
- no live tracker write-back.

Product-management roadmap and journey artifacts are optional in the baseline. When the user's role/goals imply them, setup must propose the owning layer and source/output placement in the same confirmation pass as the core KB graph.

That narrowness is deliberate. A team rollout needs one deterministic baseline before it branches into single-layer, team-only, or multi-org variants.

## Contract: install vs. init

The first-run contract has exactly two phases.

### Phase A — Install into the harness

Goal: make `/kb setup` callable.

This phase ends when the harness exposes the `kb` plugin, command, or equivalent installed skill surface.

### Phase B — Initialize the workspace

Goal: create a valid KB workspace and prove it produces the expected first outputs.

This phase ends when `/kb status`, `/kb start-day`, and one cross-layer promote or digest path succeed in the new workspace.

## Acceptance baseline

Use this baseline unless a test explicitly covers another variant.

| Item | Baseline |
|------|----------|
| User name | `alice` |
| Workspace root | `<workspace>/demo-agentic-kb` |
| Anchor layer | `alice-personal` |
| Team layer | `team-observability` |
| Team layer role | `contributor` |
| Themes | `caching`, `reliability`, `observability` |
| Workstream count | 1 |
| Extra org/company layers | skipped |
| Marketplace repo | skipped |
| Connections | skipped |
| Automation | level 1 |
| HTML styling | builtin |

## Harness-specific install end conditions

### Claude Code

Install path:

```text
/plugin marketplace add https://github.com/wlfghdr/agentic-kb
/plugin install kb@agentic-kb
```

Install phase is accepted when:

- `/kb setup` is available,
- the harness exposes the installed plugin without restart ambiguity,
- the user can invoke `/kb setup` from the intended workspace.

### VS Code Copilot Chat

Install path:

- add `wlfghdr/agentic-kb` to `chat.plugins.marketplaces`,
- install the plugin from the Extensions view.

Install phase is accepted when:

- `/kb setup` is available in Copilot Chat,
- the plugin is visible as installed,
- the same command surface is available after reopening the workspace.

### OpenCode

Install path:

```bash
git clone https://github.com/wlfghdr/agentic-kb
cd agentic-kb
scripts/install --target opencode --global
```

Install phase is accepted when:

- the skills are discoverable by OpenCode,
- `/kb setup` is available in the target workspace.

### Gemini CLI

Install path:

```bash
git clone https://github.com/wlfghdr/agentic-kb
cd agentic-kb
scripts/install --target gemini --global
```

Install phase is accepted when:

- `.gemini/commands/kb.toml` or `~/.gemini/commands/kb.toml` exists,
- `/kb setup` is available in Gemini CLI,
- the generated command body does not contain VS Code-only setup guidance.

### Kiro IDE

Install path:

```bash
git clone https://github.com/wlfghdr/agentic-kb
cd agentic-kb
scripts/install --target kiro --global
```

Install phase is accepted when:

- `.kiro/skills/kb/SKILL.md` or `~/.kiro/skills/kb/SKILL.md` exists,
- `/kb setup` is available from the Kiro slash menu,
- the installed skill matches the documented skill format.

### Codex CLI

Install path:

- clone this repo and run `scripts/install --target codex` or `scripts/install --target codex --global`,
- in Codex CLI, operate from the initialized workspace so `AGENTS.md` and `.agents/skills/kb/SKILL.md` are in scope.

Install phase is accepted when:

- `.agents/skills/kb/SKILL.md` or `~/.agents/skills/kb/SKILL.md` exists,
- Codex can operate against the same repo-local KB files without path or layout drift,
- the docs call out that Codex uses `AGENTS.md` plus the skill picker or `$kb`, not a custom slash command.

## Canonical first-run scenario

## Step 1 — Preconditions

Required before starting:

- `git` installed,
- one supported harness installed, or a Codex-compatible workflow attached to an initialized workspace,
- write access to the target workspace path.

Recommended:

- `gh` installed,
- authenticated git remote access.

Expected result:

- missing required tools stop the flow early with a clear fix,
- optional tools warn, but do not invalidate the baseline.

## Step 2 — Install phase

Run the harness-specific install path.

Expected result:

- `/kb setup` becomes callable,
- the user does not need to guess whether install succeeded.

Failure if:

- `/kb setup` is unavailable,
- the docs imply setup can proceed anyway,
- the user must infer success from hidden files alone.

## Step 3 — Start `/kb setup`

From the intended workspace root:

```text
/kb setup
```

Expected result:

- the skill clearly enters initialization mode,
- it does not re-explain plugin installation as if the user were still in Phase A,
- it asks setup questions in a stable order.

## Step 4 — Answer the baseline questions

The setup wizard runs the four-phase, goal-oriented interview defined in `plugins/kb/skills/kb-setup/SKILL.md`. Use these answers; the wizard derives the proposed layer graph and feature set from them and presents it back in phase 3 for confirmation.

### Phase 1 — Context and goals (open-ended)

| Question | Baseline answer |
|----------|-----------------|
| Q1 — Who you are | `alice — engineer on distributed systems; I spend most of my week on caching, reliability, and observability work` |
| Q2 — What you're trying to track or decide | `incidents and slow queries that hint at deeper reliability issues, plus the open architecture decisions for our caching layer` |
| Q3 — Why now | `too many parallel investigations to keep in my head; my lead keeps asking for status` |
| Q4 — Who else needs to see what | `me and one team — the observability folks` |
| Q5 — Where information feeds in | `our product repo, GitHub issues, and the weekly observability sync` |
| Q6 — What you want out | `a morning briefing and a Friday status I can share with my lead` |
| Q7 — How autonomous | `I want to confirm everything before anything is written` |

### Phase 2 — Workspace and harness facts

| Question | Baseline answer |
|----------|-----------------|
| Q8 — Workspace root | current directory / `<workspace>/demo-agentic-kb` |
| Q9 — IDE targets | current harness only |
| Q10 — Discovery pass | accept the reported empty baseline |

### Phase 3 — Proposed plan (the wizard shows, you confirm)

The wizard must derive and propose:

- two layers — `alice-personal` (scope `personal`, role `contributor`, parent `team-observability`, features `inputs, findings, topics, ideas, decisions, tasks, notes, workstreams, foundation, reports`) and `team-observability` (scope `team`, role `contributor`, parent `null`, features `findings, topics, decisions, tasks, notes, foundation, reports`, contributor-mode `notes: shared`),
- anchor layer `alice-personal`,
- workstream `platform-signals` extracted from Q2,
- connections containing the product repo and GitHub issues from Q5,
- dashboard and report panels matching Q6 (morning briefing + weekly status),
- automation level `1` (manual only) — mapped from Q7's "confirm everything" answer; Q6's regular outputs are run by the user, not on a schedule, at this baseline,
- HTML styling `builtin`.

Acceptance for phase 3: the user accepts the proposal as-is.

### Phase 4 — Final confirmation

Confirm with a single yes.

Expected result:

- the user never had to enumerate features, scopes, or contributor-mode flags themselves,
- every phase 1 answer maps to at least one concrete artifact or config effect in the proposal,
- the skill does not ask hidden prerequisite questions later,
- the user can complete setup without already knowing the internal file model.

## Step 5 — Scaffold verification

After setup finishes, the workspace should contain at least:

```text
demo-agentic-kb/
├── AGENTS.md
├── CLAUDE.md
├── alice-personal/
│   ├── AGENTS.md
│   ├── README.md
│   ├── .kb-config/
│   │   ├── layers.yaml
│   │   ├── automation.yaml
│   │   └── artifacts.yaml
│   ├── _kb-inputs/
│   │   └── digested/YYYY/MM/
│   ├── _kb-references/
│   │   ├── foundation/
│   │   ├── findings/YYYY/
│   │   ├── topics/
│   │   └── reports/
│   ├── _kb-notes/YYYY/
│   ├── _kb-ideas/
│   │   └── archive/YYYY/
│   ├── _kb-decisions/
│   │   └── archive/YYYY/
│   ├── _kb-tasks/
│   │   ├── focus.md
│   │   ├── backlog.md
│   │   └── archive/YYYY/
│   ├── _kb-workstreams/
│   ├── .kb-log/
│   ├── .nojekyll
│   ├── index.html
│   └── dashboard.html
└── team-observability/
    ├── AGENTS.md
    ├── README.md
    ├── _kb-references/
    ├── _kb-notes/
    ├── _kb-decisions/
    ├── _kb-tasks/
    ├── .kb-log/
    ├── index.html
    └── dashboard.html
```

Acceptance checks:

- no literal `{{PLACEHOLDER}}` tokens remain, except inside deliberate presentation or brand templates that are filled later by artifact commands,
- `.kb-config/layers.yaml` exists in the anchor layer and names both layers,
- `workspace.anchor-layer` points to `alice-personal`,
- `_kb-tasks/focus.md` exists,
- at least one workstream file exists,
- at least one topic stub exists,
- `index.html` and `dashboard.html` exist in both layers.

Failure if any of these are missing without explicit explanation.

## Step 6 — First status call

Run inside the anchor layer context:

```text
/kb status
```

Expected output characteristics:

- clearly read-only,
- reports clean initial state,
- points to the correct anchor layer,
- suggests the next useful actions.

A good minimal result looks like:

```text
What I did: checked your KB status.
Where it went: read alice-personal/.kb-config/layers.yaml, alice-personal/_kb-tasks/focus.md, alice-personal/.kb-log/...
Gate notes: n/a.
Suggested next steps:
- Run /kb start-day
- Capture a first source with /kb <URL-or-text>
- Try /kb note meeting <topic> before the next sync
```

## Step 7 — First briefing

Run:

```text
/kb start-day
```

Expected output characteristics:

- clearly read-only,
- no invented work,
- no false claims about pending items,
- references the empty initial focus and decision state,
- suggests a concrete first capture or task.

## Step 8 — First capture

Run:

```text
/kb https://example.com/article-about-caches
```

Expected result:

- the agent states whether it fetched external content,
- it applies the evaluation gate,
- it writes a finding,
- it may update a topic,
- it logs the operation,
- it proposes sensible next actions.

Minimum expected artifact outcomes:

- one new file in `alice-personal/_kb-references/findings/YYYY/`,
- possible update to one topic in `alice-personal/_kb-references/topics/`,
- one new `alice-personal/.kb-log/<date>.log` entry,
- archived or marked-digested input if applicable.

## Step 9 — Cross-layer proof

Run one of these:

```text
/kb promote [new-finding] team-observability
```

or

```text
/kb digest team-observability
```

Expected result:

- the source and destination layers are named explicitly,
- the operation refuses if the target role is `consumer`,
- the target layer logs the intake and reviewed result,
- the target layer's `index.html` and `dashboard.html` regenerate.

This step is what proves the setup is actually a layer graph, not just a single local folder.

## Optional Step 10 — Migration proof (legacy adopters only)

If the adopter is carrying a workspace from a pre-5.0 fixed-ladder layout into the 5.x layer graph, exercise the migration helpers end-to-end before declaring acceptance:

1. run `/kb migrate layer-model --dry-run` and confirm the proposed `.kb-config/layers.yaml` matches the named-layer graph,
2. apply the migration after review,
3. run `/kb migrate archives --dry-run` to preview the year-based archive moves,
4. apply the archive migration after review.

Acceptance checks:

- both helpers default to dry-run and only mutate after explicit confirmation,
- the migrated workspace passes the same scaffold checks as Step 5,
- the legacy ladder vocabulary is gone from the migrated config.

Greenfield adopters can skip this step.

## Optional Step 11 — Progress report proof

If the adopter wants to prove the report surface, use the narrowest path first:

1. create one finding and one note in the anchor layer,
2. promote one finding to the team layer,
3. run `/kb report progress team-observability`,
4. verify that the generated report names its sources and includes a watermark.

Acceptance checks:

- the report clearly names what sources were consulted,
- the HTML artifact is self-contained,
- no live tracker auth is required for the first proof run,
- the team lead can trace the narrative back to the generated artifacts.

## Optional Step 12 — Product-management proof

If the Phase 1 answers mention customer journeys, launch planning, phase/lane roadmaps, product sequencing, or stakeholder roadmap presentations, setup must propose `journeys` and/or `roadmaps` on a concrete owning layer.

Use a minimal variant of Q6 such as:

```text
a customer-value roadmap and journey map I can share with stakeholders
```

Acceptance checks:

- the Phase 3 proposal names the owning layer for `roadmaps` and `journeys`, rather than silently choosing during the first command run,
- setup explains why the artifacts are co-located or separated,
- `.kb-config/layers.yaml` contains the matching `roadmap:` / `journeys:` blocks only after confirmation,
- scaffolded `_kb-roadmaps/` and `_kb-journeys/` folders exist when those features are enabled,
- `/kb roadmap --dry-run` and `/kb journeys --dry-run` produce read-only validation output and name missing sources without writing to external trackers,
- the roadmap presentation rules are visible in generated guidance: value headlines, implementation/detail second lines, explicit draft/proposed/agreed/shipped status, and no checkmarks for proposed work.

## Team lead verification checklist

A team lead can treat onboarding as accepted only if all of these are true:

- every user can reach `/kb setup` without ad hoc rescue steps,
- every user ends up with the same baseline layer-graph contract,
- every user gets the same first useful `/kb status` and `/kb start-day` behavior,
- the first cross-layer promote or digest path works and is understandable,
- no user needed hidden knowledge about install vs init,
- the first capture path makes external fetch behavior explicit,
- the resulting workspace is understandable by another human reviewer.

If any of these fail, the rollout is not deterministic enough yet.

## Failure signals that must create follow-up work

Create or reopen an issue if any of these occur:

- `/kb setup` exists, but the install path is still ambiguous,
- the scaffold differs by harness in undocumented ways,
- setup succeeds, but `/kb status`, `/kb start-day`, or the first cross-layer flow is structurally wrong,
- placeholder tokens survive setup,
- the first capture path hides whether external material was fetched,
- a second human cannot quickly verify the same contract from the produced workspace.

## Related

- [README.md](../README.md)
- [REFERENCE.md](./REFERENCE.md)
- [first-hour.md](./examples/first-hour.md)
- [plugins/kb/skills/kb-setup/SKILL.md](../plugins/kb/skills/kb-setup/SKILL.md)
- [plugins/kb/skills/kb-setup/references/setup-flow.md](../plugins/kb/skills/kb-setup/references/setup-flow.md)

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-30 | v5.5.0: added the optional product-management proof path so first-run acceptance covers setup-derived roadmap/journey ownership, source/output placement, and read-only dry-run validation when role/goals imply those artifacts | Product-management surface integration |
| 2026-04-25 | v5.2.0: replaced the flat 13-question baseline with the four-phase, goal-oriented interview (Phase 1 context/goals, Phase 2 workspace facts, Phase 3 derived plan to confirm, Phase 4 single yes) so the canonical proof matches the new kb-setup behavior. Layer features and contributor-mode flags are now derived in Phase 3 from the user's own answers, not enumerated by the user. Q7 baseline answer pinned to "confirm everything" so the derived automation level stays at 1 (manual only) per the existing baseline | v5.2.0 setup rework |
| 2026-04-25 | Clarified the baseline automation answer so level 1 is explicitly the manual-only setup path | Deep spec-audit follow-up |
| 2026-04-25 | Concept-audit follow-up: aligned the doc version with the 5.1.x framework and added an optional migration-proof step covering `/kb migrate layer-model` and `/kb migrate archives` for legacy adopters | Concept-audit drift correction |
| 2026-04-25 | Reworked the deterministic onboarding proof for 5.0.0: baseline now proves a two-layer graph, verifies year-based archives and notes, and requires one cross-layer promote or digest path before acceptance | v5.0.0 flexible layer model |
| 2026-04-24 | Added Gemini CLI and Kiro IDE install-phase acceptance checks, updated Codex CLI to the `.agents/skills/` workflow, and added an export-backed roadmap proof step | Harness and roadmap proof correction |
| 2026-04-22 | Exempted the presentation template placeholder scan from scaffold acceptance because those `{{…}}` markers are intentionally deferred for `/kb present` | Fixes #17 |
| 2026-04-22 | Added Codex CLI acceptance guidance and clarified the difference between first-class supported harnesses and compatible CLI workflows | Compatibility expansion |
| 2026-04-20 | Initial deterministic first-run acceptance path for onboarding verification | Issue #6 |
