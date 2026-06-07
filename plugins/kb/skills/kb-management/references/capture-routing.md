# Capture Routing — choosing the destination layer for a new artifact

> **Version:** 6.3.0 | **Last updated:** 2026-06-02

This reference defines **which layer a `/kb` capture lands in**, and when the agent may write that artifact directly into a non-default layer without first staging it as a private finding for later promotion.

`/kb promote` moves material that **matured upward**. Capture routing is parallel, not a substitute: it answers the prior question of where a captured task, decision, note, or finding should live **the first time it is written**, when the destination is already clear and a private-first hop would just generate work.

## The three routing modes

Every `/kb [text/URL/path]` invocation picks exactly one of these modes. The agent must name the mode in the response so the user can intervene before mutation.

| Mode | Trigger | Mutation behavior |
|------|---------|-------------------|
| **Default (active layer)** | No explicit target named; agent has no strong reflection-based signal to prefer another layer | Capture into the active layer (the anchor unless context already selected a different contributor-capable layer). Apply the evaluation gate. Apply normally — no extra confirmation needed beyond the standard mutation transparency rules |
| **Explicit** | The user named a target layer in the invocation (e.g. `/kb team-observability <input>`, `/kb note team:platform <text>`), **or** a configured rule in `.kb-config/layers.yaml` (`capture-routing:` block — see "Configured routing rules" below) matches the source | Capture directly into the named layer, contributor scope if applicable. No extra confirmation step — the user already declared the routing |
| **Reflection-driven** | No explicit target was named, but the input's content, source, or context matches the strong-signal rubric below for a non-default contributor-capable layer | **Propose the target layer, name the reason, and wait for human confirmation before mutating.** Do not write to a non-default layer on inferred intent alone |

Default mode is the floor: when neither **Explicit** (a user-named target or a configured `capture-routing:` rule) nor **Reflection-driven** (an agent-proposed target that the user confirmed) fires, captures land in the active layer and the agent proceeds without an extra prompt.

## Reflection-driven inference heuristics

Reflection-driven routing is intentionally narrower than "the agent has a hunch." The agent proposes a non-default target only when at least one strong signal points at a contributor-capable layer and no weak or ambiguous signal undermines that target. If the signal is weak, shared by multiple layers, or depends on private interpretation, fall through to **Default** and let the user promote later.

Strong signals — propose:

- The paste contains an exact-match workstream name declared by another contributor-capable layer, and the captured artifact is about that workstream's owned task, decision, meeting, or status.
- The URL host and repository/path match a `connections.product-repos[].remote` or `trackers[].repo` entry declared on another contributor-capable layer.
- The input prefix matches a stored `capture-routing:` pattern with a high-confidence partial match, such as a stable paste prefix where only the issue id, date, or meeting slug varies.

Weak signals — do not propose:

- Generic vocabulary overlaps with a workstream name but does not identify the owning layer or artifact scope.
- The URL is from a shared organization repository, tracker, or document space referenced by multiple layers and no path segment or configured rule distinguishes the owner.
- The input uses ambiguous abbreviations, aliases, project nicknames, or shorthand that could name more than one layer, workstream, or source.

Concrete examples:

Strong: a paste says, "Observability Pipeline standup: tracing-coverage is blocked until the ingress span owner accepts the schema update." If `tracing-coverage` is an exact workstream in the `team-observability` contributor layer and the action item belongs to that workstream, propose `team-observability` with that exact-match workstream reason.

Strong: the user captures `https://git.example.invalid/platform/observability/issues/418` and the `team-observability` layer declares `connections.product-repos[].remote: https://git.example.invalid/platform/observability` or `trackers[].repo: platform/observability`. The source matches the layer's configured connection, so propose `team-observability` and cite the matching connection field.

Strong: the paste begins `TEAM-PLATFORM: release readiness note` and a non-default contributor layer has a `capture-routing:` source pattern such as `paste-prefix:TEAM-PLATFORM:` that normally routes matching notes explicitly. If the configured rule is not an exact source match because the prefix is embedded in a forwarded message or lightly wrapped by another tool, treat the high-confidence partial prefix as reflection-driven: propose that layer, cite the stored pattern, and wait for confirmation.

Weak: a note says, "We need better platform reliability before launch," and a layer has a `platform-reliability` workstream. The phrase is generic planning vocabulary, not an exact workstream declaration or source binding, so capture to the active layer by default.

Weak: the user captures a URL from `https://git.example.invalid/company/shared-docs/...`, and both `team-observability` and `team-platform` reference that host in their connections. Without a more specific repository, path, tracker, or configured pattern, do not propose either layer; fall through to the active layer.

Weak: a paste says, "IR follow-up is ready," but the layer graph contains `incident-response`, `identity-reliability`, and `integration-runtime` workstreams or aliases. The abbreviation is ambiguous, so do not propose a reflection-driven target.

Tie-breaker: when multiple strong signals match, propose the most-specific layer, meaning the matching contributor-capable layer deepest in the layer graph from the anchor. The confirmation prompt must disclose the runner-up matches and their reasons so the user can choose a different target without re-explaining the input.

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
      - source: "paste-prefix:TEAM-PLATFORM:"
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

