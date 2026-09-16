# Connections — setup and lifecycle

> **Version:** 6.4.0 | **Last updated:** 2026-09-16

This reference covers how to declare, configure, and maintain external connections for a layer. Connections give `/kb digest connections` its source list, and they appear in triage drift checks and `start-day` briefings.

## What a connection is

A connection is an external source of truth that the layer tracks but does not own. Two kinds exist:

| Kind | What it tracks | Typical examples |
|------|---------------|-----------------|
| `product-repos` | Git repos the layer reads from | Product code repos, shared config repos, governance repos from a repo-as-OS framework, open-source dependencies |
| `trackers` | Issue or planning systems | GitHub Issues, Jira, Linear, exported CSV |

Connections live under a layer's `connections:` block in `.kb-config/layers.yaml`. They are layer-specific: each layer tracks the external sources relevant to its scope. When a tracker is also the canonical operational home for a primitive family, the layer declares that ownership separately in `primitive-storage`; the connection only describes how to reach the tracker.

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
        - name: backend-work
          kind: github-issues
          repo: org/backend-api
          scope: is:issue is:open label:roadmap
          capabilities: [create, status, label, comment, link]
          # auth-env: TRACKER_TOKEN  # optional; omit when ambient auth is documented
        - kind: jira-export
          export-path: _kb-inputs/jira-export.csv
          project: PROJ
        - name: backend-project
          kind: github-projects
          repo: org/backend-api
          project-number: 3
          issue-tracker: backend-work
          capabilities: [create, status, label, comment, link]

      reference-mode: link            # link | inline | none
      writeback:
        enabled: false
        capabilities: []              # comment | status | label

    primitive-storage:
      decisions:
        mode: tracker
        tracker: backend-work
        kind: Decision
        summary-dir: _kb-decisions
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
| `trackers[].capabilities` | Canonical primitive operations implemented by this configured adapter: `create`, `status`, `label`, `comment`, and/or `link` |
| `trackers[].auth-env` | Optional environment-variable name containing adapter credentials; the config stores the name, never the credential. Omit only for adapters with documented ambient authentication |
| `trackers[].issue-tracker` | For `github-projects`, the name of a same-layer `github-issues` connection used for issue CRUD while the project connection stays canonical |
| `writeback.enabled` | Reserved switch for connection-digest-derived mutations; it does not authorize canonical primitive operations |
| `writeback.capabilities` | Reserved connection-digest operations; omit or leave empty while digest write-back is unsupported |
| `primitive-storage.*.tracker` | Name of the tracker connection that owns the primitive family when the mode is `tracker` or `hybrid` |

### Tracker kinds

| Kind | Description | Required fields |
|------|-------------|----------------|
| `github-issues` | GitHub Issues via the API; canonical CRUD is supported when the corresponding capability is declared and authentication is available | `repo`, optional `scope` query |
| `github-projects` | GitHub Projects v2 composite adapter; project status uses the project connection, while `create`, `label`, `comment`, and `link` delegate to its paired issue connection | `repo`, `project-number`; `issue-tracker` when issue operations are declared |
| `jira-rest` | Live Jira REST adapter; canonical operations require the corresponding capability and token-based authentication | `base-url`, `project`, `auth-env` |
| `linear-graphql` | Live Linear GraphQL adapter; canonical operations require the corresponding capability and token-based authentication | `team`, `auth-env` |
| `jira-export` | Exported Jira CSV or JSON; read-only | `export-path`, `project` |
| `linear-export` | Exported Linear CSV; read-only | `export-path`, optional `team` |
| `csv` | Generic CSV with configurable column mapping; read-only | `export-path`, `column-map` |

Live API trackers name credentials with `auth-env`; `github-issues` and `github-projects` may instead use their documented ambient authenticated CLI context. For export-backed trackers, the user drops a fresh export into the declared path before running `/kb digest connections`.

When `primitive-storage` selects a `github-projects` connection, that project connection remains the single canonical tracker. Its `issue-tracker` reference is adapter wiring, not a second ownership claim: the referenced same-layer connection must be `kind: github-issues`, target the same repository, and provide the issue endpoint used by declared issue operations. The project connection's capability list is authoritative for the composite adapter, and authentication/tooling must be available for the delegated endpoint before a mutation can proceed.

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

## Two mutation capabilities

Canonical tracker CRUD and connection-digest write-back are different capabilities.

### Canonical tracker CRUD (supported)

When `primitive-storage` makes a live tracker canonical, the skill may create the canonical item and maintain its status, labels, comments, and links. Each operation is supported only when all of these gates pass, in this order:

