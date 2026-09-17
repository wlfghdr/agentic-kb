# Reference: `/kb roadmap` command reference

> **Version:** 7.0.0 | **Last updated:** 2026-09-17

## Base command

The behavioral spec below describes the intended `/kb roadmap` surface. The shipped helper script in this repo currently implements config-driven generation for detail/roll-up scopes plus `--dry-run`; interactive mutation flows remain draft-spec behavior.

```
/kb roadmap [--scope NAME] [--since DATE | --week | --month | --quarter | --range A..B]
            [--plan-source NAME] [--delivery-source NAME]
            [--output-dir PATH] [--dry-run]
```

Generates all three artifacts (MD + HTML + JSON) using defaults from `.kb-config/layers.yaml` `roadmap:` block, with CLI flags overriding.

## Subcommands

### `digest`

```
/kb roadmap digest [--scope NAME] [--since DATE]
```

Runs plan + delivery ingestion + correlation, prints a summary to stdout, does not write artifacts. Useful for quick status checks and CI.

### `sync`

```
/kb roadmap sync [--scope NAME] [--apply]
```

Proposes plan-source updates derived from delivery reality:

- Tickets that appear closed (matching merged PRs) → propose status transition
- Tier-2 cross-references that only exist one-way → propose adding the reverse link
- `delivered-unplanned` items above threshold → propose opening a ticket
- Latest unconsumed authoring-history markers such as `[propose] phase: defined`, when a current read-only gate evaluation passes → propose the named phase transition

Before `sync` reads a tracker-backed item's body or ordered comments to discover an authoring marker, it shows the structured external-read preflight from [`html-artifacts.md`](../../kb-management/references/html-artifacts.md): canonical tracker and linked sources, scope/item filters and time window, dry-run or apply-capable execution mode, and the sync-plan output path. Explicit invocation authorizes the read but does not suppress this disclosure.

For authoring markers, `sync` identifies the canonical item from the marker's own history, reruns the same read-only criteria as `--check-gates`, and includes that evidence in the plan. It treats a proposal as consumed when the canonical phase is the proposed phase or any later phase in the configured pipeline, so an append-only marker can never propose a regression; no separate consumption write is required. Without `--apply`: writes a dry-run plan to `<output-dir>/roadmap-<scope>-<date>.sync.md`. With `--apply`: requires interactive confirmation before each plan-source mutation. A tracker-backed phase transition additionally requires canonical `primitive-storage.roadmap-items` ownership plus `status` capability and authentication on the selected connection. `--apply` is only valid when the canonical plan-source adapter supports the proposed operation; read-only adapters reject it.

### `--review-tier-4`

```
/kb roadmap --review-tier-4 [--scope NAME]
```

Walks tier-4 proposed matches from the most recent run. For each: shows plan + delivery summaries and the rationale, prompts `confirm | reject | edit`. Confirmed matches persist in `.kb-scripts/roadmap-state.json` and upgrade to tier 1 on subsequent runs.

### `--review-mismatches`

```
/kb roadmap --review-mismatches [--scope NAME] [--class CLASS] [--apply]
```

Walks section-E entries. For each: shows evidence + proposed action, prompts `accept | suppress | link`. Without `--apply`, `link` previews the cross-reference. With `--apply`, it may write only to the tracker selected by `primitive-storage.roadmap-items`, and only after the canonical connection passes the `link` capability, authentication/tooling, and per-write confirmation gates. A mismatch whose plan source is a different read input never receives a tracker mutation; `link` records a manual mapping in `roadmap-state.json` instead.

### `tune`

```
/kb roadmap tune [--scope NAME]
```

Walks the **tuning digest** from the last run (zero-match filters, low-match filters, unreachable items, suspected noise). For each proposal: shows before/after filter + expected match-count change; user `accept | reject | edit`. Accepted changes are written back to `.kb-config/layers.yaml` with an inline comment recording date + reason. See `references/issue-trackers.md`.

### `--discuss`

```
/kb roadmap [--scope NAME] --discuss
```

Or any `/kb roadmap` prompt containing `/discuss` as a token. Write-free mode: no artifact regeneration, no tuning application, no tracker writes, no implicit decisions. The skill explains state, previews proposed changes as block-quoted `> PROPOSED` text, and asks before executing. Lasts for the current turn only. See `references/discuss-mode.md`.

### Phase gate checks

```
/kb roadmap --check-gates [--scope NAME]
```

