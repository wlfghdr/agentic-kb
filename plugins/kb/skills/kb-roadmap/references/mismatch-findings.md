# Reference: mismatch findings

Mismatch findings are the primary value of the skill on imperfect datasets. Where correlation fails, the artifact surfaces *why* — not silently discard.

## Classes

| Class | Trigger | Risk type |
|---|---|---|
| `delivered-unplanned` | Delivery item unmatched; LoC / file-count above noise threshold | Scope creep, undocumented work |
| `planned-undelivered` | Plan item unmatched; status ≠ closed; older than configurable age | Stale plan, dropped commitment |
| `traceability-gap` | Tier-3 signals just below threshold; probable but unverified relationship | Audit debt |
| `stalled-in-progress` | Plan item in `in-progress` for > `stalled-after-days` with no matching delivery | Execution risk |

## Routing to KB findings

Opt-in via config:

```yaml
mismatch-findings:
  route-to: _kb-references/findings
  route-classes:
    - delivered-unplanned
    - planned-undelivered
  min-loc-threshold: 20
  stalled-after-days: 14
  ignore-paths:
    - "**/*.md"
    - "package-lock.json"
```

When routing is enabled, each mismatch becomes a finding file:

```
_kb-references/findings/YYYY-MM-DD-roadmap-<class>-<slug>.md
```

With body:

```markdown
# Finding: <class> — <title>

**Source**: kb-roadmap · run <timestamp>
**Class**: <class>
**Scope**: <workstream>

## Evidence
- Plan item: <link or id>  (or: none)
- Delivery item: <link or id>  (or: none)

## Why flagged
<one paragraph from the ladder audit trail>

## Proposed action
- [ ] ...
```

Findings are immutable — re-runs do not overwrite. A follow-up `/kb audit` pass deduplicates by evidence fingerprint.

## Noise management

Without filters, `delivered-unplanned` floods with doc-only commits and dependency updates. Defaults ship aggressive:

- Ignore any commit touching only paths in `ignore-paths`
- Ignore commits below `min-loc-threshold` LoC
- Collapse consecutive commits by the same author within 1 hour into a single entry
- Collapse merge commits whose children all matched (the merge itself is redundant)

These filters apply to routing and to section E rendering, not to the JSON sidecar — the sidecar keeps the raw truth.

## Human review loop

The skill exposes two review commands:

- `/kb roadmap --review-tier-4` — walks each proposed tier-4 match; user confirms, rejects, or edits
- `/kb roadmap --review-mismatches` — walks section-E entries; user can suppress a class per-source, or add a cross-reference to upgrade it to tier 2 on the next run

Confirmed matches and suppressions persist in `.kb-scripts/roadmap-state.json` so future runs stay stable.
