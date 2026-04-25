# Reference: active-layer `roadmap:` block in `.kb-config/layers.yaml`

Full schema with defaults.

The active layer may also declare trackers under `connections.trackers[]`. At 5.1, the roadmap pilot normalizes those connection-backed trackers into read-only `issue-trackers[]` entries when the legacy per-skill block is absent.

```yaml
roadmap:
  # Required. Default workstream/scope to render when /kb roadmap is called without --scope.
  default-scope: <string>

  # Default timeframe. Accepts: week | month | quarter | since:YYYY-MM-DD | range:YYYY-MM-DD..YYYY-MM-DD
  default-timeframe: week

  # Where artifacts go. Relative to the KB root. Default: _kb-roadmaps.
  output-dir: _kb-roadmaps

  # How long artifacts stay in output-dir before moving to <output-dir>/archive/.
  retention-days: 180

  # Scopes define views. Each scope is either a detail view (one workstream) or a roll-up (aggregates across workstreams).
  scopes:
    <workstream-name>:
      kind: detail                        # detail | roll-up
      label: <string>                     # optional human-readable title for the hero banner
      description: <string>               # optional subtitle shown on the generated HTML
      timeline:                           # optional; bounds the quarter axis
        start: YYYY-Qn                    # e.g. 2026-Q1 (default: earliest target in items ±1)
        end: YYYY-Qn                      # e.g. 2027-Q2 (default: latest target in items ±1)
      plan-sources: []                    # overrides top-level plan-sources
      delivery-sources: []                # overrides top-level delivery-sources
      correlation: {}                     # overrides top-level correlation
    exec:
      kind: roll-up
      aggregates: []                      # list of detail-scope names
      sections: [X1, X2, X3, X4, X5, X6, X7]
      max-items-per-workstream: 3

  # Plan sources (top-down). One or more. At least one required.
  plan-sources:
    - name: <string>              # required, unique per source
      adapter: <string>           # required; see references/adapters.md
      path: <string>              # required for file-based adapters
      filter:                     # optional, adapter-specific
        labels-any: []
        labels-all: []
        status-exclude: []
      hierarchy: []               # adapter-specific grouping

  # Delivery sources (bottom-up). One or more. At least one required.
  delivery-sources:
    - name: <string>
      adapter: <string>
      path: <string>
      signals: [commits, prs, tags, adrs]
      adr-glob: <string>          # when signals includes "adrs"
      ignore-paths: []

  # Correlation config.
  correlation:
    ticket-key-pattern: "[A-Z]+-\\d+"   # regex; first capture group is the key
    branch-prefixes: []
    trailer-keys: [Jira, Ticket, Issue]
    temporal-window-days: 7
    token-overlap-threshold: 0.35
    deep-investigation: false           # tier 4 is opt-in (LLM cost + review overhead)

  # Mismatch finding config.
  mismatch-findings:
    route-to: _kb-references/findings      # set to empty string to disable routing
    route-classes:
      - delivered-unplanned
      - planned-undelivered
    min-loc-threshold: 20
    stalled-after-days: 14
    ignore-paths:
      - "**/*.md"
      - "**/*.lock"
      - "package-lock.json"

  # Per-workstream overrides. Legacy form — prefer `scopes.<name>` above.
  workstreams:
    <workstream-name>:
      plan-sources: []
      delivery-sources: []
      correlation: {}

  # Legacy per-skill tracker declarations. Prefer active-layer connections.trackers[]
  # for read-only tracker inputs; keep issue-trackers[] for adapter-specific writeback
  # metadata or explicit per-roadmap overrides. See references/issue-trackers.md.
  issue-trackers:
    - name: <string>                       # unique per tracker instance
      adapter: <string>                    # github-issues | jira-rest | linear-graphql | ticket-export-markdown | custom
      capabilities: [read-items]           # subset of: read-items, read-graph, read-comments, write-comments, write-status, write-link, write-item
      config: {}                           # adapter-specific (base-url, project, auth-env, etc.)
      auth-env: <ENV_VAR_NAME>             # env var holding the token; never stored in config

  # Generic phase pipeline. See references/phase-gates.md.
  phases:
    idea:        []                        # native statuses that map to this generic phase
    defined:     []
    committed:   []
    in-delivery: []
    shipped:     []
    archived:    []

  # Gate criteria for phase transitions. Checked in digest mode; never auto-transitions.
  gate-criteria:
    defined:
      required-fields: []
    committed:
      required-fields: []
    in-delivery:
      required: []                         # e.g. [correlation-tier-1-or-2]
    shipped:
      required: []                         # e.g. [delivery-in-main, acceptance-met]

  # Continuous config tuning. See references/issue-trackers.md#continuous-tuning.
  tune:
    enabled: true                          # produce a tuning digest every run
    auto-apply: false                      # never true — tuning changes are always interactive
    low-match-threshold: 3                 # below this many items, flag the filter as low-match
    stale-filter-runs: 3                   # zero-match for N runs in a row flags as stale

  # Resume routing freshness thresholds. See references/state-machine.md.
  freshness:
    roadmap-days: 30
    status-days: 7
    draft-stale-days: 3
```

## Validation rules

- At least one of `plan-sources`, `issue-trackers`, active-layer `connections.trackers`, or scope-level `trackers` must be declared.
- At least one `delivery-sources` entry must be declared.
- Every `issue-trackers[]` entry with any `write-*` capability must declare `auth-env`.
- `correlation.ticket-key-pattern` must compile as a Python regex.
- `output-dir` must be inside the KB root (no `..` traversal).
- `mismatch-findings.route-to` empty string disables routing; any other value must be a relative path under the KB root.
- `phases` keys must match the default pipeline names (`idea`, `defined`, `committed`, `in-delivery`, `shipped`, `archived`) — adopters rename display labels in `.kb-config/artifacts.yaml`, not the canonical keys.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-25 | Clarified the 5.1 config contract: the active layer owns the roadmap block, `connections.trackers[]` can seed read-only tracker inputs, and `issue-trackers[]` is now documented as a legacy or override surface | v5.1.0 closeout release |
