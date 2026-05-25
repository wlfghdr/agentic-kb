# Reference: `/kb journeys audit`

Full-sweep consistency audit for the journeys primitive. Runs every structural, traceability, readiness, and mock-integrity rule defined by `kb-journeys` and reports each violation with a proposed correction. Every violation is actionable: the user can accept, reject, or defer the offered correction through the follow-up command or authoring flow.

## When to run

- Weekly product-direction ritual when journeys are enabled
- Before generating journey HTML or standalone mock artifacts
- After a large batch of journey edits, roadmap changes, or imported feedback
- Before a roadmap audit that depends on journey-step citations
- Before a review where journey readiness is used as evidence

## Audit scope

Covers five dimensions:

1. **Structure** - journey metadata, required section order, overview shape, and configured directories
2. **Ids** - stable step ids, duplicate detection, configured actors, and rename safety
3. **Readiness** - per-step readiness chips and configured readiness taxonomy
4. **Mocks** - mock envelopes, extracted standalone pages, and orphan generated mocks
5. **Traceability** - journey interfaces, cross-reference links, roadmap citations, and ownership metadata

## Rules checked

| # | Rule | Violation finding class | Correction offered |
|---|------|-------------------------|--------------------|
| J1 | Every journey source file has a parseable metadata block directly under the H1 | `journey-metadata-missing` | Offer to insert the metadata block from `templates/journey.md.hbs` |
| J2 | Required sections appear in contract order: `Entry Conditions`, `Exit Conditions`, `Interfaces`, `Flow` | `journey-section-order` | Offer a section-reorder patch preserving existing content |
| J3 | Every visible step heading has a step id matching `J<tier>.<phase>[-.<sub>]-S<n>` | `journey-step-id-invalid` | Offer a canonical id derived from the journey tier, phase, and step ordinal |
| J4 | Step ids are unique across all journey sources in the configured `source-dir` | `journey-step-id-collision` | Offer `/kb journeys rename-id <old-id> <new-id>` for the non-canonical duplicate |
| J5 | Step ids already cited by roadmap items, decisions, ideas, findings, or other journeys are not changed outside `rename-id` | `journey-step-id-drift` | Offer to revert the id or run `rename-id` so every citation is rewritten |
| J6 | Every visible step has a readiness chip using a configured `journeys.readiness-levels[].chip-class` | `journey-readiness-missing` | Offer to add `partial` readiness with a draft rationale, or fail when `audit.readiness-required: true` |
| J7 | Readiness chip label and class agree with the configured readiness taxonomy | `journey-readiness-invalid` | Offer to rewrite the chip class or label to a configured value |
| J8 | Every step actor token is present in `journeys.actors` when an actors list is configured | `journey-actor-unconfigured` | Offer to add the actor to config or rewrite the step to an existing actor |
| J9 | Every mock envelope has balanced begin/end markers with the same slug | `journey-mock-envelope-unbalanced` | Offer to add the missing marker or remove the incomplete envelope |
| J10 | Every mock slug is unique within its journey file and matches `[a-z0-9][a-z0-9-]*` | `journey-mock-slug-invalid` | Offer a normalized unique slug and update `data-mock` to match |
| J11 | Every mock envelope contains the configured `mock-envelope.container-selector` with matching `data-mock` | `journey-mock-container-missing` | Offer to wrap the mock body in the configured container |
| J12 | Generated standalone mock pages match the current mock envelopes; removed source envelopes leave no orphan page beyond `audit.orphan-mocks` policy | `journey-mock-orphan` | Offer `/kb journeys extract-mocks` or deletion of the orphan generated page |
| J13 | Every `Interfaces` table row references an existing journey slug or sub-journey slug | `journey-interface-broken` | Offer to update the slug to the closest existing journey or remove the stale interface row |
| J14 | Every markdown cross-reference link in journey sources resolves to a file, heading, URL, or known KB artifact | `journey-crossref-broken` | Offer to rewrite the relative link or remove the stale citation |
| J15 | When `journeys.roadmap-link.scope` or roadmap `journey-refs` is configured, every roadmap citation to a journey step resolves and every cited step belongs to the configured source | `journey-roadmap-citation-broken` | Offer a citation rewrite, a `rename-id` run, or a roadmap review finding if the cited step was removed |
| J16 | When `journeys.roadmap-link.scope` is configured, every non-future visible step has roadmap coverage or an explicit `future-work` marker | `journey-roadmap-coverage-gap` | Offer a dry-run tracker item proposal or mark the step `future-work` |
| J17 | `overview.md`, when present, lists only existing journeys and entry points | `journey-overview-drift` | Offer to regenerate the overview scaffold from discovered journey sources |
| J18 | `journeys.ownership.layer`, when present, matches the layer that owns the active `journeys:` block | `journey-ownership-mismatch` | Offer a config diff that updates `ownership.layer` or moves the journeys block to the owning layer |
| J19 | Every configured actor in `journeys.actors` is used by at least one step, unless marked reserved in config comments or adopter notes | `journey-configured-actor-unused` | Offer to remove the unused actor or mark it reserved for a planned journey |

