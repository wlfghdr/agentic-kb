# Architecture — The Five Layers

> **Version:** 0.1 | **Last updated:** 2026-04-18

Content flows across five layers. Only L1 is required; all higher layers are optional and declared in a single configuration file in the personal KB.

```
┌─────────────┐   ┌─────────────┐   ┌──────────────┐   ┌──────────────┐   ┌─────────────┐
│  L1 Personal│──►│   L2 Team   │──►│ L3 Org-Unit  │──►│ L4 Marketplace│◄──│ L5 Company  │
│  (required) │   │ (optional)  │   │  (optional)  │   │   (optional)  │   │ (top-down)  │
│             │   │ (multiple)  │   │              │   │               │   │             │
│ inputs/     │   │ <you>/inputs│   │ <team>/inputs│   │ skills/<name> │   │ OKRs, MCG   │
│ references/ │   │ <you>/outputs│  │ <team>/outputs│  │ agents/<name> │   │ strategy    │
│ ideas/      │   │ decisions/  │   │ decisions/   │   │ plugins/<name>│   │ directives  │
│ decisions/  │   │ tasks/      │   │ workstreams/ │   │               │   │             │
│ tasks/      │   │ log/        │   │ tasks/       │   │               │   │             │
│ log/        │   │             │   │ log/         │   │               │   │             │
│ workstreams/│   │             │   │              │   │               │   │             │
└─────────────┘   └─────────────┘   └──────────────┘   └──────────────┘   └─────────────┘

 Contributor unit:   —           person              team              —                —
 Cross-analysis:     workstreams across people       across teams      —                —
```

## L1 — Personal KB (required, one per person)

- **What**: your private evidence base — raw captures, distilled findings, curated positions, ideas in development, task tracking, decisions.
- **Repo**: individual Git repo.
- **Audience**: you + your AI agents.
- **Lifecycle**: Capture → Digest → Formalize → Promote (up) or Archive.
- **Supports multiple parallel workstreams** — the agent auto-routes and cross-links.
- **Declares vision, mission, and goals** — these steer the evaluation gate and task prioritization (see [12-vision-mission-goals.md](12-vision-mission-goals.md)).

## L2 — Team KB (optional, multiple allowed)

- **What**: shared decision-ready workspace — collaborative proposals, cross-references, synthesis.
- **Repo**: shared Git repo with contributor-isolated directories.
- **Audience**: a small team (2–15 people).
- **Lifecycle**: Receive promotions → Review → Cross-reference → Output → Digest back (down).
- **Decisions, tasks, and ideas** live here with RACIs (see [04-decisions.md](04-decisions.md)).

## L3 — Org-Unit KB (optional — capability, solution, or department level)

- **What**: cross-team coordination — shared workstreams, org-level decisions, strategic alignment.
- **Repo**: shared Git repo with team-isolated directories (same pattern as L2, one level up).
- **Audience**: multiple teams within a capability area, solution area, or department.
- **Contributor unit**: teams (not individuals). Each team has its own `<team>/inputs/` and `<team>/outputs/` directory.
- **Lifecycle**: Receive promotions from team KBs → Cross-team analysis (synergies, conflicts, gaps) → Org-level decisions with cross-team RACIs → Roadmap alignment.
- **Cross-analysis**: the agent synthesizes across team directories — surfacing synergies, contradictions, and gaps, just like L2 does across people.
- **Decisions, tasks, and ideas** live here with cross-team RACIs.

## L4 — Skills Marketplace (optional)

- **What**: packaged AI capabilities — skills, agents, plugins that encode institutional knowledge.
- **Repo**: a marketplace repo that implements the structure described in [`docs/spec/marketplace-and-skills.md`](../spec/marketplace-and-skills.md).
- **Audience**: everyone in the organization (or, for OSS marketplaces, the public).
- **Lifecycle**: Mature patterns from L1/L2/L3 → Skill/agent packaging → PR → Review → Published in the marketplace.
- **Only tools available via the marketplace** should be used in published skills. No hidden external dependencies.

