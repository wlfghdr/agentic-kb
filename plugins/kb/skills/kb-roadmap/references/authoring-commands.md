# Reference: item authoring commands

> **Version:** 7.0.0 | **Last updated:** 2026-09-17

Roadmap items move through a creative and critical authoring arc before they enter the delivery pipeline. The skill ships four dedicated authoring commands, each with a distinct stance:

| Command | Stance | Produces |
|---|---|---|
| `ideate` | **creative** — generate, expand, connect | New roadmap item(s) or a seeded item body |
| `discuss <item>` | **challenging** — devil's advocate | No file writes; a structured critique + open questions |
| `review <item>` | **hybrid** — challenge then create | Feedback, risks, todos, mitigations, further ideas appended to the item |
| `refine <item>` | **actionable** — delivery-shaped | Implementation plan sections appended to the item |

All four operate on the canonical roadmap item selected by `primitive-storage.roadmap-items`. In `files` mode that is `_kb-roadmaps/<scope>/items/R-*.md`; in `tracker` mode it is the tracker item, with only an optional configured summary/backlink written locally; in `hybrid` mode it is the file until the confirmed promotion transfers canonical ownership to the tracker. They respect the state markers from `state-machine.md` and the phase pipeline from `phase-gates.md`.

## Common contract

Every authoring command:

1. Locates the item — either by path or by id lookup in the scope's index.
2. Reads the full item + any linked plan item from the configured tracker (if one exists).
3. Applies its stance via the instructions below.
4. Writes output into the canonical item's authoring history under a dedicated section, prefixed with a timestamp marker where the backing store supports it. File-backed items append to the body; tracker-backed items append one structured comment.
5. Appends a state marker transition in that same history entry if the stance produces one (`ideate` → `draft`, `review` → `reviewed`, etc.). Tracker readers resolve the latest marker across the item body and ordered authoring comments.
6. Never transitions phase gates silently — gate changes require `/kb roadmap --check-gates` + user confirmation.

Item body layout after authoring passes:

```markdown
# <title>

<!-- id: R-YYYY-MM-DD-slug -->
<!-- phase: idea @ 2026-04-21T10:00Z -->
<!-- status: draft @ 2026-04-21T10:00Z -->

## Summary
...

## Ideation (2026-04-21)
<!-- authored-by: ideate @ 2026-04-21T10:15Z -->
...

## Critique (2026-04-21)
<!-- authored-by: discuss @ 2026-04-21T11:00Z -->
...

## Review (2026-04-21)
<!-- authored-by: review @ 2026-04-21T14:00Z -->
### Challenge
### Creative
### Risks
### Todos & mitigations

## Refinement (2026-04-21)
<!-- authored-by: refine @ 2026-04-21T15:30Z -->
### Implementation plan
### Acceptance criteria
### Open questions
```

Re-running a command appends a new timestamped section; it does not overwrite previous output. History is preserved in the file body or, for tracker-backed items, in ordered structured comments.

---

## `ideate` — creative pass

Turns a seed (KB idea, decision, informal note, or empty prompt) into one or more roadmap items.

### Inputs

- A KB idea file (`_kb-ideas/I-*.md`) → seeds one roadmap item per idea
- A KB decision (`_kb-decisions/D-*.md`) → derives follow-up roadmap items from the decision's *consequences* section
- A free-text prompt → generates a candidate item from scratch
- No input → scans the adopter's KB for unlinked ideas/decisions that could become roadmap items; proposes a shortlist

### Stance rules

- **Generate**, don't filter. Propose 2–5 variants when there is room to expand.
- **Connect**. Cross-reference the scope's existing items; flag overlaps and near-duplicates (but still propose the item; the user decides).
- **Name the value**. Every generated item must include a one-sentence *why this matters* tied to a goal, workstream theme, or declared VMG.
- **Propose phase `idea`**. Ideation never commits; the resulting item opens at phase `idea` with `status: draft`.
- **Never invent identifiers that belong to external trackers.** If a linked tracker item should exist, emit a *proposed tracker entry* block the user can copy-paste or apply via `sync`.

