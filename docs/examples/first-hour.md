# First Hour — Zero to First Useful Layer Graph

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

**Phase 1 — workspace and harness facts (frontloaded admin, Q1–Q3):**

| Question | Suggested first-run answer |
|----------|----------------------------|
| Q1 — Workspace root | current directory |
| Q2 — IDE targets | current harness only |
| Q3 — Discovery pass | accept the empty baseline |

**Phase 2 — context and goals (open prose, Q4–Q11):**

| Question | Suggested first-run answer |
|----------|----------------------------|
| Q4 — Who you are | `alice — engineer on distributed systems; caching, reliability, observability` |
| Q5 — What you're trying to track or decide | `incidents and slow queries that hint at deeper reliability issues` |
| Q6 — Why now | `too many parallel investigations; my lead keeps asking for status` |
| Q7 — Who else needs to see what | `me and one team — observability` |
| Q8 — Where information feeds in | `our product repo, GitHub issues, weekly observability sync` |
| Q9 — What you want out | `morning briefing and a Friday status I can share with my lead` |
| Q10 — How autonomous | `confirm everything before anything is written` |
| Q11 — Operating context today, target in 6 months | `human-only / capture discipline today; agent-assisted triage in 6 months` |

**Phase 3 — confirm the wizard's derived plan (Q12–Q15):** the wizard shows a single block with the proposed layer graph (`alice-personal` + `team-observability`), the adoption-stage label (`Stage 1 — capture discipline`), the connections derived from Q8, the dashboard panels matching Q9, automation level `1` (manual only — consistent with Stage 1), the graduation criteria for moving to Stage 2, and HTML styling `builtin`. Accept as proposed.

**Phase 4 (Q16):** one yes.

Check for success:

- `.kb-config/layers.yaml` exists in `alice-personal/` and names both layers with `workspace.anchor-layer: alice-personal`,
- `.kb-config/automation.yaml` carries the chosen `adoption-stage` and a `level` consistent with Stage 1,
- `_kb-references/foundation/me.md` records the same adoption stage,
- year-based archive directories exist,
- `index.html` and `dashboard.html` exist in both layers,
- no unresolved placeholders remain outside deliberate presentation templates.

### Setup closing — the first win

Setup ends with Step 7 (`SKILL.md` "Step 7 — First win + next-steps shortlist"), not with Step 6 verification. The wizard offers one optional bootstrap capture and emits a curated 3–5 command shortlist tailored to your adoption stage. Take the bootstrap capture if you have any URL, file, or short text ready — say "no" otherwise. Either way, the wizard closes with a short, named summary like *"Setup complete. Try `/kb capture <text>`, `/kb start-day`, `/kb note meeting <topic>` next."*

This is the moment you have a visible artifact. If you captured something, open the anchor layer's `index.html` in a browser — your first finding is there.

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
