# Reference: issue trackers as first-class sources

## Why this exists

Organizations track plans across heterogeneous systems — GitHub issues, Jira, Linear, a Notion board, a spreadsheet — and correlate delivery in a separate system. The skill treats *every* such system as an **issue tracker** with a common capability surface, not as a one-off "plan source".

Trackers are **bidirectional** when the adopter opts in: the skill can read plans, propose updates derived from delivery reality, and (with confirmation) write back comments or status transitions.

## Generic tracker model

Every tracker adapter implements a subset of these capabilities. Declare what the adapter supports; the skill degrades gracefully when a capability is absent.

| Capability | Purpose |
|---|---|
| `read-items` | List items in scope with filters (labels, status, assignees, dates) |
| `read-graph` | Follow cross-references (PR→ticket, ticket→remote-links, epic→children) |
| `read-comments` | Read comments for correlation-graph walking |
| `write-comments` | Post a comment (e.g. "linked to PR #123 by kb-roadmap") |
| `write-status` | Transition an item's status |
| `write-link` | Add a cross-reference between two items |
| `write-item` | Create a new item (used by `sync` when `delivered-unplanned` should become a ticket) |

Read-only trackers set only `read-*`. The skill never calls an unsupported capability.

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
roadmap:
  issue-trackers:
    - name: primary-tracker
      adapter: jira-rest
      capabilities: [read-items, read-graph, read-comments, write-comments, write-status, write-link]
      config:
        base-url: "https://example.atlassian.net"
        project: PROD
        auth-env: JIRA_API_TOKEN

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

- The skill never posts a comment, transitions a status, or creates an item without an explicit `--apply` on `/kb roadmap sync`.
- `--apply` requires interactive confirmation per write. Batch `--apply --yes` is refused on trackers that touch shared workspaces; requires a per-tracker `allow-batch-writes: true` in config.
- Every write records an audit line in `.kb-log/YYYY-MM-DD.log` with tracker, item id, operation, and the correlation evidence that triggered it.
- Credentials are read from environment variables named in `auth-env`. The skill never reads, stores, or emits token values.

## Migration from "plan-sources" terminology

Earlier schema used `plan-sources:` generically. Trackers are a specialized plan source with bidirectional capability. Both forms are accepted:

- Read-only plan sources (markdown milestones, release logs) stay under `plan-sources:`.
- Bidirectional, adapter-driven trackers live under `issue-trackers:`.

Adopters can mix both in the same scope.
