# Glossary

> **Version:** 0.5 | **Last updated:** 2026-04-27

Canonical terms used throughout the spec. If a term has an entry here, use this term and no synonym in spec documents.

| Term | Definition |
|------|-----------|
| **Agent** | A persona that composes one or more skills for autonomous or semi-autonomous operation. Path in this repo: `plugins/<plugin>/agents/<name>.md`. |
| **Adoption stage** | The team's posture toward the agent: **Stage 1** (capture discipline, no `/kb` invocation in the loop), **Stage 2** (agent-assisted triage, evaluation gate fires but humans confirm before persistence), **Stage 3** (bounded autonomous knowledge ops, scheduled rituals plus guarded auto-promote). Set by `kb-setup` phase 1 question 8 and surfaced in phase 3 question 12. Full contract: `plugins/kb/skills/kb-setup/references/adoption-stages.md`. |
| **Anchor layer** | The contributor-capable layer whose `.kb-config/` directory is the source of truth for the workspace graph, automation, and artifact settings. |
| **Capture** | The flow that turns raw input into a finding, note, or skipped material. Command: `/kb [text/URL/path]`. |
| **Capture-only mode** | Synonym for **Adoption stage 1**. The team uses the `agentic-kb` directory contract, evaluation-gate scoring patterns, and audit trail by hand, without invoking the `/kb` agent in the loop. A valid stop, not a half-installed product. |
| **Changelog (inline)** | The `## Changelog` section at the bottom of any long-lived file. Required on topics, foundation files, and other living shared docs. |
| **Brief** | A living delivery-intent artifact under `_kb-delivery/briefs/`. It frames the problem, scope, non-goals, success signals, and handoffs before detailed design starts. |
| **Connection** | A per-layer declaration of linked product repos, trackers, reference mode, and write-back policy under `.kb-config/layers.yaml`. |
| **Contributor-scoped** | An artifact visibility mode used at multi-user contributor layers: the file belongs to one contributor rather than the whole layer. This is not the same thing as contributor-capable, which describes whether the layer role may author shared state. |
| **Decision** | A first-class artifact representing an open or resolved choice. One file per decision. Lifecycle: `gathering-evidence → under-discussion → proposed → decided`, optionally `revisiting`. |
| **Delivery** | An optional feature family that adds `_kb-delivery/briefs/` and `_kb-delivery/specs/` for cross-role handoff artifacts between direction and execution. |
| **Digest** | The flow that pulls changes from a parent layer or from declared `connections` into the current layer as findings, note proposals, or report inputs. Command: `/kb digest <layer>` or `/kb digest connections`. |
| **Draft** | A pre-v1 skill or primitive whose contract is documented but still expected to change. Draft features are opt-in and not scaffolded by default. |
| **Evaluation gate** | The five-question relevance filter applied at every persistence boundary. |
| **External anchor** | A link from the KB to an authoritative external source (dashboard, runbook, tracker export, repo doc). Registered in `sources.md` via an alias. |
| **Finding** | A dated, immutable snapshot capturing what was learned on a specific date. Path: `_kb-references/findings/YYYY/YYYY-MM-DD-slug.md`. |
| **Focus** | The max-6 active tasks in `_kb-tasks/focus.md`. Always loaded into agent context. |
| **Foundation** | The rarely-changing identity files in `_kb-references/foundation/` — who you are, your context, stakeholders, sources, and VMG. |
| **Goal** | A measurable target declared in `_kb-references/foundation/vmg.md`. Lifecycle: `active → achieved \| deferred \| dropped`. Goals steer prioritization after the evaluation gate. Also called **MCG** (Mission-Critical Goal). |
| **Harness** | The IDE or CLI environment where the skills run. Marketplace/native plugin paths today are VS Code Copilot Chat and Claude Code. Installer-supported native command or skill paths include OpenCode, Gemini CLI, and Kiro IDE. Compatible skill workflows, such as Codex CLI, use the same repo-local KB contract through `AGENTS.md` plus `.agents/skills/`. Beyond the supported tiers, two "not yet" buckets are documented in the README: **rules-only harnesses** (e.g. Cursor, Windsurf) reuse the scaffolded files as context but have no slot for a custom `/kb` command, and **not-feasible** environments (e.g. Aider, raw Claude / Inflection Pi) lack any user-custom command hook today. |
| **Idea** | A first-class incubation object for observations with novelty potential. Lifecycle: `seed → growing → ready → shipped \| archived`. Path: `_kb-ideas/I-YYYY-MM-DD-slug.md`. Developed via `/kb develop`. |
| **Incident record** | A dated operations artifact under `_kb-operations/incidents/YYYY/` that captures impact, timeline, mitigations, and follow-up work for a production interruption. |
| **Journey** | A hierarchical user, customer, or product flow (`journey → phase → sub-journey → step`) with readiness per visible step. Managed by the optional draft `kb-journeys` skill. |
| **Layer** | A KB repo participating in the workspace graph. Layers are named and typed by `scope`, not by fixed ladder position. |
| **Marketplace** | A repo that indexes and hosts plugins for one layer's audience. It is cross-cutting and may attach to any layer via `marketplace:` in `.kb-config/layers.yaml`. |
| **Meeting note** | A shared note record under `_kb-notes/YYYY/` with required attendees and authors. Ends in proposed decisions and tasks rather than silently mutating them. |
| **Note** | A lightweight first-class record for meetings or working notes. Path: `_kb-notes/YYYY/MM-DD-slug.md`. |
| **Operations** | An optional feature family that adds `_kb-operations/incidents/YYYY/` and `_kb-operations/releases/YYYY/` for shipping and runtime-response artifacts. |
| **Parent layer** | The next upward layer in the graph. `promote` walks toward it; `digest` walks back down from it. |
| **Plugin** | A bundled skill set suitable for harness installation. Assembled by the plugin generator. |
| **Promote** | The flow that pushes a mature artifact from one contributor-capable layer to another contributor-capable layer higher in the parent chain. Command: `/kb promote [file] [layer]`. |
| **Publish** | The flow that packages KB content as a skill and publishes it to the marketplace attached to a target layer. Command: `/kb publish [file] [layer]`. |
| **RACI** | Responsible / Accountable / Consulted / Informed. Required on shared-layer decisions and tasks. |
| **Role** | The layer's mutation permission boundary. `contributor` layers may originate shared changes there; `consumer` layers may receive digest output and be read, but must refuse `promote` and `publish` as a target. |
| **Release record** | A dated operations artifact under `_kb-operations/releases/YYYY/` that captures scope, rollout, verification, rollback, and communications for a ship event. |
| **Repo-as-OS framework** | A separate, complementary framework that runs an entire enterprise out of a git repository — typically modeling signals, missions, pull requests, and releases as governance objects, with policies as enforceable gates. `agentic-kb` is the knowledge-ops layer that pairs with such frameworks; it does not bundle one and is not derived from any specific instance. See `docs/REFERENCE.md` §10 for the abstract mapping. |
| **Roadmap** | A plan-vs-delivery reconciliation artifact emitted as Markdown, HTML, and JSON by the optional draft `kb-roadmap` skill. |
| **Ritual** | A composed command that strings primitives into a user-facing flow: `start-day`, `end-day`, `start-week`, `end-week`. |
| **Scope** | A descriptive layer type such as `personal`, `team`, `org-unit`, or `company`. It is a routing hint, not a fixed enum or ladder position. |
| **Skill** | A reusable instruction unit in a directory with `SKILL.md` at its root. Path in this repo: `plugins/<plugin>/skills/<name>/SKILL.md`. Portable across first-class supported harnesses and reusable from compatible CLI workflows that honor the same repo-local contract. |
| **Spec** | A living delivery design-contract artifact under `_kb-delivery/specs/`. It records requirements, proposed shape, rollout constraints, verification, and open questions around a body of work. |
| **Task** | An actionable work item tracked in `_kb-tasks/focus.md` or `_kb-tasks/backlog.md`. The canonical term; `todo` and `TODO` are recognized synonyms. |
| **Topic** | A living document representing the current position on a theme. Updated in place. Path: `_kb-references/topics/<slug>.md`. |
| **Tracker** | An external issue or planning system declared in a layer `connections:` block, such as GitHub issues, Jira exports, or Linear exports. |
| **Watermark** | The subtle `v{version} · {date}` marker added to generated HTML artifacts or the timestamp file that marks the last processed external digest window. |
| **VMG** | Vision, Mission & Goals — the strategic steering model. Lives in `_kb-references/foundation/vmg.md`. Vision (years), Mission (quarters), Goals (weeks–quarters). Goals are synonymous with MCGs (Mission-Critical Goals). |
| **Workstream** | A parallel track inside a layer with its own themes, active decisions, and status. Path: `_kb-workstreams/<name>.md`. |

