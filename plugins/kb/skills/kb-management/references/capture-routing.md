# Capture Routing — choosing the destination layer for a new artifact

This reference defines **which layer a `/kb` capture lands in**, and when the agent may write that artifact directly into a non-default layer without first staging it as a private finding for later promotion.

`/kb promote` moves material that **matured upward**. Capture routing is parallel, not a substitute: it answers the prior question of where a captured task, decision, note, or finding should live **the first time it is written**, when the destination is already clear and a private-first hop would just generate work.

## The three routing modes

Every `/kb [text/URL/path]` invocation picks exactly one of these modes. The agent must name the mode in the response so the user can intervene before mutation.

| Mode | Trigger | Mutation behavior |
|------|---------|-------------------|
| **Default (active layer)** | No explicit target named; agent has no strong reflection-based signal to prefer another layer | Capture into the active layer (the anchor unless context already selected a different contributor-capable layer). Apply the evaluation gate. Apply normally — no extra confirmation needed beyond the standard mutation transparency rules |
| **Explicit** | The user named a target layer in the invocation (e.g. `/kb team-observability <input>`, `/kb note team:platform <text>`), **or** a configured rule in `.kb-config/layers.yaml` (`capture-routing:` block — see "Configured routing rules" below) matches the source | Capture directly into the named layer, contributor scope if applicable. No extra confirmation step — the user already declared the routing |
| **Reflection-driven** | No explicit target was named, but the input's content, source, or context clearly implies a non-default layer (paste names another team's workstream, URL is from a connected team-layer source, etc.) | **Propose the target layer, name the reason, and wait for human confirmation before mutating.** Do not write to a non-default layer on inferred intent alone |

Default mode is the floor: when neither (b) nor a configured routing rule fires, captures land in the active layer and the agent proceeds without an extra prompt.

## Configured routing rules

A layer may declare per-source or per-pattern routing in `.kb-config/layers.yaml` so that recurring inputs of a known shape land in the right layer without per-invocation negotiation:

```yaml
layers:
  - name: team-observability
    scope: team
    role: contributor
    parent: engineering-org
    capture-routing:
      - source: github://acme/observability/issues/*
        primitive: task
        reason: Issues from this repo are team backlog by definition
      - source: paste-prefix: "TEAM-PLATFORM:"
        primitive: note
        reason: Convention for cross-team meeting notes
      - workstream: incident-response
        primitive: decision
        reason: Incident decisions are layer-canonical from the start
```

A configured rule is treated as an **explicit** routing instruction by the user (mode 2). The agent must:

1. cite the matching rule in the response (path + line or rule index),
2. apply the routing without a confirmation prompt,
3. log the routing decision in `.kb-log/YYYY-MM-DD.log` with the rule reference.

If two rules match the same input with different targets, the agent stops and asks the user to disambiguate. Configured routing is a first-class user instruction; the framework does not silently resolve a conflict in the user's stated preferences.

## The confirmation contract

For mode 3 (reflection-driven), the response must follow the standard "proposed mutation" shape from `output-contract.md`:

```
Proposed capture routing
  Default would be:  alice-personal (active layer)
  Proposed target:   team-observability  → _kb-tasks/backlog.md
  Reason:            Input names the team-observability workstream "tracing-coverage"
                     and the action item ("instrument the ingress span path") is
                     team-owned engineering scope, not personal sense-making.
  Visibility:        shared (multi-user contributor layer)
  Confirm? (yes / change target / capture to default instead)
```

Three rules tighten this:

- **Never write the artifact while waiting for confirmation.** No "soft write" to a staging area as a fallback. The mutation is gated on the explicit `yes`.
- **Always offer the default as a fallback.** The user must be able to fall back to "capture to the active layer instead" with one word, without re-explaining the input.
- **Re-confirm on each invocation.** A previous confirmation for the same target does not give the agent standing permission for future captures. Configured routing rules are the supported way to make a target sticky.

## Why direct routing matters

Three observed costs of forcing every capture through the private layer first:

1. **Routine team intake gets framed as private sense-making.** A meeting note about a team decision should not have to be promoted later; it was team-layer truth from the moment it was written.
2. **Tasks get duplicated.** A private "task" that later promotes to the team backlog leaves a backlink stub and a closure ritual that adds nothing — the team backlog was the correct destination from the start.
3. **Promotion semantics get diluted.** When promotion is the *only* way artifacts cross layers, the operation becomes routine plumbing instead of a real maturity claim.

Direct routing keeps the private layer for material that genuinely needs private incubation, and keeps `/kb promote` for material that genuinely matured.

## When direct routing is wrong

Direct routing is the wrong call when any of these hold; fall back to the default + later promote flow:

- The input contains material that may need redaction before it is layer-visible (secrets, PII, internal commentary about people).
- The artifact will likely be reshaped substantially as the author thinks it through (early decisions, ideas at `seed`).
- The target layer is `role: consumer`. Consumer layers refuse capture into them just as they refuse promote into them; route to the next contributor-capable layer instead.
- The target layer has not enabled the relevant feature (e.g. captured a `brief` against a layer without `delivery`). Refuse with a clear message and propose the active layer or `/kb setup` to enable the feature.
- The target layer declares `primitive-storage: tracker` for the primitive type and the tracker rules apply — propose the tracker mutation instead of a KB file write.

## Interaction with auto-promote

Direct routing is an interactive flow gated on the user (mode 2 or 3 confirmation). It does **not** apply at automation level 3's scheduled `auto-promote` step. Auto-promote remains scoped to the parent-edge walk and the `auto-promote.confidence-threshold` algorithm in `docs/REFERENCE.md` §6; it never picks a non-parent target. If a team wants new material to land in a non-default layer on a schedule, they should declare a `capture-routing:` rule (mode 2) and continue to use the gate + watermark machinery for promotion.

## Audit and concurrency

- `/kb audit` rule **K16** (`capture-routing-unconfirmed`) flags any captured artifact whose log entry shows mode 3 (reflection-driven) without a paired confirmation entry. A failed confirmation that produced a default-layer capture instead is not flagged — only writes to a non-default target without recorded confirmation.
- Configured routing rules participate in the concurrency rules in `docs/concurrency.md`: two contributors capturing into the same shared-target path on the same day apply the standard same-day suffix rule.
- The mutation that follows direct routing is otherwise identical to a normal capture: the evaluation gate runs, dashboards regenerate, and the log entry records source + destination + routing mode.

## Response expectations

A capture response must always state, in this order:

1. **Routing mode** — `default`, `explicit (user-named)`, `explicit (configured-rule:<id>)`, or `reflection-driven (confirmed)`.
2. **Source** — where the input came from.
3. **Destination** — layer + path written, with visibility (`shared` / `contributor-scoped`).
4. **Gate notes** — score and any borderline signals.
5. **Suggested next steps** — the usual 1–3 follow-ups.

For mode 3 the response **before** the mutation is the proposed-routing block above; after confirmation, the response uses the normal applied-mutation shape.

## Related

- [`../SKILL.md`](../SKILL.md) — core rules (rule 12 carries the confirmation contract)
- [`./command-reference.md`](./command-reference.md) — capture row + the `capture-routing:` config schema is referenced from §1
- [`./promote-contract.md`](./promote-contract.md) — the parallel upward flow
- [`./evaluation-gate.md`](./evaluation-gate.md) — the relevance gate, which runs after the destination layer is fixed
- [`./output-contract.md`](./output-contract.md) — the proposed-vs-applied response shapes
- [`../../../../../docs/REFERENCE.md`](../../../../../docs/REFERENCE.md) §1 "Capture-time layer routing"
- [`../../../../../docs/collaboration.md`](../../../../../docs/collaboration.md) — agent-vs-human responsibilities at each layer
- [`../../../../../docs/concurrency.md`](../../../../../docs/concurrency.md) — same-day collisions on direct-shared writes

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-23 | Initial reference. Codifies the three capture-routing modes (default / explicit / reflection-driven), the `capture-routing:` config schema, the mandatory confirmation gate for agent-inferred non-default targets, the "do not write while waiting for confirmation" rule, the audit rule K16, and the relationship to `/kb promote` and `auto-promote`. Closes the spec gap where direct cross-layer capture was implicitly possible (via "context selects another contributor-capable layer") but never named as a deliberate alternative to the private→shared promote chain | Artifact layer routing |