### Command shapes

```
/kb roadmap ideate --scope NAME [--from <idea-or-decision-path>] [--apply]
/kb roadmap ideate --scope NAME --prompt "text" [--apply]
/kb roadmap ideate --scope NAME [--apply]       # scans for unlinked seeds, proposes shortlist
```

### Output

For each accepted item, branch on `primitive-storage.roadmap-items`: `files` writes `_kb-roadmaps/<scope>/items/R-YYYY-MM-DD-slug.md`; `tracker` proposes or creates the canonical tracker item and may write only the configured summary/backlink after its identifier is known; `hybrid` writes the file until its later confirmed promotion. Never create both an active `R-*.md` item and a tracker item for the same canonical work. Unaccepted candidates are logged to `.kb-log/YYYY-MM-DD.log` with rationale — visible on the next invocation so the user sees what was *not* taken.

---

## `discuss` — devil's advocate

Challenges an existing item. **Writes nothing by default** — output is in-chat, optionally written under `## Critique` only when the user explicitly asks.

### Stance rules

- **Challenge every assumption.** Read the item, extract declarative statements, test each against evidence (other items, decisions, findings, linked tracker data).
- **Ask, don't tell.** Produce a numbered list of questions and counterpoints, not a rewrite.
- **Surface contradictions** with existing items, decisions, or workstream VMG — cite the conflicting file path + section.
- **Scan for hedging** ("i think", "probably", "should be", "assuming", "likely", "might") and surface each match as an unstated assumption the item depends on.
- **Steel-man the alternative.** For at least one critical point, describe the strongest version of the opposing view.
- **No new content.** Do not propose solutions, risks, or todos — those belong to `review`.

### Command shape

```
/kb roadmap discuss <item-path-or-id> [--scope NAME] [--write] [--apply]
```

`/discuss` mode (the global write-free mode from `references/discuss-mode.md`) applies automatically to this command — `discuss` is write-free by default. To persist the critique, re-run with `--write` for a file-backed item or `--apply` for a tracker-backed item.

### Output

In-chat structured critique:

```
Challenges (N)
  1. <one-line claim>  — counterpoint, evidence pointer
  2. ...
Contradictions (N)
  1. Conflicts with <path#section>: <nature of conflict>
Hedges (N)
  1. "probably" in §2 — uncertainty about <topic>
Steel-man
  <strongest opposing view in 1–3 sentences>
Open questions (N)
  1. ...
```

With `--write`, the same content is appended as a `## Critique (<date>)` section in a file-backed item. With `--apply`, it is posted as a structured comment on a tracker-backed item after the normal mutation gates pass.

---

## `review` — challenging and creative

The hybrid pass. First runs the `discuss` stance, then pivots into creative contribution: risks, todos, mitigations, and additional ideas.

### Stance rules

- **Do `discuss` first.** Section 1 of the output is the critique (condensed — top 3 challenges, top 3 contradictions, hedges above threshold).
- **Then create.** Section 2 lists risks with severity (blocker / warning / info), and section 3 maps each high-severity risk to at least one mitigation or todo.
- **Propose adjacent ideas.** Section 4 proposes 2–4 *additional ideas* — items that would complement, de-risk, or accelerate this one. Each proposed idea is a one-liner with enough context to feed `ideate --from` in a follow-up.
- **Identify todos, not task titles.** Each todo states the *outcome* in present tense ("delivery signal reaches main with acceptance met") so downstream `refine` can translate to concrete tasks.
- **Evidence cites required.** Every risk, todo, and adjacent idea points to a source (KB topic, finding, decision, tracker item, or prior item section).

### Command shape

```
/kb roadmap review <item-path-or-id> [--scope NAME] [--discuss-only] [--apply]
```

`--discuss-only` stops after the critique section (use this when you want the `discuss` output in the item body without the creative contribution).

### Output

Appends `## Review (<date>)` to the item body with:

```markdown
### Challenge
- condensed critique with evidence
### Creative
- adjacent ideas that would strengthen, de-risk, or accelerate
### Risks
- [blocker] <risk> — evidence: <file#section>
- [warning] <risk> — evidence: <file#section>
### Todos & mitigations
- [for <risk-id>] <outcome-shaped todo>
```

