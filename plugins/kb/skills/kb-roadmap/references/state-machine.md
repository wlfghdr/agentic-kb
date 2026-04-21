# Reference: state machine and resume routing

## Motivation

The skill runs on partial data, mid-workflow, with humans in the loop. It must be able to:

1. Tell what state a scope is in from the file system alone (no sidecar DB).
2. Pick a single next action deterministically when re-invoked.

Both properties come from **inline state markers** + **ordered resume rules**.

## Inline state markers

Every generated artifact carries state at the top of its body, above the summary strip:

```markdown
<!-- status: draft -->
<!-- status: reviewed @ 2026-04-21T12:00:00Z by alice -->
<!-- status: published @ 2026-04-21T14:30:00Z -->
```

Markers are append-only. The current status is the newest marker. Any process (the skill, a grep, a CI check) reads the latest marker to decide what to do next.

When the skill regenerates an artifact, it preserves the existing marker history and adds a new `draft` marker on top. The review command `/kb roadmap --review` is what flips `draft` → `reviewed`; `/kb roadmap publish` (if implemented) flips `reviewed` → `published`.

## Resume routing

When the user invokes `/kb roadmap` without arguments, or with only `--scope`, the skill runs the following ordered routing before any work:

### Step 1 — Conformance check

Produce a pass/fail table for the scope:

| Check | Pass criteria |
|---|---|
| `_kb-roadmaps/<scope>/` exists | directory present |
| Scope configured | `.kb-config/layers.yaml` has `roadmap.scopes.<scope>` |
| All declared trackers reachable | `read-items` dry call returns without error |
| Last artifact fresh | newest file in `<scope>/` within `freshness-days` |
| Review backlog | no orphan `draft` markers older than `draft-stale-days` |

Report the table. If any required check fails, stop and surface it.

### Step 2 — State assessment

Scan the scope directory for the newest roadmap and status artifacts. Read their state markers. Produce a state table:

| Artifact | Latest marker | Age |
|---|---|---|
| `roadmap-2026-04-21.md` | `reviewed @ 2026-04-21T12:00Z` | 4h |
| `status-2026-04-14.md` | `published @ 2026-04-14T09:00Z` | 7d |

### Step 3 — Ordered resume rules

Apply in order. Stop at first match. The action it points to is the **single next step** surfaced to the user.

1. **Scope not configured** → run `/kb setup` tracker block for this scope.
2. **Declared tracker unreachable** → report failure + config path; stop.
3. **No artifact yet OR freshness expired** → generate a new roadmap (`/kb roadmap --scope <name>`).
4. **Artifact exists with `draft` marker** → offer review (`/kb roadmap --review --scope <name>`).
5. **Review older than cadence** → generate a new status short-form (`/kb roadmap status --scope <name>`).
6. **Mismatch finding above threshold unresolved** → offer `/kb roadmap --review-mismatches`.
7. **Tuning digest non-empty** → offer `/kb roadmap tune --scope <name>`.
8. **Everything clean** → report green; suggest `/kb roadmap --scope exec` if the roll-up is stale.

The rules are deterministic, documented, and testable. LLM judgment is not used to decide the next step.

## Why this is not VI-specific

The markers are generic status words (`draft`, `reviewed`, `published`, `archived`) and the rules refer only to artifact freshness, review backlog, and unresolved findings. No domain vocabulary.
