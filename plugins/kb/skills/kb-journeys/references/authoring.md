# Reference: journey authoring commands

`kb-journeys` shares the four-command authoring arc with `kb-roadmap` (`ideate` / `discuss` / `review` / `refine`), with journey-specific deltas. See `kb-roadmap/references/authoring-commands.md` for the shared stance contract.

## Shared contract

All four commands:

1. Locate the target (journey slug, step id, or sub-journey file).
2. Read the journey metadata + referenced sections.
3. Apply the stance.
4. Append output under a dated H2 inside the markdown file — never overwrite existing content.
5. Append a state marker when the stance produces one (`drafted`, `reviewed`, etc.).

## Deltas per command

### `ideate`

Journey-specific creative pass. Inputs:

- A persona description → generate candidate journey outline (phases → sub-journeys → steps).
- An existing roadmap item → generate the user-facing journey fragment that would deliver it.
- A free-text prompt (e.g. *"how should a first-time admin recover from a failed deploy?"*) → journey stub.
- No input → scans the adopter's KB for unlinked personas or roadmap items that could become journey fragments.

Journey-specific rules on top of the shared stance:

- Always propose **alternates** alongside the happy path — at least one named failure route per step that interacts with an external system.
- Always name the **actor** ([CLI], [WEB UI], [AGENT], [SYSTEM], [PERSONA]) for every step.
- Always tag a **target duration** on the generated journey.

### `discuss <journey>`

Devil's advocate on a journey or sub-journey. Write-free by default.

Journey-specific rules:

- Test every step's entry/exit conditions against each other: does step N's exit satisfy step N+1's entry?
- Challenge each readiness chip — is the rationale one-liner justified by implementation state?
- Check interfaces against the counterpart journey's entry conditions; flag mismatches.
- Scan mocks for hedging ("this would probably show …", "eventually the user sees …") — same language scan as roadmap authoring.

### `review <journey>`

Challenge + create on a journey. Appends a `## Review (<date>)` section.

Journey-specific rules:

- **Challenge** section covers: entry/exit coherence, interface mismatches, missing alternates, readiness rationale weakness.
- **Creative** section proposes: adjacent sub-journeys, missing failure routes, additional mocks where critical moments are implied but not shown.
- **Risks** section specifically calls out: dependency risks on external systems, persona-handoff risks, readiness-vs-implementation gaps.
- **Todos** are outcome-shaped at step granularity ("step `J1.3-S4` renders the correct error branch when the API returns 429").

Transitions `drafted` → `reviewed` on success.

### `refine <journey>`

Implementation-plan pass. Appends a `## Refinement (<date>)` section.

Journey-specific rules (in addition to shared contract):

- **Decompose each step into instrumentation needs**: what event, what page, what CLI output, what API shape. Each becomes a testable acceptance criterion.
- **Name the mock production work** explicitly — if a step needs a new mock, list it with slug + target file location.
- **Identify cross-journey contract impacts** — if refining this journey changes its entry/exit conditions, list the counterpart journeys that must re-pass `review`.
- **Never invent actor identities** — refine uses only actors declared in the journey's metadata block + `journeys.actors` config.
- Propose an `in-delivery` gate transition when the step-level acceptance criteria all have implementation pointers.

## Tracker integration

When the scope's configured tracker supports it (see `kb-roadmap/references/issue-trackers.md`), journey authoring offers the same optional side-effects as roadmap authoring:

| Command | Offered tracker write |
|---|---|
| `ideate` | Create a tracker item for a delivery increment tied to a new step (dry-run preview first) |
| `discuss` | Post critique as a comment on the journey's linked tracker item |
| `review` | Post review summary + top risks as a comment |
| `refine` | Attach implementation plan and propose `defined` transition |

All tracker writes require `--apply` + interactive confirmation.

## Consuming roadmap findings

When `kb-roadmap` runs and the scope has `journey-refs` pointing at this journey skill, drift findings are routed to `_kb-references/findings/YYYY-MM-DD-journey-drift-<step-id>.md`. The finding offers a one-click transition into `/kb journeys review <step-id>` with the finding pre-loaded as context.

Journey `review` accepts the finding as an input argument:

```
/kb journeys review J1.3-S4 --from-finding 2026-04-21-journey-drift-J1.3-S4.md
```

When invoked this way, the review stance:

- Opens with the finding's evidence (what delivery signals contradict the readiness chip).
- Challenges the current readiness rationale against that evidence.
- Proposes a readiness downgrade OR a journey-text correction OR a new sub-step that captures the reality gap.
- On `/kb journeys refine` success, the drift finding is marked **resolved** and the journey is re-rendered.

This is the only supported path for journey edits driven by delivery drift. Journeys are **never** silently updated by roadmap runs.
