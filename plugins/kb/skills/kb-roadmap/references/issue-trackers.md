# Reference: issue trackers as first-class sources

> **Version:** 6.4.0 | **Last updated:** 2026-09-17

## Why this exists

Organizations track plans across heterogeneous systems — GitHub issues, Jira, Linear, a Notion board, a spreadsheet — and correlate delivery in a separate system. The skill treats *every* such system as an **issue tracker** with a common capability surface, not as a one-off "plan source".

Trackers are **bidirectional** when the adopter opts in: the skill can read plans and propose updates derived from delivery reality. Applying a proposal uses the same canonical tracker mutation contract as every other primitive.

The preferred home for tracker declarations is the active layer's `connections.trackers[]` block in `.kb-config/layers.yaml`. The older `roadmap.issue-trackers[]` block remains accepted for read capabilities, adapter-specific read metadata, and per-roadmap overrides; it does not independently authorize writes.

## Generic tracker model

Every roadmap tracker adapter implements a subset of these read capabilities. Declare what the adapter supports; the skill degrades gracefully when a capability is absent.

| Capability | Purpose |
|---|---|
| `read-items` | List items in scope with filters (labels, status, assignees, dates) |
| `read-graph` | Follow cross-references (PR→ticket, ticket→remote-links, epic→children) |
| `read-comments` | Read comments for correlation-graph walking |
Read-only trackers set only `read-*`. Canonical writes are declared on the matching `connections.trackers[].capabilities` entry with `create`, `status`, `comment`, or `link`; `label` is also available to adapters that implement it. The skill never calls an unsupported capability.

## Shipped tracker adapters

| Adapter | Tracker | Read | Write |
|---|---|---|---|
| `ticket-export-markdown` | Any tracker exported as markdown files with YAML frontmatter | items, graph | — |
| `github-issues` | GitHub (via `gh` CLI) | items, graph, comments | comments, status (close/reopen), link, item |
| `jira-rest` | Jira Cloud or Server (via REST + token) | items, graph, comments | comments, status, link |
| `linear-graphql` | Linear (via GraphQL) | items, graph, comments | comments, status |

Adopters add trackers by dropping a Python module under `<adopter-kb>/.kb-scripts/roadmap-adapters/<name>.py` implementing the `Tracker` protocol (see `adapters.md`).

## Per-workstream search parameters

Each scope declares **its own** tracker filter so one tracker instance can serve many workstreams:

```yaml
layers:
  - name: alice-personal
    path: .
    connections:
      trackers:
        - name: primary-tracker
          kind: jira
          export-dir: ../jira-export/PROD
    roadmap:
      scopes:
        workstream-a:
          trackers:
            - tracker: primary-tracker
              search:
                jql: "labels = workstream-a AND status != Done"
                fields: [summary, status, assignee, labels, parent, links]
              hierarchy: [Epic, Story, Task]
        workstream-b:
          trackers:
            - tracker: primary-tracker
              search:
                jql: "component = 'workstream-b' AND updated >= -30d"
```

`search` is a free-form adapter-specific block. Every adapter documents which fields it accepts.

A layer may read and correlate heterogeneous trackers across scopes, but the current `primitive-storage.roadmap-items` contract names one canonical tracker for the whole roadmap-item family in that layer. Therefore only scopes whose canonical items live in that selected tracker are apply-capable. Other configured trackers remain read-only inputs. If scopes require different canonical write destinations, place them in separately owning layers; per-scope tracker ownership is not part of the current schema. Setup and audit must reject a configuration that presents more than one tracker in the same layer as apply-capable for roadmap items.

## Continuous tuning

Search filters drift: labels get renamed, components get split, new ones appear. The skill can propose config updates after each run.

After a run, the engine produces a **tuning digest**:

- `zero-match-filters` — filters that returned nothing (likely stale)
- `low-match-filters` — filters that returned < N items where history showed more
- `unreachable-items` — items the engine correlated to this scope via graph-walk but that the filter missed (candidates to broaden the filter)
- `suspected-noise` — items returned by the filter that correlate to a different scope with higher confidence (candidates to narrow the filter)

Run `/kb roadmap tune [--scope NAME]` to walk the digest interactively. Each proposal shows before/after filter + expected match-count change; user `accept | reject | edit`. Accepted changes are written back to `.kb-config/layers.yaml` with an inline comment recording the date + reason.

Tuning is **opt-in** and never silent. Without `/kb roadmap tune`, the digest is recorded in the JSON sidecar and the MD/HTML artifact's §G "Decisions needed" surfaces the top 3 proposed changes as "config tuning candidates".

