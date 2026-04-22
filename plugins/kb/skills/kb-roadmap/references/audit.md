# Reference: `/kb roadmap audit`

Full-sweep consistency audit for the roadmap scope. Runs every rule defined across the skill and reports each violation with a proposed correction. Every violation is actionable — the user can accept, reject, or defer.

## When to run

- Weekly ritual (auto-offered by `/kb roadmap` when no recent audit exists)
- Before generating a new roadmap artifact
- After a large batch of tracker changes
- Before a leadership review

## Audit scope

Covers four dimensions:

1. **Mappings** — issues ↔ roadmap items ↔ journey steps
2. **Timeline discrepancies** — plan dates vs. delivery dates vs. readiness transitions
3. **Scope mismatches** — items flagged for this scope vs. items actually aligning with its journeys
4. **Structural integrity** — citation format, id stability, envelope balance, config validity

## Rules checked

| # | Rule | Violation finding class | Correction offered |
|---|------|------------------------|---------------------|
| R1 | Every non-infrastructural, non-foundational roadmap item cites ≥ 1 journey step | `journey-uncovered-item` | Propose citation (from tier-4 deep-investigation) or mark as `infra`/`foundational` |
| R2 | Every cited journey step id resolves to the journey source | `journey-citation-broken` | Offer rename (if id was changed) or drop (if step was removed) |
| R3 | Every journey step has ≥ 1 roadmap item or is explicitly marked `future-work` in the journey | `journey-uncovered-step` | Offer new tracker item creation (dry-run) |
| R4 | Every issue in configured trackers has a phase mapping | `unmapped-status` | Offer to add the unseen status to `.kb-config/layers.yaml` `roadmap.phases:` |
| R5 | Every roadmap item that is `shipped` has delivery evidence (commit/PR/tag in delivery sources) | `shipped-without-delivery` | Offer to downgrade phase or link delivery signal |
| R6 | Every roadmap item that is `in-delivery` has tier-1-or-2 correlation | `missing-correlation` | Offer branch-name or trailer suggestion for next PR |
| R7 | Timeline: plan `committed-date` ≤ delivery `first-commit-date` (no retroactive planning) | `retroactive-commit` | Flag for leadership review; suggest decision entry |
| R8 | Timeline: plan `target-date` not silently slipping (same item re-targeted ≥ 3 times) | `slip-spiral` | Offer decision entry documenting the slip + root cause |
| R9 | Timeline: item status `in-progress` for > `freshness.stale-after-days` | `stalled-in-progress` | Offer escalation comment on the tracker item |
| R10 | Journey step readiness `green` ↔ delivery signals ≥ gate-criteria (no readiness-without-delivery) | `journey-reality-mismatch` | Offer `/kb journeys review <step>` transition |
| R11 | Scope membership: every item tagged into this scope matches the scope's tracker filter (no manual drift) | `scope-tag-mismatch` | Offer untag from this scope or update the tracker filter |
| R12 | Scope membership: every item in the scope's journey-refs is reachable through at least one item (no orphan journey tier) | `journey-tier-orphan` | Offer creation of a parent-epic tracker item to cover the tier |
| R13 | Structural: citation notation parseable by `journey-grounding.citation-pattern` | `citation-format-error` | Offer to rewrite the citation in the canonical format |
| R14 | Structural: no duplicate ids across plan sources (same key seen in two plan trackers with conflicting metadata) | `duplicate-plan-id` | Offer merge proposal |
| R15 | Config: every tracker named in a scope's `trackers[]` exists in `issue-trackers[]` | `config-tracker-missing` | Offer to add the tracker definition |

## Infrastructure / foundational escape hatch (R1 only)

Not every roadmap item maps to a journey step. Infrastructure, build, security-hardening, test harness, and foundational work often exist **to enable** journeys without directly advancing one. R1 is satisfied when the item carries any of these labels / trailers:

- Tracker label matching `roadmap.audit.infra-labels` (default: `infra`, `foundational`, `platform`, `tech-debt`, `security`, `compliance`, `build`, `ci`, `test-harness`)
- Item body contains a trailer line `Classification: infrastructural` or `Classification: foundational`
- Item is explicitly linked to an ADR (the ADR replaces the journey citation)

R1 reports `journey-uncovered-item` only when **none** of these escape hatches apply. Items classified as infra are listed separately in the audit report as *"justified infra work"* so the user can still sanity-check the classification.

## Config

```yaml
roadmap:
  audit:
    infra-labels: [infra, foundational, platform, tech-debt, security, compliance, build, ci, test-harness]
    infra-trailer-pattern: "^Classification:\\s*(infrastructural|foundational)\\s*$"
    adr-glob: docs/architecture/adr-*.md
    # Timeline rule tuning
    slip-threshold: 3                     # R8 — how many re-targets trigger slip-spiral
    retroactive-grace-days: 2             # R7 — plan committed-date may be up to N days after first-commit
    # Output
    max-violations-per-class: 50
    severity-gate: warn                   # warn | error — exit code on violations
```

## Output

The audit emits the triple artifact (MD + HTML + JSON) into `_kb-roadmaps/<scope>/audit-<YYYY-MM-DD>.{md,html,json}`.

Structure:

1. **Summary chip strip** — one chip per rule, colored by violation count (green 0, amber 1-N, red > threshold).
2. **Per-rule violation list** — each violation with:
   - Violation id (`V-<rule>-<n>`)
   - Affected item(s) / step(s) / config key(s)
   - Evidence (quoted excerpt)
   - Proposed correction (actionable, 1-line)
   - Accept / Reject / Defer action (resolved via follow-up subcommand)
3. **Justified infra work** — R1 escape-hatch items, with the justification shown.
4. **Dependency graph preview** — scope → trackers → items → journey steps, highlighting gaps.
5. **Next-step menu** — the top 3 corrections offered to apply immediately.

## Applying corrections

Each violation can be addressed via:

```
/kb roadmap audit --resolve V-R3-7 --action create-item
/kb roadmap audit --resolve V-R5-3 --action downgrade-phase
/kb roadmap audit --resolve V-R1-12 --action classify-infra
/kb roadmap audit --resolve V-R10-1 --action open-journey-review
/kb roadmap audit --resolve V-R4-2 --action add-status-mapping
```

All resolution actions follow the existing safety gates:

- Tracker writes require `--apply` + interactive confirmation.
- Journey reviews transition into `/kb journeys review --from-finding <file>`.
- Config edits produce a diff preview before writing.
- Decision entries route to `_kb-decisions/D-<date>-<slug>.md` with `**Status**: gathering-evidence` per the decision template default.

## Resume routing integration

When `/kb roadmap` runs the state machine and finds a recent audit artifact with unresolved violations, it surfaces the top 3 violations (by severity × scope weight) as the next action. This replaces the default resume rule when audit violations exist.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | No violations (or all within warn threshold) |
| 1 | Config error (skill cannot run) |
| 2 | Violations exceed severity-gate |
| 3 | User deferred one or more resolutions without completing |