## Non-Terms

The following terms are **not** used in this spec; use the term on the right instead.

| Avoid | Use instead |
|-------|------------|
| contributor-capable artifact | contributor-scoped artifact |
| L1 / L2 / L3 / L4 / L5 | layer / scope / parent layer |
| Database, record, entry | file, topic, finding, decision, or note |
| Library, module | skill |
| TODO, todo (in spec text) | task (but `todo` remains an accepted command alias) |
| OKR | goal / MCG |
| User profile, account | foundation / `me.md` |
| Repository (as abstract concept) | KB layer / repo (concrete Git repo) |
| RFC | spec |
| PRD, project charter | brief |
| postmortem | incident record |
| maturity level (for adoption) | adoption stage |
| AI maturity model, agentic curve | adoption stage |
| pre-agent mode, manual mode | capture-only mode |
| Sync | Use the specific flow you mean: `digest`, `promote`, `publish`, `diff`, or `sync` for contributor-scoped reconciliation |

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-27 | Added soft-transition vocabulary: `adoption stage`, `capture-only mode`, `repo-as-OS framework`. Non-term mappings now steer `maturity level (for adoption)` and `AI maturity model / agentic curve` to `adoption stage`, and `pre-agent mode / manual mode` to `capture-only mode` | Soft-transition extension |
| 2026-04-26 | Added the new delivery and operations vocabulary: `brief`, `spec`, `delivery`, `operations`, `release record`, and `incident record`, plus the canonical non-term mappings for `RFC`, `PRD`, and `postmortem` | Software-engineering operating-model gap closure |
| 2026-04-25 | Added the missing `contributor-scoped` term and tightened the `Role` definition so artifact visibility and layer mutation rights are no longer easy to confuse | Deep spec-audit follow-up |
| 2026-04-25 | Concept-audit follow-up: extended the Harness definition with the rules-only and not-feasible buckets that the README documents, so the glossary stays the single source of truth for harness vocabulary | Concept-audit drift correction |
| 2026-04-25 | Replaced the fixed L1–L5 vocabulary with the 5.0 flexible layer graph terms (layer, scope, role, parent layer, anchor layer), added notes/connections/tracker terminology, and clarified marketplace as a per-layer capability | v5.0.0 flexible layer model |
| 2026-04-24 | Updated the harness definition to distinguish marketplace/native plugin paths, installer-supported native command or skill paths, and Codex's compatible skill workflow | Harness docs correction |
| 2026-04-22 | Added Codex CLI to the harness definition as a compatible CLI workflow and clarified first-class vs repo-local support language | Compatibility expansion |
| 2026-04-22 | Added draft roadmap/journey terminology, updated in-repo skill/agent paths, and clarified the non-generic use of `sync` | Doc drift review |
| 2026-04-18 | Initial version | New |
| 2026-04-18 | Escaped literal `\|` inside the Digest row so markdownlint MD056 passes (no semantic change) | CI fix |
