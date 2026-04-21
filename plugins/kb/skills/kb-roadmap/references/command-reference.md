# Reference: `/kb roadmap` command reference

## Base command

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

Without `--apply`: writes a dry-run plan to `<output-dir>/roadmap-<scope>-<date>.sync.md`. With `--apply`: requires interactive confirmation before mutating plan sources. `--apply` is only valid when the plan-source adapter supports writes; most read-only adapters reject it.

### `--review-tier-4`

```
/kb roadmap --review-tier-4 [--scope NAME]
```

Walks tier-4 proposed matches from the most recent run. For each: shows plan + delivery summaries and the rationale, prompts `confirm | reject | edit`. Confirmed matches persist in `.kb-scripts/roadmap-state.json` and upgrade to tier 1 on subsequent runs.

### `--review-mismatches`

```
/kb roadmap --review-mismatches [--scope NAME] [--class CLASS]
```

Walks section-E entries. For each: shows evidence + proposed action, prompts `accept | suppress | link`. `link` opens an interactive cross-reference editor that writes back to the plan source (if adapter supports writes) or records a manual mapping in `roadmap-state.json`.

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
/kb roadmap ideate --scope NAME [--from <idea-or-decision-path>]
/kb roadmap ideate --scope NAME --prompt "text"
/kb roadmap ideate --scope NAME
```

Creative pass. Turns a KB idea, decision, free-text prompt, or nothing (scans for unlinked seeds) into one or more roadmap item stubs under `_kb-roadmaps/<scope>/items/R-YYYY-MM-DD-slug.md`. Proposes 2–5 variants when space to expand; flags overlaps; names the value. Items open at phase `idea`, status `draft`.

### `discuss`

```
/kb roadmap discuss <item-path-or-id> [--scope NAME] [--write]
```

Devil's advocate. Challenges assumptions, surfaces contradictions with existing items / decisions / foundation, scans for hedging language, steel-mans the opposing view. Write-free by default; `--write` appends a `## Critique` section to the item.

### `review`

```
/kb roadmap review <item-path-or-id> [--scope NAME] [--discuss-only]
```

Challenge-then-create. Runs condensed `discuss` output first, then adds adjacent ideas, risks (severity-classified), and outcome-shaped todos with mitigations. Every entry cites evidence. Appends `## Review` section; transitions `draft` → `reviewed`.

### `refine`

```
/kb roadmap refine <item-path-or-id> [--scope NAME] [--force]
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
