# Glossary

> **Version:** 0.1 | **Last updated:** 2026-04-18

Canonical terms used throughout the spec. If a term has an entry here, use this term and no synonym in spec documents.

| Term | Definition |
|------|-----------|
| **Agent** | A persona that composes one or more skills for autonomous or semi-autonomous operation. Path in this repo: `plugins/<plugin>/agents/<name>.md`. |
| **Draft** | A pre-v1 skill or primitive whose contract is documented but still expected to change. Draft features are opt-in and not scaffolded by default. |
| **Capture** | The flow that turns raw input into a finding (or skipped material). Command: `/kb [text/URL/path]`. |
| **Changelog (inline)** | The `## Changelog` section at the bottom of any long-lived file. Required on topics, foundation files, and team output topics. |
| **Decision** | A first-class artifact representing an open or resolved choice. One file per decision. Lifecycle: `gathering-evidence → under-discussion → proposed → decided`, optionally `revisiting`. |
| **Digest** | The flow that pulls changes from a higher layer (team/org) down into the personal KB as a finding. Command: `/kb digest team\|org`. |
| **Evaluation gate** | The five-question relevance filter applied at every persistence boundary. |
| **External anchor** | A link from the KB to an authoritative external source (dashboard, runbook, CMDB). Registered in `sources.md` via an alias. |
| **Finding** | A dated, immutable snapshot capturing what was learned on a specific date. Path: `_kb-references/findings/YYYY-MM-DD-slug.md`. |
| **Focus** | The max-6 active tasks in `_kb-tasks/focus.md`. Always loaded into agent context. |
| **Foundation** | The rarely-changing identity files in `_kb-references/foundation/` — who you are, your context, stakeholders, sources. |
| **Goal** | A measurable target declared in `_kb-references/foundation/vmg.md`. Lifecycle: `active → achieved \| deferred \| dropped`. Goals steer evaluation gate scoring and task prioritization. Also called **MCG** (Mission-Critical Goal). |
| **Harness** | The IDE or CLI environment where the skills run. First-class supported harnesses today are VS Code Copilot, Claude Code, and OpenCode. Compatible CLI workflows, such as Codex CLI, use the same repo-local KB contract without a native marketplace/install target yet. |
| **Idea** | A first-class incubation object for observations with novelty potential. Lifecycle: `seed → growing → ready → shipped \| archived`. Path: `_kb-ideas/I-YYYY-MM-DD-slug.md`. Developed via `/kb develop`. |
| **Journey** | A hierarchical user, customer, or product flow (`journey → phase → sub-journey → step`) with readiness per visible step. Managed by the optional draft `kb-journeys` skill. |
| **L1 / L2 / L3 / L4 / L5** | Personal / Team / Org-Unit / Marketplace / Company-wide layers. |
| **Marketplace** | A repo that indexes and hosts plugins for consumption across harnesses. Layer 4. |
| **Plugin** | A bundled skill set suitable for harness installation. Assembled by the plugin generator. |
| **Promote** | The flow that pushes a mature artifact from a lower layer to a higher one. Command: `/kb promote [file]`. |
| **Publish** | The flow that packages KB content as a marketplace skill and opens a PR. Command: `/kb publish [file]`. |
| **RACI** | Responsible / Accountable / Consulted / Informed. Required on team and org-unit decisions and tasks. |
| **Roadmap** | A plan-vs-delivery reconciliation artifact emitted as Markdown, HTML, and JSON by the optional draft `kb-roadmap` skill. |
| **Ritual** | A composed command that strings primitives into a user-facing flow: `start-day`, `end-day`, `start-week`, `end-week`. |
| **Skill** | A reusable instruction unit in a directory with `SKILL.md` at its root. Path in this repo: `plugins/<plugin>/skills/<name>/SKILL.md`. Portable across first-class supported harnesses and reusable from compatible CLI workflows that honor the same repo-local contract. |
| **Task** | An actionable work item tracked in `_kb-tasks/focus.md` or `_kb-tasks/backlog.md`. The canonical term; "todo" and "TODO" are recognized synonyms. |
| **Topic** | A living document representing the current position on a theme. Updated in place. Path: `_kb-references/topics/<slug>.md`. |
| **Watermark** | The subtle `v{version} · {date}` marker added to generated HTML artifacts' intro slides. |
| **VMG** | Vision, Mission & Goals — the strategic steering model. Lives in `_kb-references/foundation/vmg.md`. Vision (years), Mission (quarters), Goals (weeks–quarters). Goals are synonymous with MCGs (Mission-Critical Goals). |
| **Workstream** | A parallel track inside a personal KB with its own themes, active decisions, and status. Path: `_kb-workstreams/<name>.md`. |

## Non-Terms

The following terms are **not** used in this spec; use the term on the right instead.

| Avoid | Use instead |
|-------|------------|
| Database, record, entry | file, topic, finding, decision (depending on what you mean) |
| Library, module | skill |
| TODO, todo (in spec text) | task (but "todo" is accepted as a command synonym) |
| OKR | goal / MCG (the spec uses "goal" — OKRs, KPIs, and similar frameworks map onto this) |
| User profile, account | foundation, `me.md` |
| Repository (as abstract concept) | KB (layer) / repo (concrete Git repo) |
| Sync | Use the specific flow you mean: `digest`, `promote`, `publish`, or `/kb sync team` for contributor-topic cross-reference. Avoid using bare "sync" as a generic term. |

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-22 | Added Codex CLI to the harness definition as a compatible CLI workflow and clarified first-class vs repo-local support language | Compatibility expansion |
| 2026-04-22 | Added draft roadmap/journey terminology, updated in-repo skill/agent paths, and clarified the non-generic use of "sync" | Doc drift review |
| 2026-04-18 | Initial version | New |
| 2026-04-18 | Escaped literal `\|` inside the Digest row so markdownlint MD056 passes (no semantic change) | CI fix |