## Log format

Capture-routing entries follow the canonical `.kb-log/` shape declared in kb-management SKILL.md rule 6 — `HH:MM:SSZ | operation | scope | target | details`. The `details` field is a comma-separated list of `key=value` pairs so the audit can parse it mechanically. Three operations are reserved:

| Operation | When | Required `details` keys |
|-----------|------|--------------------------|
| `capture-routing-propose` | The agent surfaces a reflection-driven target and waits for confirmation. Written **before** the user response, so an abandoned session leaves the proposal in the log without a paired confirmation | `correlation-id=<ulid-or-uuid>`, `routing-mode=reflection-driven`, `proposed-target=<layer>`, `default-target=<layer>`, `source=<short-ref>`, `reason="<one-line reason>"` |
| `capture-routing-confirm` / `capture-routing-reject` | The user answered the proposal. `confirm` carries the agreed target; `reject` records the fallback (typically `target=<default-layer>`) | `correlation-id=<same-id>`, `target=<layer>` |
| `capture` | The applied mutation. Always written, regardless of routing mode | `correlation-id=<ulid-or-uuid>`, `routing-mode=default \| explicit \| reflection-driven`, `target=<layer>`, `path=<repo-relative path>`, `gate-score=<0-5>`. For `explicit`, also `rule-ref=<file>:<line>` or `rule-ref=invocation` |

Rules for the `correlation-id`:

1. **Default mode** writes one `capture` line; the `correlation-id` is locally unique to that capture so external systems can link follow-ups.
2. **Explicit mode** also writes one `capture` line. The `rule-ref` field identifies which user instruction or `capture-routing:` rule routed the capture (configured rules use `<path>:<line>` or `<path>:<rule-index>`; invocation-named targets use `rule-ref=invocation`).
3. **Reflection-driven mode** writes three lines in order: `capture-routing-propose` → `capture-routing-confirm` (or `capture-routing-reject`) → `capture`. All three share the same `correlation-id`. A `reject` ends the chain at the default layer and writes the `capture` line with `routing-mode=default` and `rule-ref=reflection-rejected`.

Example log slice for a reflection-driven capture:

```text
14:02:11Z | capture-routing-propose | layer | alice-personal | correlation-id=01H8X..., routing-mode=reflection-driven, proposed-target=team-observability, default-target=alice-personal, source=paste:5fc2..., reason="Input names tracing-coverage workstream and the action item is team-owned engineering scope"
14:02:38Z | capture-routing-confirm | layer | team-observability | correlation-id=01H8X..., target=team-observability
14:02:38Z | capture | finding | team-observability | correlation-id=01H8X..., routing-mode=reflection-driven, target=team-observability, path=_kb-references/findings/2026-05-23-tracing-coverage.md, gate-score=4
```

## Audit and concurrency

- `/kb audit` rule **K16** (`capture-routing-unconfirmed`) parses `.kb-log/` for every `capture` entry whose `details` carry `routing-mode=reflection-driven`, then requires a same-`correlation-id` `capture-routing-confirm` entry with an earlier timestamp in the same daily log (or the previous day's log if the chain crosses midnight). A `capture` line missing the confirmation, or matched only by a `capture-routing-reject`, fires the violation. A `capture-routing-propose` without a paired `confirm` and without a paired `capture` is also flagged (orphaned proposal). A `capture` written at `routing-mode=default` after a `reject` is **not** flagged — that is the supported fallback path.
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
| 2026-06-02 | Added required version/changelog metadata so plugin specs and references are covered by the consistency check | Issue #144 |
| 2026-05-24 | Added the reflection-driven inference heuristics subsection defining strong signals, weak signals, concrete examples, and the deepest-layer tie-breaker so agents have an operational rubric for when to propose a non-default capture target. The routing-mode table now points at this rubric instead of relying on vague "clearly implies" wording | Issue #126 |
| 2026-05-23 | Review-feedback follow-up on the initial reference: fixed the broken YAML in the `capture-routing:` example (the `source: paste-prefix: "TEAM-PLATFORM:"` line had two `:` tokens at the same indentation, restructured as a single quoted scalar `source: "paste-prefix:TEAM-PLATFORM:"`); rephrased the "Default mode is the floor" sentence to name the modes explicitly instead of referencing an `(b)` label that did not exist; added the "Log format" subsection declaring the three reserved operations (`capture-routing-propose`, `capture-routing-confirm`/`capture-routing-reject`, `capture`), their required `details` keys, the `correlation-id` rules, and a worked example so audit rule K16 is mechanically checkable. Audit K16 wording tightened accordingly | Copilot review #116 |
| 2026-05-23 | Initial reference. Codifies the three capture-routing modes (default / explicit / reflection-driven), the `capture-routing:` config schema, the mandatory confirmation gate for agent-inferred non-default targets, the "do not write while waiting for confirmation" rule, the audit rule K16, and the relationship to `/kb promote` and `auto-promote`. Closes the spec gap where direct cross-layer capture was implicitly possible (via "context selects another contributor-capable layer") but never named as a deliberate alternative to the private→shared promote chain | Artifact layer routing |
