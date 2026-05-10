# Connections — setup and lifecycle

This reference covers how to declare, configure, and maintain external connections for a layer. Connections give `/kb digest connections` its source list, and they appear in triage drift checks and `start-day` briefings.

## What a connection is

A connection is an external source of truth that the layer tracks but does not own. Two kinds exist:

| Kind | What it tracks | Typical examples |
|------|---------------|-----------------|
| `product-repos` | Git repos the layer reads from | Product code repos, shared config repos, governance repos from a repo-as-OS framework, open-source dependencies |
| `trackers` | Issue or planning systems | GitHub Issues, Jira, Linear, exported CSV |

Connections live under a layer's `connections:` block in `.kb-config/layers.yaml`. They are layer-specific: each layer tracks the external sources relevant to its scope.

Repo-as-OS bridge defaults still materialize as `connections.product-repos[]` entries. From `agentic-kb`'s perspective, an external governance repo is still a watched repo connection with optional path filters and ticket-pattern extraction.

## Configuration shape

```yaml
layers:
  - name: alice-personal
    # ...
    connections:
      product-repos:
        - name: backend-api
          path: ../backend-api          # local clone path (optional)
          remote: org/backend-api       # GitHub-style remote ref
          watch:
            - CHANGELOG.md
            - src/api/                  # path prefix filter
          ticket-pattern: 'PROJ-\d+'   # regex to extract issue refs from commits

      trackers:
        - kind: github-issues
          repo: org/backend-api
          scope: is:issue is:open label:roadmap
        - kind: jira-export
          export-path: _kb-inputs/jira-export.csv
          project: PROJ
        - kind: github-projects
          repo: org/backend-api
          project-number: 3

      reference-mode: link            # link | inline | none
      writeback:
        enabled: false
        capabilities: []              # comment | status | label
```

### Field contract

| Field | Purpose |
|-------|---------|
| `product-repos[].name` | Human-readable label used in digest output and log entries |
| `product-repos[].path` | Local path to a checked-out clone; omit to use remote-only mode |
| `product-repos[].remote` | `owner/repo` reference for remote API reads when no local path exists |
| `product-repos[].watch` | File paths or prefixes to track for changes; empty means all commits |
| `product-repos[].ticket-pattern` | Regex to match issue or ticket references in commit messages |
| `trackers[].kind` | Tracker adapter; see Tracker kinds below |
| `trackers[].scope` | Filter expression passed to the adapter (label, query, JQL, etc.) |
| `reference-mode` | `link` cites the source, `inline` embeds a summary, `none` records only the watermark |
| `writeback.enabled` | Whether the skill may post comments, status updates, or labels back to the tracker |
| `writeback.capabilities` | Which write operations are permitted; omit or leave empty when `enabled: false` |

### Tracker kinds

| Kind | Description | Required fields |
|------|-------------|----------------|
| `github-issues` | GitHub Issues via the API | `repo`, optional `scope` query |
| `github-projects` | GitHub Projects v2 | `repo`, `project-number` |
| `jira-export` | Exported Jira CSV or JSON | `export-path`, `project` |
| `linear-export` | Exported Linear CSV | `export-path`, optional `team` |
| `csv` | Generic CSV with configurable column mapping | `export-path`, `column-map` |

For live API trackers (`github-issues`, `github-projects`), the skill reads using the harness's ambient authentication context. For export-backed trackers, the user drops a fresh export into the declared path before running `/kb digest connections`.

## Setup flow

Connections are proposed during `kb-setup` phase 3 after the wizard has already learned the user's feeds in phase 1 and discovered nearby repos in phase 2. The setup skill:

1. derives which product repos and trackers the layer should follow,
2. validates that local paths exist or remotes are reachable,
3. writes the `connections:` block into `.kb-config/layers.yaml`,
4. creates `_kb-references/strategy-digests/YYYY/` if it does not already exist,
5. offers an initial `/kb digest connections` dry-run to set the first watermark.

No connections means the block is written with empty lists and `reference-mode: link`. The block stays in the config so a later setup rerun can add connections without a merge conflict.

## Digest lifecycle

### Initial digest

The first `/kb digest connections` for a newly declared connection:

1. reads the declared source (commit log, API query, or export file),
2. writes a bootstrap digest finding under `_kb-references/strategy-digests/YYYY/YYYY-MM-DD-<name>-initial.md`,
3. records the HEAD commit SHA or export timestamp as the watermark in `_kb-references/strategy-digests/.last-digest` or in a per-source watermark file,
4. logs `digest-connections | <scope> | <name> | initial digest, watermark set`.

### Ongoing digests

Each subsequent `/kb digest connections`:

1. reads the stored watermark for each declared connection,
2. fetches only changes since that watermark (commits, issues opened or closed, project column moves),
3. runs each delta through the evaluation gate against the layer's active workstream themes,
4. writes a delta digest finding when the gate score is 1 or higher under `_kb-references/strategy-digests/YYYY/`,
5. updates the watermark,
6. logs the operation.

When no changes are detected, the skill records a no-delta log entry and advances the watermark. It does not write an empty finding.

### Watermark file format

The skill accepts two watermark layouts:

```text
# Single-file layout (default for simple setups)
_kb-references/strategy-digests/.last-digest
  <source-name>: <watermark>
  <source-name>: <watermark>

# Per-source layout (preferred when there are many connections)
_kb-references/strategy-digests/<source-name>.watermark
  commit: abc123de
  fetched: 2026-04-25T08:15:00Z
```

Both layouts are valid. Writers should prefer per-source files for new setups. Readers must accept both.

## Connection drift in triage

When `/kb` runs without arguments, it compares each declared connection's current HEAD or latest export timestamp against the stored watermark. If any connection is ahead of its watermark, triage surfaces the drift and suggests `/kb digest connections`.

This is a read-only check. It does not fetch or mutate.

## Write-back

Write-back allows the skill to post updates back to a tracker on the user's behalf. It is off by default.

To enable:

```yaml
writeback:
  enabled: true
  capabilities: [comment, status]
```

Write-back actions require explicit user confirmation before any update is posted. The skill never posts silently, even at automation level 3. Every write-back is logged with `digest-connections-writeback` plus the target identifier and action taken.

Supported capabilities:

| Capability | What it does |
|------------|-------------|
| `comment` | Posts a comment to the issue or ticket citing the related KB finding |
| `status` | Transitions an issue status when a linked KB decision is resolved |
| `label` | Applies or removes labels based on KB finding maturity or workstream |

## Disconnect and cleanup

To stop tracking a connection:

1. remove its entry from `connections.product-repos[]` or `connections.trackers[]` in `layers.yaml`,
2. optionally delete the associated watermark file or lines,
3. leave existing digest findings in place; they are historical record.

## Related

- [`../SKILL.md`](../SKILL.md)
- [`command-reference.md`](./command-reference.md)
- [`../../../../../docs/REFERENCE.md`](../../../../../docs/REFERENCE.md) §5 — `layers.yaml` field contract
- [`../../kb-setup/SKILL.md`](../../kb-setup/SKILL.md) — setup interview and proposal flow

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-27 | Added a dedicated reference for connection kinds, config shape, setup flow, digest lifecycle, watermark format, triage drift checks, write-back, and disconnect behavior; aligned repo-as-OS bridge wording to the current `connections.product-repos[]` schema | Documentation gap follow-up |
