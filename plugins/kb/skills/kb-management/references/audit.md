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
| K4 | Every decision (`_kb-decisions/D-*.md`) has a `**Status**:` line and — if `resolved` — a resolution date in the evidence trail | `decision-status-missing` | Prompt for status |
| K5 | Every idea (`_kb-ideas/I-*.md`) has a `**Stage**:` line (`seed` / `growing` / `ready` / `shipped` / `archived`) | `idea-stage-missing` | Prompt for stage |
| K6 | No pending inputs older than `freshness.inputs-days` without being triaged | `stale-input` | Offer triage now |
| K7 | Foundation files present: `me.md`, `context.md`, `vmg.md`, `sources.md`, `naming.md` | `foundation-incomplete` | Offer scaffold |
| K8 | Topics last updated more than `freshness.topic-days` days ago that are still cited by recent findings | `stale-cited-topic` | Offer `/kb develop <topic>` |
| K9 | Workstream files have current status blocks (not "TBD" or empty) | `workstream-status-missing` | Offer digest pull |
| K10 | HTML artifacts in `_kb-references/reports/` are not older than their source topics | `stale-html-artifact` | Offer regeneration |
| K11 | Every record with `status: promoted` resolves its `canonical:` target (file exists; relative path resolves; target is not itself another `status: promoted` stub) | `backlink-broken` | Offer to rewrite the relative path (when the canonical target has moved) or to remove the promoted stub if the canonical record was deleted |
| K12 | Every retro (`_kb-notes/YYYY/*.md` with `type: retro`) carries `status: open` / `tracked` / `closed`; `open` retros older than 7 days without a `tracked` move are flagged; `tracked` retros whose linked tasks/decisions are all done/resolved are flagged as eligible for `closed` | `retro-status-stale` | Offer to (a) link each `## What we will change` item to a backlog task or decision and move to `tracked`, or (b) move to `closed` when all linked commitments are discharged |
| K13 | Every entry in `_kb-log/promote-conflicts.md` older than 7 days has a matching dedup or rename mutation in `.kb-log/` (per [`docs/concurrency.md`](../../../../../docs/concurrency.md) case 1) | `promote-conflict-unresolved` | Offer `/kb sync <layer>` so the human picks between dedup (drop the suffixed file) and rename (keep both with distinct slugs) |
| K14 | Every `status: promoted` source file's mtime is not newer than its `promoted-at:` frontmatter date (per [`docs/concurrency.md`](../../../../../docs/concurrency.md) case 2) | `backlink-diverged` | Offer to (a) revert the source edit (canonical wins) or (b) copy the source edit upward to the canonical record and resync the backlink on the next promote |
| K15 | Every topic that has carried more than one `## Position — @<author>` heading for longer than `freshness.topic-days` (default 60) is flagged (per [`docs/concurrency.md`](../../../../../docs/concurrency.md) case 3) | `topic-author-sections-unconverged` | Offer to open a convergence decision (`D-YYYY-MM-DD-<topic-slug>.md`) that cites both author sections and propose the rewrite to a single `## Position` heading |
| K16 | For every `.kb-log/` `capture` line whose `details` carry `routing-mode=reflection-driven`, a matching `capture-routing-confirm` entry with the same `correlation-id` and an earlier timestamp must exist in the same daily log (or the previous day's log if the chain crosses midnight). An orphaned `capture-routing-propose` with no paired `confirm`/`reject`/`capture` is also flagged. See [`capture-routing.md`](./capture-routing.md) "Log format" for the full line shape | `capture-routing-unconfirmed` | Offer to (a) revert the artifact to the default active-layer location, or (b) declare a `capture-routing:` rule in `.kb-config/layers.yaml` so future captures of this shape route explicitly. A `capture` line written at `routing-mode=default` after a `capture-routing-reject` is **not** flagged — that is the supported fallback path |

## Delegated audits

When the listed skills are installed, `/kb audit` delegates their domain-specific rules and consolidates the report:

### Delegated to `kb-roadmap`

If `.kb-config/layers.yaml` has a `roadmap:` block, run `/kb roadmap audit --scope <each>` for every configured scope. Pulls in the 15 rules from [`kb-roadmap/references/audit.md`](../../kb-roadmap/references/audit.md):

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

If `.kb-config/layers.yaml` has a `journeys:` block, run `/kb journeys audit`. Pulls in the 19 rules from [`kb-journeys/references/audit.md`](../../kb-journeys/references/audit.md):

- J1/J2 — metadata and required section integrity
- J3/J4/J5 — step id format, collisions, and rename safety
- J6/J7/J8 — readiness and configured actor coverage
- J9/J10/J11/J12 — mock envelope and standalone mock integrity
- J13/J14 — interface and cross-reference resolution
- J15/J16 — roadmap citation and coverage checks when roadmap links are configured
- J17/J18/J19 — overview drift, ownership metadata, and unused configured actors

### Cross-primitive checks (run by kb-management directly)

| # | Rule | Violation class | Correction offered |
|---|------|----------------|---------------------|
| X1 | Every ADR referenced by an item-escape-hatch exists under `roadmap.audit.adr-glob` | `adr-link-broken` | Offer to update the link or remove the escape-hatch claim |
| X2 | Every decision (`_kb-decisions/D-*`) citing a journey step cites a valid id | `decision-journey-citation-broken` | Offer rename or removal |
| X3 | Every idea (`_kb-ideas/I-*`) that was promoted to a roadmap item retains a back-link in its Development Log (stage moved to `shipped` with a log entry citing the roadmap item id) | `idea-promotion-traceability-gap` | Offer to backfill the link |
| X4 | Every finding under `_kb-references/findings/` with class `journey-*` has a matching open journey-review task until resolved | `journey-finding-unresolved` | Offer to open `/kb journeys review --from-finding` |

## Output

Single triple artifact at `_kb-references/reports/audit-<YYYY-MM-DD>.{md,html,json}`:

1. **Summary chip strip** — total violations per primitive (KB-wide / roadmap / journeys / cross-primitive).
2. **KB-wide violations** — K1-K16 with corrections.
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

Every resolution respects the existing safety gates (tracker writes need `--apply`; config edits get diff previews; decisions route to `_kb-decisions/` with `**Status**: gathering-evidence` per the template default).

## Exit codes

| Code | Meaning |
|---|---|
| 0 | No violations across any primitive |
| 1 | KB-wide violations only |
| 2 | Delegated audits failed (roadmap or journeys reported violations beyond their severity-gate) |
| 3 | Cross-primitive violations |
| 4 | Audit itself failed to run (config error, missing delegated skill) |

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-24 | Linked delegated roadmap and journeys audits to their canonical audit references and replaced the inline journeys checklist with the J1-J19 delegated rule summary from `kb-journeys/references/audit.md` | Issue #125 |
| 2026-05-23 | Tightened K16 wording so it is mechanically checkable: it now cites the required `routing-mode` / `correlation-id` log keys, the propose → confirm → capture line ordering, and the supported-fallback exemption. Aligned with the "Log format" subsection added to [`capture-routing.md`](./capture-routing.md) | Copilot review #116 |
| 2026-05-23 | Added K16 (`capture-routing-unconfirmed` — every reflection-driven capture has a paired confirmation entry in `.kb-log/` before the mutation) for the capture-routing contract in [`capture-routing.md`](./capture-routing.md). Updated the output-shape line to reference K1-K16 | Artifact layer routing |
| 2026-05-22 | Added K13 (`promote-conflict-unresolved`), K14 (`backlink-diverged`), K15 (`topic-author-sections-unconverged`) for the concurrency contract in [`docs/concurrency.md`](../../../../../docs/concurrency.md). Closes audit finding #106 | Audit-tracker closeout |
| 2026-05-22 | Added K11 (`backlink-broken` — every `status: promoted` record's `canonical:` target must resolve) and K12 (`retro-status-stale` — `open` retros older than 7 days without `tracked` move, or `tracked` retros eligible for `closed`). Closes audit findings #111 and #112 | Concept/spec gap audit |
| 2026-05-10 | Added the missing `## Changelog` section so this reference satisfies AGENTS rule 3 (every long-lived spec/concept doc carries an inline changelog). No semantic changes to the audit rules, delegated audits, or exit codes | v6.0.0 adoption + daily-usage gap audit |
