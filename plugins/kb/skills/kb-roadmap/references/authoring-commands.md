# Reference: item authoring commands

Roadmap items move through a creative and critical authoring arc before they enter the delivery pipeline. The skill ships four dedicated authoring commands, each with a distinct stance:

| Command | Stance | Produces |
|---|---|---|
| `ideate` | **creative** — generate, expand, connect | New roadmap item(s) or a seeded item body |
| `discuss <item>` | **challenging** — devil's advocate | No file writes; a structured critique + open questions |
| `review <item>` | **hybrid** — challenge then create | Feedback, risks, todos, mitigations, further ideas appended to the item |
| `refine <item>` | **actionable** — delivery-shaped | Implementation plan sections appended to the item |

All four operate on items inside `_kb-roadmaps/<scope>/items/` (markdown files, one per item). They respect the state markers from `state-machine.md` and the phase pipeline from `phase-gates.md`.

## Common contract

Every authoring command:

1. Locates the item — either by path or by id lookup in the scope's index.
2. Reads the full item + any linked plan item from the configured tracker (if one exists).
3. Applies its stance via the instructions below.
4. Writes output into the item body under a dedicated H2 section, prefixed with a timestamp comment for audit.
5. Appends a state marker transition if the stance produces one (`ideate` → `draft`, `review` → `reviewed`, etc.).
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

Re-running a command appends a new timestamped section; it does not overwrite previous output. History is preserved in the file.

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
/kb roadmap ideate --scope NAME [--from <idea-or-decision-path>]
/kb roadmap ideate --scope NAME --prompt "text"
/kb roadmap ideate --scope NAME                 # scans for unlinked seeds, proposes shortlist
```

### Output

Writes `_kb-roadmaps/<scope>/items/R-YYYY-MM-DD-slug.md` for each accepted item. Unaccepted candidates are logged to `.kb-log/YYYY-MM-DD.log` with rationale — visible on the next invocation so the user sees what was *not* taken.

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
/kb roadmap discuss <item-path-or-id> [--scope NAME]
```

`/discuss` mode (the global write-free mode from `references/discuss-mode.md`) applies automatically to this command — `discuss` is write-free by default. To persist the critique into the item body, re-run with `--write`.

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

With `--write`, the same content is appended as a `## Critique (<date>)` section.

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
/kb roadmap review <item-path-or-id> [--scope NAME] [--discuss-only]
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

Transitions the item's `status: draft` to `status: reviewed` marker on success. A second `review` run appends a new section — the marker history records the re-review.

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
- **Propose a gate transition.** If the refined content satisfies the `defined` gate criteria, emit a `[propose] phase: defined` line at the bottom of the section. The user applies via `/kb roadmap --check-gates` + confirm.

### Command shape

```
/kb roadmap refine <item-path-or-id> [--scope NAME] [--force]
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

When the scope has a tracker with `write-*` capabilities declared, each authoring command offers (but never silently performs) a tracker side-effect:

| Command | Offered tracker write |
|---|---|
| `ideate` | Create a new tracker item (if `write-item`) — dry-run preview first |
| `discuss` | Post critique as a comment on the linked tracker item (if `write-comments`) |
| `review` | Post a review summary + top risks as a comment (if `write-comments`) |
| `refine` | Attach the implementation plan as a comment and propose a status transition to `defined` (if `write-comments` + `write-status`) |

All tracker writes are gated by `--apply` + interactive confirmation, matching the safety rules in `issue-trackers.md`.