## Safety

- The skill never posts a comment, transitions a status, links records, or creates an item unless `primitive-storage.roadmap-items` makes the selected connection tracker canonical and that connection declares the exact operation.
- `/kb roadmap sync --apply` requires available authentication/tooling and interactive confirmation per write. Batch `--apply --yes` is refused for shared workspaces; roadmap configuration cannot weaken the canonical per-action confirmation rule.
- Missing ownership follows the configured canonical home and does not propose a mutation in the noncanonical tracker. Only after tracker ownership succeeds may missing capability or authentication produce a complete manual tracker proposal; after manual completion, the skill waits for and records the resulting identifier without creating a competing roadmap item.
- Every write records an audit line in `.kb-log/YYYY-MM-DD.log` with tracker, item id, operation, and the correlation evidence that triggered it.
- Credentials are read from the canonical `connections.trackers[].auth-env` name or from a documented ambient authentication context. The skill never reads, stores, or emits token values.

### Legacy roadmap capability migration

Pre-6.4 configurations may carry `write-item`, `write-status`, `write-comments`, or `write-link` under `roadmap.issue-trackers[].capabilities`. Setup and audit must build one complete migration proposal rather than only rename those capabilities:

1. Select a same-named canonical connection only when it is a compatible live adapter: its kind matches the legacy live adapter, its non-secret endpoint identity matches, and it has no `export-dir` or `export-path`. A same-named export-backed, custom, or incompatible connection remains read-only and must not receive write capabilities; derive a distinct live connection name instead. A compatible connection with an explicit empty capability list is intentionally read-only: pause for the user to edit it or select another destination rather than adding writes. If more than one live destination is plausible, ask the user to choose instead of persisting.
2. Map `write-item` → `create`, `write-status` → `status`, `write-comments` → `comment`, and `write-link` → `link` onto that canonical connection. Preserve its declared capabilities, or its temporary normalized capabilities when the field is absent, before adding the mapped operations. Preserve an `auth-env` already declared on the selected connection; otherwise copy the legacy environment-variable name—not its value—from either the tracker entry or its documented `config` mapping. For a token-only adapter, pause and ask for that source when neither location supplies one; do not present the migration as complete. Adapters with documented ambient authentication may retain that mode.
3. Remove the migrated `write-*` names from the legacy entry while preserving its `read-*` capabilities, so setup and audit do not propose the same migration again.
4. Create `primitive-storage.roadmap-items` with `mode: tracker`, the selected canonical tracker name, and `kind: Roadmap Item` when no ownership mapping exists. If an existing mapping names another canonical home, surface the conflict and do not overwrite it.

The user confirms this whole config diff before it is persisted. Until migration is accepted, legacy names may describe the proposal but do not satisfy ownership, capability, or authentication gates.

## Migration from "plan-sources" terminology

Earlier schema used `plan-sources:` generically. Trackers are a specialized plan source with bidirectional capability. Both forms are accepted:

- Read-only plan sources (markdown milestones, release logs) stay under `plan-sources:`.
- Tracker inputs now prefer active-layer `connections.trackers[]`; adapter-driven roadmap-specific read overrides may still live under `issue-trackers:` when needed.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-09-17 | Preserved normalized capabilities and canonical authentication during legacy migration, including nested legacy authentication metadata | PR #153 review |
| 2026-09-17 | Made legacy migration pause without token authentication, clean up migrated write names, and refuse automatic upgrades of explicit read-only connections | PR #153 review |
| 2026-09-17 | Limited apply-capable roadmap ownership to one canonical tracker per layer and prevented legacy migration from upgrading same-named export-backed or incompatible connections | PR #153 review |
| 2026-09-16 | Made legacy roadmap migration create or select the canonical connection and `primitive-storage.roadmap-items` ownership mapping in the same confirmed diff | PR #153 review |
| 2026-09-16 | Prevented manual tracker proposals after failed ownership and moved authentication-source authority and migration to the canonical connection | PR #153 review |
| 2026-09-16 | Routed roadmap writes through `primitive-storage.roadmap-items` and canonical connection capabilities; added explicit migration mapping for legacy `write-*` names | Issue #152 review |
| 2026-06-02 | Added required version/changelog metadata so plugin specs and references are covered by the consistency check | Issue #144 |
| 2026-04-25 | Updated the tracker reference to prefer active-layer `connections.trackers[]` and recast `issue-trackers[]` as the legacy/override surface for the 5.1 closeout | v5.1.0 closeout release |

Adopters can mix both in the same scope.
