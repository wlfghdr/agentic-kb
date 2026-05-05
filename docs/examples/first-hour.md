# First Hour — Zero to First Useful Layer Graph

> **Version:** 5.5.1 | **Last updated:** 2026-05-05

This walkthrough covers the minimum path from nothing installed to the first useful `/kb` responses in a freshly initialized workspace. Target audience: a developer who wants to prove the adoption path end-to-end in under an hour.

## Prerequisites (5 min)

| Tool | Check | If missing |
|------|-------|-----------|
| `git` | `git --version` | install it first |
| One supported harness | open the harness | install it first |
| Optional compatible CLI workflow: Codex CLI | `codex --help` | optional |
| `gh` | `gh --version` | recommended, not required |

Stop here if `git` or the harness is missing. `/kb setup` will stop anyway.

## Phase 1 — Install the skill surface (5 min)

Marketplace install or `scripts/install` makes `/kb setup` callable. The install phase is successful when the harness can invoke `/kb setup` in the target workspace and the surface survives a restart.

## Phase 2 — Initialize the workspace (20 min)

Run:

```text
/kb setup
```

The wizard runs the four-phase, goal-oriented interview. You never enumerate layers, features, or contributor-mode flags yourself — the wizard derives them from your prose and shows the proposal back in phase 3.

**Phase 1 — context and goals (open prose, Q1–Q8):**

| Question | Suggested first-run answer |
|----------|----------------------------|
| Q1 — Who you are | `alice — engineer on distributed systems; caching, reliability, observability` |
| Q2 — What you're trying to track or decide | `incidents and slow queries that hint at deeper reliability issues` |
| Q3 — Why now | `too many parallel investigations; my lead keeps asking for status` |
| Q4 — Who else needs to see what | `me and one team — observability` |
| Q5 — Where information feeds in | `our product repo, GitHub issues, weekly observability sync` |
| Q6 — What you want out | `morning briefing and a Friday status I can share with my lead` |
| Q7 — How autonomous | `confirm everything before anything is written` |
| Q8 — Operating context today, target in 6 months | `human-only / capture discipline today; agent-assisted triage in 6 months` |

**Phase 2 — workspace and harness facts (Q9–Q11):**

| Question | Suggested first-run answer |
|----------|----------------------------|
| Q9 — Workspace root | current directory |
| Q10 — IDE targets | current harness only |
| Q11 — Discovery pass | accept the empty baseline |

**Phase 3 — confirm the wizard's derived plan (Q12–Q15):** the wizard shows a single block with the proposed layer graph (`alice-personal` + `team-observability`), the adoption-stage label (`Stage 1 — capture discipline`), the connections derived from Q5, the dashboard panels matching Q6, automation level `1` (manual only — consistent with Stage 1), the graduation criteria for moving to Stage 2, and HTML styling `builtin`. Accept as proposed.

**Phase 4 (Q16):** one yes.

Check for success:

- `.kb-config/layers.yaml` exists in `alice-personal/` and names both layers with `workspace.anchor-layer: alice-personal`,
- `.kb-config/automation.yaml` carries the chosen `adoption-stage` and a `level` consistent with Stage 1,
- `_kb-references/foundation/me.md` records the same adoption stage,
- year-based archive directories exist,
- `index.html` and `dashboard.html` exist in both layers,
- no unresolved placeholders remain outside deliberate presentation templates.

## Phase 3 — First four commands (20 min)

### `/kb status`

Expected shape:

```text
What I did: Checked your KB status.
Where it went: read alice-personal/.kb-config/layers.yaml, alice-personal/_kb-tasks/focus.md, alice-personal/.kb-log/...
Gate notes: n/a.
Suggested next steps:
  - Run /kb start-day
  - Capture something with /kb <URL-or-text>
  - Try /kb note meeting <topic>
```

### `/kb start-day`

Expected behavior: read-only briefing, no invented work, clear next actions, and no hidden assumptions about team or company state.

### `/kb <paste-a-URL>`

```text
/kb https://example.com/article-about-caches
```

Expected behavior: the skill says whether it fetched external content, applies the five-question evaluation gate, writes a finding under `alice-personal/_kb-references/findings/YYYY/`, possibly updates a topic, logs the operation, and refreshes `index.html` and `dashboard.html`.

### `/kb promote <file> team-observability`

Expected behavior:

1. names source and destination layers,
2. stages the intake in the destination contributor area,
3. completes the destination-layer review,
4. archives the staged copy under `digested/YYYY/MM/`,
5. refreshes the destination `index.html` and `dashboard.html`.

If the command targets a `role: consumer` layer, it must refuse clearly.

## What to do when this walkthrough breaks

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `/kb setup` is not offered | Install phase did not complete | Re-run marketplace install or `scripts/install`, restart the harness |
| Scaffolded files contain literal `{{USER_NAME}}` etc. | Post-write check skipped or an interview answer was empty | Re-run `/kb setup`; it is idempotent |
| `/kb status` returns nothing or crashes | `.kb-config/layers.yaml` invalid or the anchor layer is incomplete | Re-run `/kb setup` or fix the config |
| URL capture prints nothing | The skill could not fetch the URL | Paste the text directly |
| Promotion fails unexpectedly | Target layer role or path is wrong | Inspect `.kb-config/layers.yaml` and confirm the target layer is contributor-capable |

## Related

- [REFERENCE.md](../REFERENCE.md)
- [first-run-acceptance.md](../first-run-acceptance.md)
- [day-in-the-life.md](day-in-the-life.md)
- [kb-setup SKILL.md](../../plugins/kb/skills/kb-setup/SKILL.md)

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-05 | v5.5.1: replaced the legacy block-and-answer table that asked the user to enumerate layers, features, and contributor-mode flags with the goal-oriented four-phase interview (Q1–Q8 prose, Q9–Q11 admin, Q12–Q15 confirm-the-derived-plan, Q16 final yes), matching `kb-setup/SKILL.md` since v5.4.0. Success checks now also assert that the chosen adoption stage is durable in `automation.yaml` and `foundation/me.md` | Onboarding consistency review |
| 2026-04-25 | Aligned the walkthrough with the acceptance baseline: Stage wording became Phase wording, the sample layer answers now include the parent graph fields, and automation level 1 is called out as manual-only | Deep spec-audit follow-up |
| 2026-04-25 | Reworked the walkthrough for 5.0.0: setup now proves a two-layer graph, year-based archives, notes, and the first cross-layer promote path | v5.0.0 flexible layer model |
| 2026-04-24 | Updated the Codex walkthrough to the installed `.agents/skills/` flow instead of the older bootstrap-only wording | Harness docs correction |
| 2026-04-22 | Exempted the presentation template placeholder scan from the first-run success criteria because those `{{…}}` markers are intentionally deferred for `/kb present` | Fixes #17 |
| 2026-04-20 | Updated the walkthrough to match automatic overview regeneration after every `/kb` mutation | v3.2.0 live-overview refresh |
| 2026-04-18 | Initial walkthrough — zero-to-first-briefing in three stages | First-hour fixture |