## L5 — Company-wide (optional, top-down only)

- **What**: strategy decks, directives, OKRs, company-wide announcements.
- **Repo**: no single repo — consumed from various company sources.
- **Audience**: everyone (top-down).
- **Lifecycle**: Company publishes → Agent pulls relevant signals → Integrates into personal/team/org context.
- **No bottom-up input** — L5 accepts no promotions. Lower layers **reference** L5 material (strategy, MCG, OKRs) when making decisions or shaping positions, but they don't write to it.
- **How to use it**: the agent includes relevant L5 references as context when evaluating captures, drafting decisions, or promoting across layers. L5 grounds the "why" — it doesn't receive the "what".

## External Resources — First-Class Links

Layers can also reference **external assets**: product outcome repos, dashboards, websites, CMDBs, wikis, ticket systems. These are not KB layers themselves — they're linked from the KB via a standard concept described in [10-external-links.md](10-external-links.md). Examples:

- A topic about "service resilience" links to the current SLO dashboard and the service's runbook repo.
- A decision about a migration links to the asset registry entry and the product backlog.

External links are authoritative outside the KB — the KB references them; it doesn't duplicate their content. Full spec: [10-external-links.md](10-external-links.md).

## Configuration

Layer configuration lives in a single file inside the personal KB. This is the only place the mapping is declared — all tooling reads it.

```yaml
# .kb-config.yaml (in personal KB root)
layers:
  personal:
    path: .
    workstreams:
      - name: reliability
        themes: [slo, incident, postmortem]
      - name: platform
        themes: [deploy, pipeline, tooling]

  teams:                         # L2 — zero or more
    - name: platform-team
      path: ../platform-team-kb
      contributor-dir: your-name

  org-unit:                      # L3 — zero or one
    name: reliability-org
    path: ../reliability-org-kb

  marketplace:                   # L4
    enabled: true
    repo: org/agentic-kb-marketplace
    path: ../agentic-kb-marketplace

  company:                       # L5
    enabled: false
    sources: []                  # optional list of URLs / paths to poll
```

## Configuration Rules

- **Single source of truth** — `.kb-config.yaml` in the personal KB is the authoritative layer declaration. Team and org-unit KBs do not declare "who is a member"; membership is implicit from who has cloned the repo and who contributes.
- **Relative paths** — layers are referenced by relative path from the personal KB root. If a user moves their workspace, they update relative paths once in this file.
- **Per-layer opt-in** — disabling a layer is `enabled: false`, not deletion. The agent keeps the block for later re-enablement.

## What Flows Between Layers

| Flow | Direction | Command | Gate |
|------|-----------|---------|------|
| Capture | external → L1 | `/kb [text/URL/path]` | Relevance to declared themes |
| Promote | L1 → L2 | `/kb promote [file]` | Team-relevant, decision-ready |
| Promote org | L2 → L3 | `/kb promote org [file]` | Cross-team relevance |
| Publish | L1/L2/L3 → L4 | `/kb publish [file]` | Generalizable, safe, reusable |
| Digest team | L2 → L1 | `/kb digest team` | Position-changing signal only |
| Digest org | L3 → L1 | `/kb digest org` | Position-changing signal only |
| Install | L4 → harness | `/kb install [skill]` | Marketplace-approved |
| Propagate | L5 → L1 | `/kb [capture]` | Relevance to themes |

Full flow details: [09-flows.md](09-flows.md).

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | L3: added team-isolated directories (mirroring L2 person-directories). L5: clarified as reference-only, no bottom-up input. ASCII diagram updated with contributor-unit / cross-analysis rows. | Spec review |
| 2026-04-18 | Added ideas/ to L1 layout, renamed todo→tasks across layers, added VMG reference to L1, added ideas+tasks to L2/L3 | Spec review — Ideas + VMG + tasks rename |
| 2026-04-18 | Initial version | Extracted from source spec §1 |