Reads the configured `roadmap.gate-criteria` and reports, per plan item in scope, which required fields for the item's current phase are missing. Never transitions phases. Violations appear under section G in the next generated artifact.

### `audit`

```
/kb roadmap audit [--scope NAME] [--rule R<n>] [--severity warn|error]
/kb roadmap audit --resolve V-<rule>-<n> --action <accept-action>
```

Full-sweep consistency audit. Runs 15 rules across four dimensions (mappings, timeline discrepancies, scope mismatches, structural integrity). Emits the triple artifact `audit-<YYYY-MM-DD>.{md,html,json}` to `<output-dir>/<scope>/`. Every violation carries an actionable proposed correction. `--resolve` accepts a specific correction and applies it with the usual safety gates. See `references/audit.md`.

The infra/foundational escape hatch (R1) prevents non-journey-aligned work from being falsely flagged: items labeled `infra`, `foundational`, `platform`, `tech-debt`, `security`, `compliance`, `build`, `ci`, `test-harness` — or carrying a `Classification:` trailer, or linked to an ADR — satisfy R1 without citing a journey step.

## Item authoring subcommands

Four dedicated commands for creating and shaping roadmap items. Full contract in `references/authoring-commands.md`.

### `ideate`

```
/kb roadmap ideate --scope NAME [--from <idea-or-decision-path>] [--apply]
/kb roadmap ideate --scope NAME --prompt "text" [--apply]
/kb roadmap ideate --scope NAME [--apply]
```

Creative pass. Turns a KB idea, decision, free-text prompt, or nothing (scans for unlinked seeds) into one or more roadmap items. File-backed and pre-promotion hybrid items use `_kb-roadmaps/<scope>/items/R-YYYY-MM-DD-slug.md`; tracker-backed items are proposed unless `--apply` and the mutation gates succeed. Proposes 2–5 variants when space to expand; flags overlaps; names the value. Items open at phase `idea`, status `draft`.

### `discuss`

```
/kb roadmap discuss <item-path-or-id> [--scope NAME] [--write] [--apply]
```

Devil's advocate. Challenges assumptions, surfaces contradictions with existing items / decisions / foundation, scans for hedging language, steel-mans the opposing view. Write-free by default; `--write` appends a `## Critique` section to a file-backed item, while `--apply` is required to post it to a tracker-backed item.

### `review`

```
/kb roadmap review <item-path-or-id> [--scope NAME] [--discuss-only] [--apply]
```

Challenge-then-create. Runs condensed `discuss` output first, then adds adjacent ideas, risks (severity-classified), and outcome-shaped todos with mitigations. Every entry cites evidence. Appends `## Review` section; transitions `draft` → `reviewed`.

### `refine`

```
/kb roadmap refine <item-path-or-id> [--scope NAME] [--force] [--apply]
```

Actionable pass. Decomposes reviewed outcomes into sized tasks with dependencies, writes testable acceptance criteria, lists interface contracts, marks blocking open questions. Refuses to run on `draft` items without `--force`. Proposes a `defined` gate transition when criteria are satisfied.

See `references/authoring-commands.md` for stance rules, output shapes, and tracker integration.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Artifacts written, no errors |
| 1 | Configuration error (invalid `.kb-config/layers.yaml`) |
| 2 | Source ingestion failed (unreachable path, missing adapter) |
| 3 | Ran successfully but found new high-severity mismatches (for CI gates) |
| 4 | User aborted during interactive prompt |

Exit code 3 is a hook for CI / scheduled runs: fail the job when new unplanned-delivery above threshold appears.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-09-17 | Made phase proposals consumed at the proposed or any later configured phase, preventing stale markers from proposing regressions | PR #153 review |
| 2026-09-17 | Required the structured external-read preflight before `sync` loads tracker-backed authoring history | PR #153 review |
| 2026-09-17 | Defined how `sync` discovers, verifies, and applies proposed authoring phase markers | PR #153 review |
| 2026-09-17 | Added `--apply` and canonical ownership/capability gates to mismatch-link writes while retaining manual mappings for noncanonical sources | PR #153 review |
| 2026-09-17 | Added `--apply` to each tracker-capable item-authoring command shape | PR #153 review |
| 2026-09-16 | Version aligned to 7.0.0; no semantic change | Version alignment |
| 2026-06-02 | Added required version/changelog metadata so plugin specs and references are covered by the consistency check | Issue #144 |
| 2026-05-08 | Clarified which `/kb roadmap` behaviors are covered by the shipped helper script versus the broader draft command spec | Integration pass |