## Severity and policy knobs

Default severity:

- **Error** - J1-J5, J9-J11, J13-J15, J18
- **Warning** - J6-J8, J12, J16, J17, J19

Config may tighten or relax only the documented warning policies:

```yaml
journeys:
  audit:
    readiness-required: false             # false = warn on J6; true = error
    interface-resolution: strict          # strict | lenient; lenient downgrades J13 external/unknown slugs to warning
    orphan-mocks: warn                    # warn | error | ignore for J12
    max-violations-per-class: 50
    severity-gate: warn                   # warn | error; exit code 2 when exceeded
```

Structural integrity, id integrity, mock envelope integrity, and ownership mismatches are not suppressible through config. They define whether the primitive can be trusted by roadmap and KB-wide audits.

## Output

The audit emits the triple artifact (MD + HTML + JSON) into `_kb-journeys/audit-<YYYY-MM-DD>.{md,html,json}` unless `journeys.output-dir` changes the root.

Structure:

1. **Summary chip strip** - one chip per rule, colored by violation count (green 0, amber 1-N, red above threshold).
2. **Per-rule violation list** - each violation with:
   - Violation id (`V-<rule>-<n>`)
   - Affected journey, step id, mock slug, config key, or linked artifact
   - Evidence (quoted excerpt or file path)
   - Proposed correction (actionable, 1 line)
   - Accept / Reject / Defer action (resolved via follow-up subcommand)
3. **Traceability preview** - journeys -> steps -> roadmap citations -> linked KB artifacts, highlighting gaps.
4. **Mock extraction preview** - envelope count, standalone count, orphan count, and stale generated pages.
5. **Next-step menu** - the top 3 corrections offered to apply immediately.

The JSON artifact MUST include the same violation ids, rule ids, finding classes, severity, affected paths, and proposed correction strings as the markdown report so `/kb audit` can embed the delegated summary without reparsing prose.

## Applying corrections

Each violation can be addressed via:

```text
/kb journeys audit --resolve V-J2-1 --action reorder-sections
/kb journeys audit --resolve V-J4-2 --action rename-id --apply
/kb journeys audit --resolve V-J9-1 --action repair-envelope
/kb journeys audit --resolve V-J12-3 --action extract-mocks
/kb journeys audit --resolve V-J16-4 --action propose-roadmap-item
```

All resolution actions follow the existing safety gates:

- Source markdown edits show a diff preview before writing.
- `rename-id` requires `--apply` and rewrites every citation across journeys, roadmap items, decisions, ideas, and findings.
- Tracker writes are dry-run by default and require `--apply` plus interactive confirmation.
- Config edits produce a diff preview before writing.
- Journey text refinements that change behavior or readiness route through `/kb journeys review` or `/kb journeys refine` rather than silently patching meaning during audit.

## Resume routing integration

When `/kb journeys` runs the state machine and finds a recent audit artifact with unresolved violations, it surfaces the top 3 violations by severity and traceability impact as the next action. This replaces the default resume rule when audit violations exist.

## KB-wide audit integration

`/kb audit` delegates here when `.kb-config/layers.yaml` has a `journeys:` block. The delegated summary embedded in the KB-wide audit report MUST link to the full `_kb-journeys/audit-<YYYY-MM-DD>.{md,html,json}` artifacts and preserve the `J` rule ids so findings can be traced back to this reference.

Roadmap-specific checks that compare plan items to journey readiness remain owned by [`kb-roadmap/references/audit.md`](../../kb-roadmap/references/audit.md). This audit owns the journey source's structural integrity and the journey side of cross-primitive citations.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | No violations, or only warnings below `severity-gate` |
| 1 | Config error or unreadable journey source |
| 2 | Violations exceed `severity-gate` |
| 3 | User deferred one or more resolutions without completing |

## Changelog

| Date | What changed | Source |
|------|--------------|--------|
| 2026-05-24 | Added the canonical J1-J19 journeys audit rule set, output contract, resolution actions, and KB-wide delegation contract so `/kb journeys audit` has a version-pinnable reference | Issue #125 |