1. `primitive-storage` names this tracker as the canonical home for the primitive family.
2. The selected `connections.trackers[]` entry declares the operation in `capabilities` and the adapter implements it.
3. Authentication and a suitable tracker tool/API are available for the target.
4. The agent shows the exact target and mutation, and the user explicitly confirms that one mutation.

`primitive-storage` selects ownership; it grants no permission. A capability declaration states what the adapter can execute; it grants no user authorization. Confirmation authorizes one executable proposal; it cannot add a missing capability or authentication. `connections.writeback.enabled` has no bearing on canonical CRUD.

If `primitive-storage` does not select the tracker, follow the configured canonical home and do not propose a tracker mutation. Once the tracker is canonical, missing capability or authentication returns a proposed issue body or update plus exact manual UI/CLI/API steps. Missing confirmation leaves the executable mutation proposed and unapplied. After a manual operation, the user supplies the resulting tracker identifier; record only the configured summary/backlink and log the handoff. Never create a canonical KB task or decision as a fallback when `primitive-storage` says the tracker is canonical.

### Connection-digest write-back (RESERVED)

The `connections.writeback` block is reserved specifically for mutations derived from `/kb digest connections`, such as posting a KB finding back to a source ticket. Connection digests are read-only in this release. Setting `writeback.enabled: true`, even with `writeback.capabilities`, is a no-op; `/kb status` must warn that the value is ignored. Setup must render `enabled: false` and an empty capability list.

### Planned contract (for future implementation)

Digest write-back would allow the skill to post digest-derived updates back to a tracker on the user's behalf. It would be off by default.

To enable (planned syntax):

```yaml
writeback:
  enabled: true
  capabilities: [comment, status]
```

Write-back actions would require explicit user confirmation before any update is posted. The skill would never post silently, even at automation level 3. Every write-back would be logged with `digest-connections-writeback` plus the target identifier and action taken.

Planned capabilities:

| Capability | What it would do |
|------------|------------------|
| `comment` | Post a comment to the issue or ticket citing the related KB finding |
| `status` | Transition an issue status when a linked KB decision is resolved |
| `label` | Apply or remove labels based on KB finding maturity or workstream |

Open questions before digest write-back can ship: adapter coverage, source-of-truth behavior when a digest and tracker disagree, and merge semantics for concurrent digest write-backs. These do not block confirmation-gated CRUD on the tracker record that `primitive-storage` already made canonical.

## Disconnect and cleanup

To stop tracking a connection:

1. remove its entry from `connections.product-repos[]` or `connections.trackers[]` in `layers.yaml`,
2. optionally delete the associated watermark file or lines,
3. leave existing digest findings in place; they are historical record.

## Related

- [`../SKILL.md`](../SKILL.md)
- [`command-reference.md`](./command-reference.md)
- [`tracker-backed-primitives.md`](./tracker-backed-primitives.md)
- [`../../../../../docs/REFERENCE.md`](../../../../../docs/REFERENCE.md) §5 — `layers.yaml` field contract
- [`../../kb-setup/SKILL.md`](../../kb-setup/SKILL.md) — setup interview and proposal flow

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-09-16 | Defined `github-projects` as a composite canonical connection with an explicit same-layer `issue-tracker` reference for issue CRUD | PR #153 review |
| 2026-09-16 | Added `trackers[].auth-env` to the canonical connection field contract while retaining documented ambient authentication as an explicit alternative | PR #153 review |
| 2026-09-16 | Separated supported canonical tracker CRUD from reserved connection-digest write-back; defined capability, authentication, and per-mutation confirmation precedence plus the manual-proposal fallback | Issue #152 |
| 2026-06-02 | Added required version/changelog metadata so plugin specs and references are covered by the consistency check | Issue #144 |
| 2026-05-18 | Relabeled the Write-back section as RESERVED (not implemented in v6.1.0): `writeback.enabled: true` is a no-op today; the planned contract is preserved as the future spec; open questions (which trackers, auth model, source-of-truth rule, concurrent-write semantics) are now explicit. `kb-setup` must not propose `writeback.enabled: true` in v6.1.0. Closes audit finding #102 | Concept/onboarding/process audit |
| 2026-05-17 | Clarified that tracker connections and tracker-backed primitive ownership are separate config concerns: `connections.trackers[]` describes access, while `primitive-storage` declares canonical ownership | Tracker-backed onboarding design |
| 2026-04-27 | Added a dedicated reference for connection kinds, config shape, setup flow, digest lifecycle, watermark format, triage drift checks, write-back, and disconnect behavior; aligned repo-as-OS bridge wording to the current `connections.product-repos[]` schema | Documentation gap follow-up |