Transitions the item's `status: draft` to `status: reviewed` marker on success. For a tracker-backed item, the structured review comment contains both the `## Review (<date>)` section and `<!-- status: reviewed @ <timestamp> -->`; the ordered comment stream is the canonical authoring history, so no separate body-update capability is required. A second `review` run appends a new section or comment — the marker history records the re-review.

---

## `refine` — implementation plan

Turns a reviewed item into actionable delivery detail. Stance is **engineering-grounded, not inspirational** — the pass that leaves ambiguity on the floor.

### Stance rules

- **Require prior review.** Refuses to run if the item's latest status marker is `draft` (never `reviewed`). Override with `--force`; the override is logged.
- **Decompose outcomes into tasks.** Every todo from the review becomes 1–N concrete tasks with: scope, owner placeholder, rough size (S/M/L), dependency list.
- **Name the acceptance criteria** in present-tense, testable terms — one per key behavior or interface.
- **Identify interfaces + contracts.** If the item touches APIs, file formats, or protocols, list them with current state and target state.
- **List open questions explicitly.** If any question blocks delivery start, mark it with `[blocks-start]`.
- **Never promise dates.** The refine output is sequencing and sizing, not scheduling.
- **Propose a gate transition.** If the refined content appears to satisfy the `defined` gate criteria, emit a `[propose] phase: defined` line at the bottom of the section. The user verifies it with `/kb roadmap --check-gates --scope <name>`, then applies the reviewed transition through `/kb roadmap sync --scope <name> --apply` and its per-write confirmation.

### Command shape

```
/kb roadmap refine <item-path-or-id> [--scope NAME] [--force] [--apply]
```

### Output

Appends `## Refinement (<date>)` with:

```markdown
### Implementation plan
- T1 <task title> (size: S, deps: —)
- T2 <task title> (size: M, deps: T1)
...
### Acceptance criteria
- AC1 <testable statement>
- AC2 <testable statement>
### Interfaces & contracts
- <name> — current: <state>, target: <state>
### Open questions
- [blocks-start] <question>
- <question>
### Proposed next gate
[propose] phase: defined
```

---

## Authoring + trackers

When `primitive-storage.roadmap-items` selects a tracker, each authoring command may offer (but never silently perform) the operation declared by the matching canonical connection:

| Command | Offered tracker write |
|---|---|
| `ideate` | Propose a new canonical roadmap item; apply only when `primitive-storage.roadmap-items` selects the tracker and its connection declares `create` |
| `discuss` | Post critique on the canonical tracker item only when its connection declares `comment` |
| `review` | Post one structured comment containing the review section, top risks, and `reviewed` state marker on the canonical tracker item only when its connection declares `comment` |
| `refine` | Post the implementation plan and proposed `defined` transition when the canonical connection declares `comment`; `--check-gates` only verifies criteria, and applying the reviewed transition later through `sync --apply` separately requires `status` |

All tracker writes are gated by `--apply` + interactive confirmation, matching the safety rules in `issue-trackers.md`.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-09-17 | Routed reviewed phase application through confirmation-gated `sync --apply`; `--check-gates` remains read-only | PR #153 review |
| 2026-09-17 | Added `--apply` to tracker-capable authoring command grammar and limited `refine` itself to the `comment` capability; a later gate transition independently requires `status` | PR #153 review |
| 2026-09-16 | Defined structured tracker comments as the canonical authoring history for review sections and state markers, avoiding an undeclared body-update capability | PR #153 review |
| 2026-09-16 | Made every authoring command storage-mode-aware so tracker mode operates on one canonical tracker item and writes only an optional local summary/backlink | PR #153 review |
| 2026-09-16 | Version aligned to 7.0.0 and authoring writes moved from legacy `write-*` names to canonical ownership and connection capabilities | Issue #152 review |
| 2026-06-02 | Added required version/changelog metadata so plugin specs and references are covered by the consistency check | Issue #144 |
