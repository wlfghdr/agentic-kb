# Reference: `/kb audit`

KB-wide consistency audit. Runs the foundational checks directly, then delegates scope-specific audits to installed primitive skills (`kb-roadmap`, `kb-journeys`) and consolidates the results into a single report with offered corrections.

## When to run

- Weekly ritual (auto-offered by `/kb end-week` if no recent audit exists)
- Before a major review or presentation
- After a large batch of captures / imports / external changes
- Whenever the user suspects drift between primitives

## Rules checked (KB-wide)

| # | Rule | Violation class | Correction offered |
|---|------|----------------|---------------------|
| K1 | Every finding and topic has a `**Maturity**:` line (`raw` / `emerging` / `durable`) | `maturity-missing` | Propose classification from content |
| K2 | Every `durable` finding is referenced from at least one topic | `durable-finding-orphan` | Offer to cite it in the closest-matching topic |
| K3 | Every topic's `sources.md` entries resolve to existing files or URLs | `broken-source` | Offer removal or update |
| K4 | Every decision (`_kb-decisions/D-*.md`) has a `status:` and — if resolved — a resolution date | `decision-status-missing` | Prompt for status |
| K5 | Every idea (`_kb-ideas/I-*.md`) has a `status:` marker | `idea-status-missing` | Prompt for status |
| K6 | No pending inputs older than `freshness.inputs-days` without being triaged | `stale-input` | Offer triage now |
| K7 | Foundation files present: `me.md`, `context.md`, `vmg.md`, `sources.md`, `naming.md` | `foundation-incomplete` | Offer scaffold |
| K8 | Topics last updated more than `freshness.topic-days` days ago that are still cited by recent findings | `stale-cited-topic` | Offer `/kb develop <topic>` |
| K9 | Workstream files have current status blocks (not "TBD" or empty) | `workstream-status-missing` | Offer digest pull |
| K10 | HTML artifacts in `_kb-references/reports/` are not older than their source topics | `stale-html-artifact` | Offer regeneration |

## Delegated audits

When the listed skills are installed, `/kb audit` delegates their domain-specific rules and consolidates the report:

### Delegated to `kb-roadmap`

If `.kb-config/layers.yaml` has a `roadmap:` block, run `/kb roadmap audit --scope <each>` for every configured scope. Pulls in the 15 rules from `kb-roadmap/references/audit.md`:

- R1 — every non-infra item cites a journey step
- R2 — every citation resolves
- R3 — every journey step has coverage
- R4 — every status maps to a phase
- R5 — `shipped` items have delivery evidence
- R6 — `in-delivery` items have tier-1-or-2 correlation
- R7/R8/R9 — timeline discrepancies (retroactive-commit, slip-spiral, stalled-in-progress)
- R10 — journey readiness ↔ delivery signals
- R11/R12 — scope membership checks
- R13/R14/R15 — structural integrity

### Delegated to `kb-journeys`

If `.kb-config/layers.yaml` has a `journeys:` block, run `/kb journeys audit` to check:

- Metadata block present and parseable per journey
- Required sections in order
- Step ids match pattern + unique
- Mock envelopes balanced + unique slugs
- Every interface table row references an existing journey
- Cross-reference links resolve
- Readiness coverage (warn)

### Cross-primitive checks (run by kb-management directly)

| # | Rule | Violation class | Correction offered |
|---|------|----------------|---------------------|
| X1 | Every ADR referenced by an item-escape-hatch exists under `roadmap.audit.adr-glob` | `adr-link-broken` | Offer to update the link or remove the escape-hatch claim |
| X2 | Every decision (`_kb-decisions/D-*`) citing a journey step cites a valid id | `decision-journey-citation-broken` | Offer rename or removal |
| X3 | Every idea (`_kb-ideas/I-*`) that was promoted to a roadmap item retains a back-link in its `status: promoted` trail | `idea-promotion-traceability-gap` | Offer to backfill the link |
| X4 | Every finding under `_kb-references/findings/` with class `journey-*` has a matching open journey-review task until resolved | `journey-finding-unresolved` | Offer to open `/kb journeys review --from-finding` |

## Output

Single triple artifact at `_kb-references/reports/audit-<YYYY-MM-DD>.{md,html,json}`:

1. **Summary chip strip** — total violations per primitive (KB-wide / roadmap / journeys / cross-primitive).
2. **KB-wide violations** — K1-K10 with corrections.
3. **Delegated audits** — embedded summaries from `/kb roadmap audit` and `/kb journeys audit`, with links to their full artifacts.
4. **Cross-primitive violations** — X1-X4 with corrections.
5. **Offered next actions** — top 5 corrections across all dimensions, ranked by impact × ease.

## Applying corrections

The KB-wide audit composes over the primitive-skill resolution commands — it does not introduce a new resolution path. Top-5 corrections link directly to:

- `/kb roadmap audit --resolve V-<rule>-<n>` for roadmap violations
- `/kb journeys review <step-id> --from-finding ...` for journey drift
- `/kb develop <topic>` for stale topics
- `/kb decide resolve <id>` for incomplete decisions
- Inline `accept | defer | suppress` for KB-wide violations that don't need further routing

Every resolution respects the existing safety gates (tracker writes need `--apply`; config edits get diff previews; decisions route to `_kb-decisions/` with `status: proposed`).

## Exit codes

| Code | Meaning |
|---|---|
| 0 | No violations across any primitive |
| 1 | KB-wide violations only |
| 2 | Delegated audits failed (roadmap or journeys reported violations beyond their severity-gate) |
| 3 | Cross-primitive violations |
| 4 | Audit itself failed to run (config error, missing delegated skill) |
