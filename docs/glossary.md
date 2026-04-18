# Glossary

> **Version:** 0.1 | **Last updated:** 2026-04-18

Canonical terms used throughout the spec. If a term has an entry here, use this term and no synonym in spec documents.

| Term | Definition |
|------|-----------|
| **Agent** | A persona that composes one or more skills for autonomous or semi-autonomous operation. Path: `agents/<name>.md`. |
| **Capture** | The flow that turns raw input into a finding (or skipped material). Command: `/kb [text/URL/path]`. |
| **Changelog (inline)** | The `## Changelog` section at the bottom of any long-lived file. Required on topics, foundation files, and team output topics. |
| **Decision** | A first-class artifact representing an open or resolved choice. One file per decision. Lifecycle: `gathering-evidence → under-discussion → proposed → decided`, optionally `revisiting`. |
| **Digest** | The flow that pulls changes from a higher layer (team/org) down into the personal KB as a finding. Command: `/kb digest team\|org`. |
| **Evaluation gate** | The five-question relevance filter applied at every persistence boundary. |
| **External anchor** | A link from the KB to an authoritative external source (dashboard, runbook, CMDB). Registered in `sources.md` via an alias. |
| **Finding** | A dated, immutable snapshot capturing what was learned on a specific date. Path: `references/findings/YYYY-MM-DD-slug.md`. |
| **Focus** | The max-3 active tasks in `tasks/focus.md`. Always loaded into agent context. |
| **Foundation** | The rarely-changing identity files in `references/foundation/` — who you are, your context, stakeholders, sources. |
| **Goal** | A measurable target declared in `.kb-config.yaml` under `vmg.goals`. Lifecycle: `active → achieved \| deferred \| dropped`. Goals steer evaluation gate scoring and task prioritization. Also called **MCG** (Mission-Critical Goal). |
| **Harness** | The IDE or CLI environment where the skills run (VS Code Copilot, Claude Code, OpenCode). |
| **Idea** | A first-class incubation object for observations with novelty potential. Lifecycle: `seed → growing → ready → shipped \| archived`. Path: `ideas/I-YYYY-MM-DD-slug.md`. Developed via `/kb develop`. |
| **L1 / L2 / L3 / L4 / L5** | Personal / Team / Org-Unit / Marketplace / Company-wide layers. |
| **Marketplace** | A repo that indexes and hosts plugins for consumption across harnesses. Layer 4. |
| **Plugin** | A bundled skill set suitable for harness installation. Assembled by the plugin generator. |
| **Promote** | The flow that pushes a mature artifact from a lower layer to a higher one. Command: `/kb promote [file]`. |
| **Publish** | The flow that packages KB content as a marketplace skill and opens a PR. Command: `/kb publish [file]`. |
| **RACI** | Responsible / Accountable / Consulted / Informed. Required on team and org-unit decisions and tasks. |
| **Ritual** | A composed command that strings primitives into a user-facing flow: `start-day`, `end-day`, `start-week`, `end-week`. |
| **Skill** | A reusable instruction unit in a directory with `SKILL.md` at its root. Portable across VS Code, Claude Code, OpenCode. |
| **Task** | An actionable work item tracked in `tasks/focus.md` or `tasks/backlog.md`. The canonical term; "todo" and "TODO" are recognized synonyms. |
| **Topic** | A living document representing the current position on a theme. Updated in place. Path: `references/topics/<slug>.md`. |
| **Watermark** | The subtle `v{version} · {date}` marker added to generated HTML artifacts' intro slides. |
| **VMG** | Vision, Mission & Goals — the strategic steering model declared per layer. Vision (years), Mission (quarters), Goals (weeks–quarters). Goals are synonymous with MCGs (Mission-Critical Goals). See `12-vision-mission-goals.md`. |
| **Workstream** | A parallel track inside a personal KB with its own themes, active decisions, and status. Path: `workstreams/<name>.md`. |

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
| Sync | digest (L2/L3 → L1), promote (L1 → L2/L3), publish (→ L4) — there is no generic "sync" |

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | New |
| 2026-04-18 | Escaped literal `\|` inside the Digest row so markdownlint MD056 passes (no semantic change) | CI fix |
