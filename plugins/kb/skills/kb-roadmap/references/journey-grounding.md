# Reference: journey grounding

Journeys are the **ground truth** for what should become reality. Tracker items describe *intent to build something*; journeys describe *what the product must actually do*. When the two diverge, the journey wins — the roadmap is there to close the gap, not the other way round.

This reference defines how `kb-roadmap` uses `kb-journeys` artifacts as a reference, a review lens, and a consistency check for every roadmap run.

## Roles a journey plays for a roadmap

| Role | What it means |
|---|---|
| **Reference** | Every **non-infrastructural** roadmap item should trace to one or more journey steps it exists to deliver. Steps without roadmap coverage are candidate-next-work. |
| **Review challenge** | During `/kb roadmap review` and `/kb roadmap refine`, every item is challenged against the journey step(s) it claims to serve: does the proposed change actually move that step from its current readiness to a higher one? |
| **Consistency check** | `digest` + `audit` runs cross-check that every item tagged with a journey step id exists, and that every step claimed by any item is still present in the journey source. |
| **Drift finding** | When delivery signals contradict the journey (step marked green by readiness but delivery is incomplete; step blocked but items appear shipped), emit a finding routed through the normal mismatch-findings pipeline. |

## Infrastructure / foundational escape hatch

Not every roadmap item maps to a journey step. Infrastructure, build, security-hardening, platform, test-harness, and foundational work exist **to enable** journeys without directly advancing one. An item satisfies the journey-coverage rule without a step citation when any of these are true:

- Tracker label matches `roadmap.audit.infra-labels` (default: `infra`, `foundational`, `platform`, `tech-debt`, `security`, `compliance`, `build`, `ci`, `test-harness`)
- Item body contains a `Classification: infrastructural` or `Classification: foundational` trailer
- Item is explicitly linked to an ADR (the ADR replaces the journey citation)

Items using the escape hatch are listed separately in audit reports as *"justified infra work"* so classification is still auditable. See `audit.md` R1 for the full rule.

## Binding a scope to journeys

Each roadmap scope can declare journey references:

```yaml
roadmap:
  scopes:
    <scope-name>:
      kind: detail
      journey-refs:
        - source: <journey-source-name>    # name of a journey config in .kb-config/layers.yaml under journeys:
          filter:
            tiers: [t1, t2]                # optional — restrict to these tiers
            phases: [1.1, 1.2, 1.3]        # optional — restrict to these journeys
          require-coverage: true            # every item in scope should cite ≥1 journey step
          coverage-warn-only: false         # if true, missing coverage logs warn instead of finding
```

The skill reads the adopter's `journeys:` block from the same config file, then resolves step ids against the journey source on each run.

## Citing journeys from tracker items

Adopters use a stable notation in ticket descriptions, PR bodies, or commit trailers:

```
journey: J1.3-S4
journey: J1.3-S4, J1.4.2-S1          # multiple
journeys: J1.1-S1-S3                 # step range shorthand (inclusive)
```

The skill parses these out of the raw item text using the configured `journeys.citation-pattern` (default: `journeys?:\s*([A-Z][\w.,\s-]+)`). Any step id that does not resolve to the journey source is flagged as a citation error in the roadmap's mismatch findings.

## Consistency checks (run on every `digest` + `roadmap`)

| Check | Output |
|---|---|
| **Unknown journey step cited by item** | Finding, class `journey-citation-broken`, routed to `_kb-references/findings/` |
| **Journey step with no item coverage** | Finding, class `journey-uncovered`, class-level summary in section E |
| **Journey step marked feasible but blocking item shipped** | Finding, class `journey-reality-mismatch`, cites item + step |
| **Item claims to deliver step N, but the work is unrelated** | Detected via tier-4 deep-investigation when enabled — `proposed, pending review` |
| **Journey step renamed / id rewritten** | Warning with diff; prompt to run `/kb journeys rename-id` or update the citation |

All consistency findings feed the same mismatch-findings pipeline as delivery-plan mismatches. Noise filters apply.

## Artifact impact

Adds a dedicated subsection inside section **C. Correlation matrix**:

```
C.4 Journey coverage
- 47 items cite a journey step (91% of scope)
- 4 items cite a non-existent step (see findings)
- 12 journey steps are uncovered by any item (see section E)
- 3 steps show journey-vs-delivery drift (see findings)
```

And a dedicated subsection inside section **E. Mismatch findings**:

- `journey-uncovered` — step with no tracker coverage (**candidate-next-work**)
- `journey-citation-broken` — item cites unknown step
- `journey-reality-mismatch` — readiness claim contradicts delivery signal

And a dedicated subsection inside section **F. Forward plan**:

- Steps trending from amber → green this period
- Steps newly red or blocked
- Highest-impact uncovered steps (proposed as next items)

## Authoring-command behaviour

Journey grounding is enforced in the four authoring commands. See also `authoring-commands.md`.

| Command | Journey-grounding action |
|---|---|
| `ideate` | If the seed is a journey step, generate items that advance its readiness. If the seed is an item, cite the journey step(s) it serves (or flag `needs-journey-link`). |
| `discuss` | Treat the journey as the third party in the critique — *"the journey says this step should be green in Q3; the item doesn't move that needle."* |
| `review` | Every proposed todo must cite a journey step. The review fails if any item in scope lacks journey coverage **and** `require-coverage: true`. |
| `refine` | Acceptance criteria must reference the journey step they advance. If the acceptance criteria would change the journey (e.g. the step itself needs more detail), emit a suggestion to open `/kb journeys review <step>` before proceeding. |

## Updating journeys from findings

When a roadmap run finds that reality has diverged from the journey, the journey is **not silently updated**. Instead:

1. The finding is recorded under `_kb-references/findings/YYYY-MM-DD-journey-drift-<step-id>.md`.
2. The finding offers a one-click transition to `/kb journeys review <step-id>` with the finding pre-loaded as context.
3. Journey edits go through the standard journey authoring arc (`review` → `refine`). Only after the journey is re-authored does the drift finding resolve.

This ensures the journey remains a deliberate document — never a silent shadow of delivery.

## Configuration summary

Added under `.kb-config/layers.yaml` `roadmap:`:

```yaml
roadmap:
  # ... existing config ...
  journey-grounding:
    enabled: true
    citation-pattern: "journeys?:\\s*([A-Z][\\w.,\\s-]+)"
    require-coverage-default: false        # per-scope override takes precedence
    findings:
      route-classes: [journey-uncovered, journey-citation-broken, journey-reality-mismatch]
      min-uncovered-to-find: 1              # suppress spam when entire journey is future work
```
