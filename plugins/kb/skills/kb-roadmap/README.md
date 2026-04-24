# kb-roadmap

A draft skill in the `agentic-kb` marketplace that reconciles planning-truth sources against delivery reality.

**Status**: draft (`v0.1.0`). Not scaffolded by default. Opt in by declaring `roadmap:` in your `.kb-config/layers.yaml`.

## What it does

Every organization has at least two sources of "planning truth" — tickets, milestones, OKRs — and at least one source of delivery signal — a repository, an ADR set, a release log. They drift. `/kb roadmap` closes the loop:

1. Ingests plan + delivery sources via pluggable adapters
2. Runs a five-tier correlation ladder (direct key → cross-reference → heuristic → LLM-assisted → mismatch)
3. Classifies every unmatched item (delivered-unplanned, planned-undelivered, traceability-gap, stalled)
4. Emits a roadmap artifact in three formats: Markdown (human), HTML (presentation, themed), JSON (machine)

## Lean first proof path

Start with exported tracker markdown before live APIs:

1. export a small GitHub or Jira slice to markdown,
2. bind those directories with `adapter: ticket-export-markdown`,
3. run the roadmap pilot or `/kb roadmap digest`,
4. inspect the JSON sidecar and HTML output,
5. only then add live tracker adapters or write-back.

That keeps the first adoption proof deterministic, token-free, and easy to run in CI.

## Vendor-neutral by construction

This skill ships zero vendor-specific names, colors, or adapters beyond the generic minimum. Adopters supply:

- Source adapter bindings via `.kb-config/layers.yaml` `roadmap.plan-sources[]` / `delivery-sources[]`
- Brand tokens + logo via `.kb-config/artifacts.yaml` `html-template.tokens` / `html-template.logo`
- Workstream vocabulary via `.kb-config/layers.yaml` `layers.personal.workstreams[]`

## See

- [SKILL.md](SKILL.md) — full contract
- [references/correlation-ladder.md](references/correlation-ladder.md) — the five tiers
- [references/adapters.md](references/adapters.md) — adapter contract + shipped set
- [references/mismatch-findings.md](references/mismatch-findings.md) — classification + routing
- [references/config-schema.md](references/config-schema.md) — `.kb-config/layers.yaml` `roadmap:` block
- [references/artifact-contract.md](references/artifact-contract.md) — MD/HTML/JSON contract
- [references/command-reference.md](references/command-reference.md) — subcommands + exit codes
