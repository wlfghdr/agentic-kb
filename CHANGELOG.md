# Changelog

All notable changes to the **agentic-kb** specification are documented here.

This file follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) convention.
The spec uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html): `MAJOR.MINOR.PATCH`.

## Versioning Conventions

| Bump | When to use |
|------|-------------|
| **PATCH** | Prose edits, typos, clarifications that don't change meaning or structure |
| **MINOR** | New sections, new spec rules, new commands — non-breaking additions |
| **MAJOR** | Breaking changes to the directory layout, command surface, or file formats that invalidate existing implementations |

**Versioning**: the root-level `VERSION` file and this `CHANGELOG.md` track the aggregate framework version. The behavioral spec lives in `plugins/kb/skills/*/SKILL.md` and `plugins/kb/agents/*.md`; the structural reference is `docs/REFERENCE.md`.

---

## [Unreleased]

### Fixed

- **Onboarding flow consistency review** — closed five long-standing gaps that prevented the documented "answer the wizard, get the promised artifacts" contract from working end-to-end:
  1. `docs/first-run-acceptance.md` was a release behind. Phase 2 is now numbered Q9/Q10/Q11 (was Q8/Q9/Q10), and the missing Q8 (operating context / adoption stage, added in v5.4.0) is back in the baseline answer set with `human-only / capture discipline today; agent-assisted triage in 6 months` mapping to Stage 1. Phase 3 expected output now requires the adoption-stage label, the Stage↔automation-level consistency check, and the graduation-criteria block, so the team-lead acceptance baseline actually exercises the soft-transition flow it advertises.
  2. `plugins/kb/skills/kb-setup/SKILL.md` placeholder mapping was incomplete and used stale Q-numbers in two rows. The mapping now documents the global Q-numbering convention and lists every placeholder the templates emit (`{{THEMES}}`, `{{WORKSTREAMS}}`, `{{TEAM_NAME}}`, `{{ORG_UNIT_NAME}}`, `{{REPO_INDEX}}`, `{{ALIAS_INDEX}}`, `{{KEYWORD_LOOKUP}}`, `{{VMG_VISION}}`, `{{VMG_MISSION}}`, `{{VMG_GOALS}}`, `{{AUTOMATION_LEVEL}}`), so the post-write placeholder scan no longer hits undocumented tokens. Skill version bumped to 5.5.1.
  3. `plugins/kb/skills/kb-setup/templates/foundation-me.md` and `plugins/kb/skills/kb-setup/templates/automation.yaml` now carry the `{{ADOPTION_STAGE}}` slot the SKILL.md placeholder mapping promised since v5.4.0. The chosen stage is now durable in the scaffold instead of implicit.
  4. `plugins/kb/skills/kb-setup/templates/automation.yaml` no longer ships `level: 1` together with active schedules. The schedules block is commented out by default (the wizard uncomments and fills it only at level ≥ 2), and the file gained an `adoption-stage` field plus the level-mapping comment block, matching the contract in `references/automation-levels.md`. The `level` field is now a `{{AUTOMATION_LEVEL}}` placeholder so the wizard can write the chosen level cleanly.
  5. `plugins/kb/skills/kb-management/references/html-artifacts.md` and `plugins/kb/skills/kb-setup/templates/presentation-template.html` no longer point at "kb-setup Q13" for the presentation-template copy step — they now reference the phase-3 HTML-styling step, which survives any future renumbering.
- **`docs/examples/first-hour.md` walkthrough refreshed (v5.0.0 → v5.5.1)** — replaced the legacy "Block | Suggested first-run answer" table that contradicted the v5.2.0 "Never ask the user to enumerate layers, features, contributor-mode flags, or scopes in phase 1" rule with the goal-oriented four-phase interview, including the Q8 operating-context answer and the phase-3 confirmation block. Success checks now also assert that the chosen adoption stage is durable in `automation.yaml` and `foundation/me.md`.

- Post-5.5.1 follow-ups only.

## [5.5.1] — 2026-04-30

> **Why PATCH:** documentation and landing-page positioning fix. The v5.5.0 release made roadmap and journey work first-class in the setup/docs surface, but the public HTML landing page still led with the older generic knowledge-ops value proposition and did not show roadmaps/journeys in the first-class primitive grid. No command surface, file format, or layer-graph behavior changes.

### Changed

- **HTML value proposition now matches v5.5** — `index.html` now names product direction, roadmaps, journeys, delivery, and operations in the hero, problem framing, agentic-curve positioning, first-class building blocks, command summaries, and product-management draft-skill cards.
- **Per-file versions and manifests rolled to 5.5.1** — `VERSION`, root `plugin.json`, `.claude-plugin/marketplace.json`, regenerated `plugins/kb/plugin.json`, `README.md`, and `AGENTS.md` now reflect the patch release.

## [5.5.0] — 2026-04-30

> **Why MINOR:** this release makes roadmap and journey work a first-class product-management surface in setup and command routing. The layer graph and existing file formats remain compatible, but setup can now propose roadmap/journey ownership from role, goals, sources, and desired outputs instead of leaving the draft skills as discoverability-only opt-ins.

### Added

- **Setup-proposed product-management primitives** — `kb-setup` now treats customer journeys, phase/lane roadmaps, launch planning, stakeholder roadmap communication, and product sequencing as signals to propose `roadmaps` and `journeys` on a concrete owning layer. The proposal names source inputs, output folders, and whether roadmap/journey ownership is co-located.
- **Roadmap and journey feature placement contract** — `docs/REFERENCE.md`, `docs/operating-model.md`, `docs/glossary.md`, the setup flow, setup templates, and first-run acceptance now document that placement is an onboarding decision. The first setup path keeps one confirmed owning layer by default; layered roll-ups and journey inheritance are documented as future enhancement work.
- **Value-first roadmap presentation rules** — `kb-roadmap` now documents the generic phase/lane presentation contract: aggregate dense source data into lanes/phases, limit visible items per lane/phase, use customer/user value headlines with detail on the second line, preserve source traceability in JSON/appendix, make draft/proposed/agreed/shipped status visible, and reserve checkmarks for implemented or already-true work.

### Changed

- **Command and trigger surface expanded** — `kb-management` and the packaged `kb.prompt.md` now route natural-language roadmap/journey phrases such as product roadmap, phase roadmap, now/next/later, roadmap presentation, user journey, customer journey, journey map, and user flow through the `/kb roadmap` and `/kb journeys` draft skills. Missing config now points users to `/kb setup` as the normal ownership-placement path.
- **Draft skills rolled forward** — `kb-roadmap` and `kb-journeys` moved to `v0.2.0` to reflect setup-proposed activation, explicit ownership metadata, and product-management wording while remaining draft and non-breaking.
- **Manifests and public narrative rolled to 5.5.0** — root `VERSION`, marketplace manifests, README, reference docs, setup/management skills, and `kb-operator` all now describe the setup-proposed roadmap/journey surface.

## [5.4.2] — 2026-04-29

> **Why PATCH:** documentation and routing fix. The opt-in draft skills (`kb-roadmap`, `kb-journeys`) had been shipping with the marketplace install since 5.x, were named in `README.md`, `docs/REFERENCE.md`, the glossary, and both `plugin.json` files, but were not reachable through the `/kb` dispatcher and never advertised on the visual landing page. Adopters who installed via the marketplace could not find them. This release closes that gap. No file format, layer-graph, or core command-surface change.

### Added

- **Dispatcher routes for the draft subcommands** — both `plugins/kb/commands/kb.md` and `plugins/kb/skills/kb-setup/templates/kb.prompt.md` now include an explicit "Draft-skill subcommand" routing rule that hands `/kb roadmap` (alias `roadmaps`) and `/kb journeys` (alias `journey`) off to the matching skill. If the active layer has no `roadmap:` / `journeys:` config block in `.kb-config/layers.yaml`, the dispatcher refuses with a message that names the missing block and points at the skill's `references/config-schema.md`.
- **Trigger keywords on `kb-management`** — the `triggers:` list now includes `roadmap`, `roadmaps`, `journey`, and `journeys` so harnesses that fire skills on natural-language feature keywords (per the v5.2.0 expansion) also wake the right routing path for these flows. A new "Roadmap (draft)" / "Journeys (draft)" pair of rows in the flow-primitive table makes the handoff visible in the behavioral surface.
- **Draft-skill subcommands section in the kb-management command reference** — `plugins/kb/skills/kb-management/references/command-reference.md` now names the two draft skills, the activating config block on each side, and the refusal contract when the block is missing.
- **Optional draft skills section on the visual landing page** — `index.html` now carries a dedicated "Optional draft skills (opt-in)" section with one card per draft skill (status, what it does, the per-layer config block that wakes it up) so marketplace adopters can find them from the public landing page. The single-command list also picks up the two draft subcommands as a follow-on bullet pair.

### Changed

- **Per-file versions and public manifests rolled to 5.4.2** — `VERSION`, `plugin.json`, `.claude-plugin/marketplace.json`, the regenerated `plugins/kb/plugin.json`, `README.md`, `docs/REFERENCE.md`, `plugins/kb/skills/kb-management/SKILL.md`, `plugins/kb/skills/kb-setup/SKILL.md`, and `plugins/kb/agents/kb-operator.md`. `AGENTS.md` rolled to v0.6.

## [5.4.1] — 2026-04-27

> **Why PATCH:** this release is a documentation and consistency fix after v5.4.0. No command surface, file format, or layer-graph behavior changes. It tightens the spec where current `main` had already gained valid clarifications, makes the repo-as-OS bridge wording match the actual `layers.yaml` schema, and publishes the deeper `/kb digest connections`, `/kb publish`, and VMG setup/update contracts that were still missing from the reference surface.

### Added

- **Dedicated connection lifecycle reference** — `plugins/kb/skills/kb-management/references/connections-lifecycle.md` now documents `connections:` config shape, watermark formats, digest lifecycle, triage drift checks, write-back, and disconnect behavior at the same depth as the existing promote contract.
- **Dedicated publish contract reference** — `plugins/kb/skills/kb-management/references/publish-contract.md` now documents the `/kb publish` transformation boundary, generalizability gate, safety validation, package layout under `plugins/<plugin>/skills/<name>/`, and response expectations.
- **Explicit VMG sourcing and update guidance** — `plugins/kb/skills/kb-setup/references/setup-flow.md` now explains how `foundation/vmg.md` is initially populated (URL fetch, file read, direct text), how parent-layer digest updates should be handled, and how VMG conflicts should surface as explicit decisions.

### Changed

- **Repo-as-OS bridge wording now matches the live schema** — references to the non-existent `connections.work-repos[]` bridge field were corrected to `connections.product-repos[]` in `docs/REFERENCE.md`, `plugins/kb/skills/kb-setup/SKILL.md`, and `plugins/kb/skills/kb-setup/references/adoption-stages.md` so the narrative matches the actual `layers.yaml` contract and templates.
- **Command/reference cross-links are now complete** — `kb-management` and `command-reference.md` now point directly to the new connection lifecycle and publish contract references instead of keeping those rules implicit.
- **Per-file versions and public manifests rolled to 5.4.1** — `VERSION`, `plugin.json`, `.claude-plugin/marketplace.json`, the regenerated `plugins/kb/plugin.json`, `README.md`, `docs/REFERENCE.md`, `plugins/kb/skills/kb-management/SKILL.md`, `plugins/kb/skills/kb-setup/SKILL.md`, and `plugins/kb/agents/kb-operator.md`.

## [5.4.0] — 2026-04-27

> **Why MINOR:** this release adds the soft-transition adoption-stage layer on top of the v5.3.0 operating-model coverage. The directory contract, command surface, file formats, automation levels, and knowledge artifacts stay unchanged. What changes is how `agentic-kb` positions itself in the human → agentic enterprise journey, and how `kb-setup` tailors the proposed scaffold to where the team actually is today instead of dropping the same Stage-3 scaffold on every adopter.

### Added

- **Adoption-stage layer** — a three-stage ladder (Stage 1 capture discipline → Stage 2 agent-assisted triage → Stage 3 bounded autonomous knowledge ops) is now the canonical way `agentic-kb` describes where a team meets it on the agentic curve. The ladder is named in the value prop (README + `index.html`), in `docs/REFERENCE.md` §9, in the glossary, and in a new normative reference at `plugins/kb/skills/kb-setup/references/adoption-stages.md`. Each stage names what it scaffolds, why it stops where it stops, and what the team must demonstrate before graduating to the next one.
- **Relationship to repo-as-OS frameworks** — `docs/REFERENCE.md` §10 documents the abstract mapping between `agentic-kb` knowledge-ops primitives (foundation, briefs, specs, decisions, findings, topics, reports) and the work-flow primitives (signals, missions, pull requests, releases, policies) that surrounding **repo-as-OS frameworks** typically own. Out-of-scope items (PR approval enforcement, packaging/releasing, on-call routing, compliance posture, multi-agent orchestration of execution) are now named explicitly. Mapping is intentionally vendor-neutral.
- **`kb-setup` operating-context question** — phase 1 question 8 asks the user where they are on the agentic curve today and (optionally) where they want to be in 6 months. Three buckets: human-only / capture discipline, repo-as-OS framework already in use, or already running AI agents in daily work. The answer biases the proposed scaffold so a Stage-1 team does not get a Stage-3 setup and a Stage-3 team does not get a Stage-1 setup. Subsequent question numbers renumbered (Q9–Q16).
- **`kb-setup` repo-as-OS detection** — phase 2 discovery pass now also probes for repo-as-OS structures (`work/signals/`, `work/missions/`, `org/<layer>/`, `CONFIG.yaml`, `CODEOWNERS` plus a policy directory) and surfaces them before phase 3 so the proposal can offer bridge defaults (`connections.work-repos[]`) instead of inventing parallel structure.
- **`kb-setup` graduation criteria** — phase 3 question 14 now surfaces the 2–3 concrete things a team needs before safely advancing to the next adoption stage. The list is informational and can be skipped; the criteria themselves are normative in `references/adoption-stages.md`.

### Changed

- **Glossary picks up adoption-stage vocabulary** — new canonical terms `adoption stage`, `capture-only mode`, and `repo-as-OS framework`. Non-term mappings now steer "maturity level (for adoption)" and "AI maturity model / agentic curve" to **adoption stage**, and "pre-agent mode / manual mode" to **capture-only mode**, so reviewers do not have to litigate vocabulary in PRs.
- **`docs/REFERENCE.md` cross-references renumbered** — the previous §9 (Plugin / Marketplace Package Layout) and §10 (Harness Support) are now §11 and §12 to make room for the two new sections. The kb-operator autonomous-loop note now points at §12 instead of §10.
- **Per-file versions and root manifests rolled to 5.4.0** — `VERSION`, `plugin.json`, `.claude-plugin/marketplace.json`, the regenerated `plugins/kb/plugin.json`, `docs/REFERENCE.md`, `docs/glossary.md`, `plugins/kb/skills/kb-setup/SKILL.md` (catching up from the unbumped 5.2.0 since this release changes the question flow), `plugins/kb/skills/kb-management/SKILL.md`, and `plugins/kb/agents/kb-operator.md`. README badge and Status row updated.

### Fixed

- **CI fix** — appended the missing trailing newline to `docs/operating-model.md` so `markdownlint` (MD047) passes again. Carried forward from the post-5.3.0 follow-up; no semantic change.
- **CI fix** — replaced the `CODE_OF_CONDUCT.md` attribution link to the Contributor Covenant site root with the stable versioned code-of-conduct URL after `lychee` hit an intermittent network reset on the root page during the `dead-links` job. Carried forward from the post-5.3.0 follow-up; no semantic change.

## [5.3.0] — 2026-04-26

> **Why MINOR:** this release adds non-breaking but substantive coverage for the day-to-day operating model of software engineering organizations. The existing layer graph, command surface, and core knowledge artifacts stay valid, but the spec now standardizes the missing handoff artifacts between direction, design, delivery, and operations.

### Added

- **Software-engineering operating model** — added `docs/operating-model.md`, a new concept document that maps the main role loops in a software company (direction, design, delivery, operations, learning), the daily/weekly questions those roles answer, and the minimum durable artifact chain needed to keep cross-role work legible.
- **Optional `delivery` and `operations` feature families** — `docs/REFERENCE.md` now declares `delivery` and `operations` as opt-in layer features. `delivery` owns `_kb-delivery/briefs/` and `_kb-delivery/specs/`; `operations` owns `_kb-operations/releases/YYYY/` and `_kb-operations/incidents/YYYY/`.
- **Four standard artifact formats for cross-role handoffs** — the reference now defines canonical markdown shapes for `Brief`, `Spec`, `Release record`, and `Incident record`, and `plugins/kb/skills/kb-management/templates/` now ships matching templates (`brief.md`, `spec.md`, `release.md`, `incident.md`).

### Changed

- **Behavioral and vocabulary surface now recognizes the new artifacts** — `kb-management` now treats `brief`, `spec`, `release`, and `incident` as first-class feature keywords, and the glossary now names `delivery`, `operations`, `brief`, `spec`, `release record`, and `incident record` as canonical terms. Non-term mappings now steer `RFC` to `spec`, `PRD` / `project charter` to `brief`, and `postmortem` to `incident record`.
- **Public entry points now expose the broader company operating loop** — README now points readers to the new operating-model document, explains the added delivery/operations handoff layer in the product value proposition, and rolls the framework version to `5.3.0` across the published manifests.

## [5.2.0] — 2026-04-25

> **Why MINOR:** two non-breaking additions to the user-facing behavior of the reference skills. The command surface, file formats, and layer-graph contract are unchanged, but invocation can now reach the skills through natural-language feature keywords (not only `/kb`), and onboarding now starts from the user's goals instead of from a feature list. Existing `/kb`-driven adopters keep working unchanged.

### Added

- **kb-management trigger surface covers every first-class feature keyword** — `plugins/kb/skills/kb-management/SKILL.md` `triggers:` now lists, in addition to `/kb`, the disambiguated multi-word phrases for findings, decisions, workstreams, vmg, meeting notes, sparring sessions, briefings, daily/weekly summaries, progress reports, and migrations. Harnesses fire the skill on those phrases without requiring the user to remember `/kb`. The "When to invoke" section was expanded with an explicit rule: when the skill is reached via a feature keyword rather than `/kb`, the response must name the inferred `/kb …` flow, restate the inferred target layer, and ask for confirmation before any mutation; read-only flows (`status`, triage scans) may proceed immediately.
- **kb-setup runs a four-phase, goal-oriented interview** — `plugins/kb/skills/kb-setup/SKILL.md` replaces the flat 12-block, feature-list interview with: Phase 1 (Q1–Q7) open prose about identity, what the user tracks/decides, why now, audience, sources, desired outputs, and autonomy preference; Phase 2 (Q8–Q10) workspace root, IDE targets, and a discovery pass; Phase 3 (Q11–Q13) one derived plan covering layer graph, connections, dashboard panels and report types, automation level, and HTML styling, presented for inline adjust-or-confirm; Phase 4 (Q14) one summary and one yes. Layer features, contributor-mode flags, scope, and role are derived from the user's answers and not enumerated by the user. A compact expert path stays available for users who already know the framework.

### Changed

- **Setup and cross-layer guidance are easier to follow** — README now separates quick plugin install from the longer guided workspace scaffold and points new adopters at `docs/examples/first-hour.md`; the first-hour walkthrough now matches the acceptance baseline more closely (phase terminology, parent fields, manual-only automation level); `docs/REFERENCE.md` and `kb-setup` now document what automation levels 1/2/3 mean instead of leaving adopters to infer them from `.kb-config/automation.yaml`.
- **Promotion and consumer-layer semantics are now explicit** — the glossary now distinguishes contributor-scoped artifacts from contributor-capable layers, `docs/collaboration.md` and `docs/REFERENCE.md` now say that consumer layers may receive digests but are never promote/publish targets, and `kb-management` now links to a dedicated `promote-contract.md` reference that explains staged review for multi-user targets versus direct writes for single-user targets.
- **Website (`index.html`) layer section is now clearer than the README diagram** — replaced the abstract "anchor → parent → parent's parent" flow with a concrete named-layer chain (`anchor → team → org → company`) carrying both promote and digest arrows per hop, role tags on each box (contributor / consumer with a dashed border for the read-down-only case), and a separate marketplace row that visually shows publish as a side-attachment rather than a slot in the chain. New CSS classes (`.layer-chain`, `.layer`, `.layer-hop`, `.marketplace-row`) carry the layout; the old `.flow-box` / `.flow-arrow` classes are kept for the proof strip and other unaffected sections.
- **README header trimmed** — removed the "One-page visual overview → `index.html`" pointer in the header and the `index.html` entry from the "Where to start" list, so the README is the canonical narrative entry point and the visual landing page stands on its own. Repo-layout and tooling references to `index.html` (it is still the GitHub Pages root and is generated by `scripts/generate-index.py` for any KB layer) are unchanged.
- **First-run acceptance baseline tracks the new question flow** — `docs/first-run-acceptance.md` Step 4 now lists baseline answers for the goal-oriented Phase 1 + Phase 2 questions and the expected derived proposal in Phase 3 (two layers, anchor, workstream, connections, dashboard panels, automation level, styling). The acceptance contract still proves the same two-layer graph and the same cross-layer promote/digest path, but the proof now also asserts that the user never had to enumerate features themselves.
- **Per-file versions and root manifests rolled to 5.2.0** — `VERSION`, `plugin.json`, `.claude-plugin/marketplace.json`, the regenerated `plugins/kb/plugin.json`, `docs/REFERENCE.md`, `docs/first-run-acceptance.md`, `plugins/kb/skills/kb-management/SKILL.md`, `plugins/kb/skills/kb-setup/SKILL.md`, and `plugins/kb/agents/kb-operator.md`. `AGENTS.md` bumped to `0.5`. README badge and Status row updated.

### Fixed

- **Website layer-chain arrow directions match the horizontal layout** — `index.html` `.layer-hop` now uses `promote →` / `← digest` on the desktop horizontal chain (parent is to the right) and switches to `↓ promote` / `↑ digest` on the mobile vertical stack (parent is below) via a media-query-driven `.axis-h` / `.axis-v` swap. The previous `↑ promote` / `↓ digest` labels read backwards on the desktop layout because the chain itself runs left-to-right.

## [5.1.1] — 2026-04-25

> **Why PATCH:** documentation-only consistency sweep after a concept audit. No runtime semantics, no command-surface changes, no file-format changes. Every fix corrects drift between the Markdown spec, the website, and the per-file headers; or makes already-shipped behavior visible in the docs that adopters read first.

### Fixed

- **Website (`index.html`) no longer teaches a retired model and no longer ships a non-existent install command** — replaced the "Five layers, one command" / `L1`–`L5` flow boxes with the 5.0 flexible layer graph (anchor → parent chain, marketplace as cross-cutting), removed the false "L1 Personal — required" claim, dropped the bogus `/install-marketplace …` slash command in favor of the documented `/plugin marketplace add` + `/plugin install kb@agentic-kb`, called out the missing `git clone` step for installer-backed harnesses, replaced the marketing claim "Install in 60 seconds" with the README's "about a minute", expanded the proof-strip wording to match the 2-layer acceptance baseline, expanded "Four kinds of memory" into the full first-class building-block set (decisions, notes, tasks, workstreams included), and refreshed the command preview list with `digest connections`, migration helpers, and `report progress`.
- **`AGENTS.md` changelog and version field caught up with the framework** — bumped from `0.3` to `0.4`, added the missing changelog rows for the 4.1.0, 5.0.0, 5.1.0, and 5.1.1 release alignments so a new reader doesn't see "v4.0.0 release alignment" as the most recent state.
- **README compatibility model wording matches its own table** — the prose said "three setup tiers" while the table listed five rows; rules-only and not-feasible buckets now sit in a separate "not yet covered" sub-table so the supported-tier count and the row count agree.
- **Glossary and `REFERENCE.md §10` now document the same harness universe** — the Harness term and the harness-support matrix both call out the rules-only (Cursor, Windsurf) and not-feasible (Aider, raw Claude / Inflection Pi) buckets the README references, so the spec is the single source of truth instead of the README inventing terms on its own.
- **First-run acceptance path is back in version sync** — bumped `docs/first-run-acceptance.md` from `5.0.0` to `5.1.1` and added an optional Step 10 covering `/kb migrate layer-model` and `/kb migrate archives` for legacy adopters, so the canonical onboarding proof now exercises the migration helpers that already shipped in 5.1.0.
- **Historical L1/L2 vocabulary in the 2026-04-21 walkthrough is now flagged** — added a retroactive vocabulary note to `docs/test-reports/2026-04-21-first-run-walkthrough.md` so the retired ladder language is preserved as historical record without contradicting the current glossary.

### Changed

- **Per-file version headers caught up with the framework** — `docs/REFERENCE.md` (5.1.0 → 5.1.1), `docs/glossary.md` (0.2 → 0.3), `docs/first-run-acceptance.md` (5.0.0 → 5.1.1), `AGENTS.md` (0.3 → 0.4). Manifest versions (`VERSION`, root `plugin.json`, `.claude-plugin/marketplace.json`, `plugins/kb/plugin.json`) all rolled to `5.1.1` for the audit closeout.

## [5.1.0] — 2026-04-25

> **Why MINOR:** this release closes the remaining 5.0.0 follow-up gaps without changing the 5.0 layer-graph semantics. It adds explicit migration helpers for legacy adopters, wires the roadmap pilot to the active layer's 5.x config model plus `connections:` tracker declarations, and brings the public command/docs surface into sync so the outstanding follow-up issues can close.

### Added

- **Explicit migration helpers for legacy adopters** — `plugins/kb/skills/kb-management/scripts/migrate_archives.py` previews or applies the year-based archive moves, and `plugins/kb/skills/kb-management/scripts/migrate_layer_model.py` converts fixed-ladder `.kb-config/layers.yaml` files into the named-layer graph while preserving workstreams and legacy roadmap blocks under the anchor layer.

### Changed

- **Roadmap pilot now understands the active layer's 5.x config contract** — `plugins/kb/skills/kb-roadmap/scripts/kb_roadmap.py` now resolves `roadmap:` from the active layer entry and normalizes trackers declared under `connections.trackers[]`, while preserving legacy `roadmap.issue-trackers[]` fallback for older adopters.
- **Public command and migration docs now describe the shipped closeout path** — `README.md`, `docs/REFERENCE.md`, `kb-management`, `kb-setup`, and the roadmap references now document `/kb migrate archives`, `/kb migrate layer-model`, and the connections-backed roadmap behavior instead of leaving the 5.0 follow-up issues as implicit tribal knowledge.

### Fixed

- **Regression coverage for the closeout helpers** — added `scripts/test_kb_migrations.py`, extended `scripts/test_kb_roadmap.py` with a connections-backed fixture, and wired the new migration test into `.github/workflows/validate.yml` so CI exercises the repaired 5.1 surfaces directly.

## [5.0.0] — 2026-04-25

> **Why MAJOR:** the core model is now a flexible layer graph instead of a fixed L1-L5 ladder. This is a breaking semantic change for adopters and tool builders: `.kb-config/layers.yaml` moved to a list-based graph model with `anchor-layer`, `role`, `parent`, per-layer `features`, `marketplace`, and `connections`; note files are now first-class primitives; archive paths are year-based; and setup plus acceptance now prove named-layer promotion/digest flows instead of the old fixed stack.

### Changed

- **Flexible layer graph became the canonical architecture** — `docs/REFERENCE.md`, `docs/glossary.md`, `README.md`, `docs/collaboration.md`, `docs/first-run-acceptance.md`, and the core `kb-management` / `kb-setup` skill specs now describe named layers with `scope`, `role`, `parent`, `features`, `marketplace`, and `connections` instead of numbered L1-L5 slots.
- **Setup and adoption flows now scaffold the 5.0 workspace contract** — `plugins/kb/skills/kb-setup/SKILL.md`, its templates, and the first-run walkthroughs now generate anchor-layer configs, year-based archive paths, note directories, and a deterministic two-layer proof path with explicit cross-layer promote/digest behavior.
- **Cross-layer operations and reports are role-aware** — `/kb promote [file] [layer]`, `/kb digest [layer]`, `/kb digest connections`, `/kb note`, and `/kb report progress [scope]` are now part of the documented stable command surface, with consumer-only layers refusing promote/publish mutations.

### Fixed

- **Acceptance-fixture and index-generator drift against the 5.0 model** — `scripts/scaffold_acceptance_fixture.py`, `scripts/test_acceptance_fixture.py`, `scripts/generate-index.py`, and `scripts/test_generate_index.py` now cover recursive year-based findings, notes, progress reports, and the multi-layer fixture shape used by the new adoption proof.
- **Behavioral and template drift after the major rewrite** — command prompts, instructions, rituals, output examples, roadmap/journey references, and generated scaffold templates were updated so newly installed workspaces match the 5.0 reference docs instead of teaching the retired fixed-ladder model.

## [4.1.0] — 2026-04-25

> **Why MINOR:** this release adds non-breaking marketplace-contract guidance for reusable plugin utilities, explicit incompatibility metadata, and fixture-backed regression checks for policy/routing-heavy skills. Existing implementations remain valid; new metadata and test guidance are optional but now part of the reference spec.

### Added

- **Generic marketplace extension contract** — `docs/REFERENCE.md`, `README.md`, and `CONTRIBUTING.md` now describe three portable patterns adopted from broader skill ecosystems without any vendor lock-in: optional plugin-local `utils/` helpers declared via `utils:` frontmatter, explicit `incompatible_with` metadata for overlapping trigger surfaces, and fixture-backed regression checks under `tests/fixtures/` for safety-, routing-, and scoring-heavy skills.

## [4.0.0] — 2026-04-25

> **Why MAJOR:** two breaking semantic changes for downstream implementations: (1) `/kb promote` for local team KBs is now a composite operation that runs the destination-layer review and archives the staged input rather than stopping at the team inbox, and (2) every artifact flow that performs external reads MUST emit a structured preflight summary before fetching, and HTML artifacts only complete after a defined post-generation QA sweep. Implementations that rely on the older `promote` semantics or that treat artifact write as completion will fail the new contracts.

### Changed

- **`/kb promote` for local team KBs** — promotion is now a composite operation: stage the intake in the target contributor `_kb-inputs/`, run the L2 review immediately in team context, archive the staged input under `_kb-inputs/digested/YYYY-MM/`, and leave the reviewed result in `_kb-references/`. Updated `kb-management`, its command/output docs, the team-scaffold template, and collaboration guidance so promote no longer teaches a mandatory second manual `/kb review` after every L1 promotion.
- **Artifact-generation control points are now explicit spec rules** — any `/kb` flow that needs external reads to produce a capture or artifact must show a structured preflight summary before fetching, and HTML artifact completion now includes a mandatory QA sweep (theme toggle, placeholders/assets, readability/contrast, keyboard affordances, offline/self-contained behavior). Updated `docs/REFERENCE.md`, `kb-management`, `kb-operator`, and `html-artifacts.md` so the reusable pattern from live roadmap/presentation work is part of the core concept rather than tribal knowledge.

### Fixed

- **Harness install surfaces now match the documented native entrypoints** — `scripts/install.py` no longer clones the VS Code `/kb` prompt verbatim into every non-VS Code harness. Claude Code and OpenCode get generated command markdown without VS Code-only tool setup text, Gemini gets the same cleaned body inside TOML, Kiro now installs `.kiro/skills/kb/SKILL.md`, and Codex now installs `.agents/skills/kb/SKILL.md` instead of the retired `~/.codex/prompts/` path. The public setup docs and landing copy now describe the same support tiers and file locations. Fixes #63, #65.
- **Shipped HTML templates now enforce the self-contained artifact contract directly** — removed external font fetches from the checked-in report and presentation templates, extended `scripts/check_html_artifacts.py` to catch external CSS `@import` usage, and added `scripts/test_html_templates.py` so CI validates the shipped template family directly. Fixes #64.
- **Shared-adoption proof is now executable in-repo** — added `scripts/scaffold_acceptance_fixture.py` plus `scripts/test_acceptance_fixture.py` for the layered personal → team → org scaffold, and added `scripts/test_kb_roadmap.py` for the lean export-backed roadmap proof path. Together they move the strongest adoption claims from prose to regression-tested fixtures. Fixes #66.

- **`/kb` slash command missing after Claude Code marketplace install** — `plugins/kb/commands/kb.md` was not shipped, so Claude Code treated `/kb` as "Unknown command" for anyone installing via `/plugin install kb@agentic-kb`. Only the dev-install path (`scripts/install.py --target claude`) wired the slash command by copying `kb.prompt.md` into `.claude/commands/`. Added the missing plugin-root `commands/kb.md` (verbatim copy of the canonical prompt) so Claude Code auto-registers `/kb` from marketplace install. Fixes #59.
- **Root `index.html` surfaces markdown content** — `scripts/generate-index.py` now scans `_kb-references/{findings,topics}/`, `_kb-ideas/`, and `_kb-decisions/` alongside HTML artifacts, rendering them under dedicated `Findings` / `Topics` / `Ideas` / `Decisions` categories. Titles are extracted from the first `# heading` (with `Finding:` / `Topic:` / `Idea:` / `D-YYYY-MM-DD-slug:` prefixes stripped); dates from the filename or `**Date**:` / `**Created**:` fields. Archived ideas/decisions are excluded. `scripts/test_generate_index.py` gains coverage for all four markdown categories. Fixes #21.
- **Placeholder mapping table completeness** — `kb-setup/SKILL.md` §Templates now declares `{{WORKSPACE_ROOT}}` (Q4), `{{ALIAS_INDEX}}` (computed), and the five workstream-stub placeholders (`{{ACTIVE_DECISIONS}}`, `{{KEY_TOPICS}}`, `{{CURRENT_STATE}}`, `{{ACTIVE_THREADS}}`, `{{DEPENDENCIES}}`) so the post-write `{{…}}` gate no longer forces agents to improvise or silently block Step 8. Fixes #20.
- **Version metadata and shipped dashboard copy aligned for v3.4.3** — `README.md` now advertises `spec-v3.4.3`, the root/plugin/Claude marketplace manifests now all report `3.4.3`, and the shipped `kb-management` `index.html` template describes `dashboard.html` as including live topics. Follow-up for PR #54.
- **Dashboard topics visibility** — `scripts/generate-dashboard.py` now renders a dedicated `topics` panel from `_kb-references/topics/`, the default `artifacts.yaml` dashboard panel list includes it, and the dashboard contract docs (`docs/REFERENCE.md`, `kb-management`, `kb-operator`, `html-artifacts.md`) now describe topics as first-class live dashboard state. Fixes #22.
- **`_kb-references/strategy-digests/` added to the directory contract** — the digest watermark (`.last-digest`) and per-layer digest findings already lived there in practice (read by `generate-dashboard.py` and by the `Upstream digest drift` triage signal), but neither `kb-management/SKILL.md` §Directory contract nor `docs/REFERENCE.md` §Workspace layout declared it, and `kb-setup` didn't pre-create it. All three now do. Fixes #19.
- **Version metadata aligned for the phantom-overview fix** — bumped `plugins/kb/skills/kb-management/SKILL.md` from `3.4.1` to `3.4.2` and `plugins/kb/agents/kb-operator.md` from `3.4.0` to `3.4.2` so the shipped behavioral change is versioned under the current framework patch release.
- **`docs/examples/first-hour.md` setup-flow drift** — the first-hour walkthrough now matches the current `kb-setup` interview order: 13 core question blocks, VMG explicitly documented as Q3, and the remaining onboarding answers renumbered through Q13. Fixes #27.
- **Phantom Family-1 live overviews dropped** — `kb-management` SKILL rule 9, `command-reference.md` `--refresh-overviews`, `html-artifacts.md` §Family 1, `docs/REFERENCE.md` §HTML artifacts, `kb-operator.md` §Always-current overviews, and `docs/examples/first-hour.md` all stop claiming that `inventory.html`, `open-decisions.html`, and `open-tasks.html` get regenerated after every mutation. No generator ever existed for those three files; their equivalent signals already live in `dashboard.html` panels. The orphan cards pointing to them in `kb-management/templates/index.html` are replaced with a dashboard card. Fixes #18.
- **`docs/REFERENCE.md` workspace-root prompt contract** — the required-files row no longer treats `.github/prompts/kb.prompt.md` as universal. `REFERENCE.md` now mirrors the established harness-specific setup contract: VS Code uses `.github/prompts/` + `.github/instructions/`, Claude Code and OpenCode do not require workspace prompt files, and compatible CLI workflows reuse whatever prompt/instruction files are already present in the initialized workspace. Fixes #28.
- **`kb-setup` version alignment** — bumped `plugins/kb/skills/kb-setup/SKILL.md` from `3.4.0` to `3.4.1` so the shipped placeholder-gate behavior fix is versioned under the current framework patch release.
- **Setup post-write placeholder gate blocked on shipped template** — `kb-setup` Step 8 scanned every file in the scaffolded workspace for residual `{{…}}` markers and refused to commit when it found any. The shipped `presentation-template.html` (and its branded sibling) intentionally keep seven `{{…}}` fields because they are filled per-artifact by `/kb present`, so the gate failed on every first run. The post-write check + `docs/examples/first-hour.md` + `docs/first-run-acceptance.md` now exempt those filenames. Fixes #17.
- **Idea lifecycle field canonicalized to `**Stage**:`** — `generate-dashboard.py` now reads the `**Stage**:` bold-bullet field on idea files (matching `docs/REFERENCE.md` and the `idea.md` template) and accepts a legacy `**Status**:` fallback so pre-3.5 idea files keep rendering. Audit K5 + cross-primitive rule X3 updated to the canonical field. `test_generate_dashboard.py` gains a regression case covering both forms. Fixes #35.
- **`command-reference.md` triage table completeness** — the bare-`/kb` signal list now includes `Top task` and `External completions`, matching the generated `kb.prompt.md` contract and the task-handling rules already defined in `kb-management`. Follow-up within PR #49.
- **`command-reference.md` drift** — the task verb is now declared canonical as `/kb task` (with `/kb todo` and `/kb tasks` as accepted aliases), a new Ideas section documents `/kb idea` and `/kb develop`, and the stale-task triage rule is split into `focus-overdue-days` (7) and `backlog-stale-days` (14) matching the canonical bullet-in-file data model used by `kb.prompt.md` and SKILL rule 11g. Fixes #24, #25, #26.
- **`scripts/install.py` drift detection** — existing installs now compare source and installed front-matter `version:` values for skills and agents before skipping. Re-runs report `up-to-date` when versions match, `stale (old -> new)` when a copied install is behind, and the generic `skip (exists)` path now tells adopters to rerun with `--force` to reinstall/update. Fixes #29.
- **Evaluation gate Q5 polarity and scoring examples** — `kb-management` now frames Q5 as "materially new compared to existing topics", defines the numeric score as the count of yes answers across Q1-Q5, removes the obsolete VMG `+1` bonus from the normative summaries, and fixes the worked examples/log wording. Fixes #30.
- **`**Maturity**:` never written on findings/topics** — added the field to `finding.md` and `topic.md` templates, wired the capture flow in `kb-management/SKILL.md` to set it from the gate outcome, and aligned the triage signal (`kb.prompt.md`, `command-reference.md`) and audit rule K1 (`audit.md`) to read the same bold-bullet form. Fixes the broken `capture → promote` surfacing loop (#14, #31).
- **Open-decisions triage signal never fires** — aligned the `/kb` triage rule and audit K4 to read the decision template's `**Status**:` bold-bullet form instead of a non-existent `status: proposed` YAML frontmatter. Triage now counts open decisions as files under `_kb-decisions/` whose status is not `resolved` / `superseded` / `dropped`. Fixes #15.
- **Dashboard focus/backlog parser bugs** (`scripts/generate-dashboard.py`) — the parser now respects `##` section boundaries (no more `(none)` under `## Waiting` counted as a focus task), strips HTML comments from bullet titles so metadata like `<!-- workstream: … -->` no longer leaks into the rendered UI, and skips placeholder bullets (`(none)`, `(empty)`, `—`, `-`). Added `scripts/test_generate_dashboard.py` with CI coverage. Fixes #23.
- **Missing `idea.md` scaffold template** — restored `plugins/kb/skills/kb-management/templates/idea.md` so `/kb idea` has a canonical file source again, matching the behavioral spec and REFERENCE docs.
- **`/kb setup` scaffold source ambiguity** — clarified in `plugins/kb/skills/kb-setup/SKILL.md` which personal-KB scaffold files come from `kb-setup/templates/` versus `kb-management/templates/`, so implementers no longer have to guess across two directories.
- **Residual vendor-neutrality cleanup** — removed the last internal-specific residue from the public spec by replacing an internal example label in `kb-roadmap` adapter docs and generalizing a changelog note that still exposed a vendor-prefixed token pattern.
- **Vendor-neutrality sweep** — removed all vendor-specific terms from scripts, templates, and plugin skill docs:
  - `generate-dashboard.py` / `generate-index.py`: removed vendor logo SVG and vendor-prefixed CSS variable mappings; only generic token names remain.
  - `kb-setup/templates/artifacts.yaml`: removed vendor logo option; built-in choices are now `hexagon | none` plus custom `logo-file`.
  - `kb-journeys/SKILL.md`: removed internal-repo path reference from mock-extraction script description.
  - `kb-roadmap` references and script: replaced vendor-specific hierarchy terms with generic equivalents (Theme, Initiative, Epic) throughout `adapters.md`, `html-template.md`, and `kb_roadmap.py`.
- **`CONTRIBUTING.md` stale reference** — replaced `make check` (no Makefile exists) with "Local checks pass".
- **Version alignment** — `kb-management` SKILL.md, `kb-setup` SKILL.md, and `kb-operator` agent.md now all declare `version: 3.2.0`, matching the framework version.
- **`spec-summary.md` layout discrepancy** — decisions directory now shows active decisions at root (matching REFERENCE.md and SKILL.md), not under an `active/` subdirectory. Added missing `_kb-ideas/`, `index.html`, and `dashboard.html` entries.
- **`command-reference.md` stale path** — promote command now references `_kb-inputs/` (not old `inputs/`). Section renamed to "Decisions & Tasks" for glossary consistency.
- **`rituals.md` rule number drift** — task-reconciliation references updated from `#10c` to `#11c` (matching current SKILL.md rule numbering).
- **`setup-flow.md` broken links** — fixed relative path depth for `docs/first-run-acceptance.md` cross-references (4 levels → 5 levels).
- **`REFERENCE.md` markdown-lint violations** — removed leading whitespace on heading and list items in the draft-skill config section; fixed extra table column in the changelog.
- **`generate-index.py` self-containment** — removed the external Google Fonts import so generated root artifact indexes stay fully self-contained and comply with the HTML artifact contract.
- **Stale manual-refresh guidance** (`docs/examples/first-hour.md`, `plugins/kb/skills/kb-management/references/command-reference.md`, `docs/roadmap.md`) — walkthroughs, triage rules, and roadmap status now match the shipped always-current overview behavior.
- **Manifest version drift** (`plugin.json`, `plugins/kb/plugin.json`, `.claude-plugin/marketplace.json`) — root and per-plugin marketplace metadata now match the current framework version (`3.2.0`) and describe the shipped draft extensions accurately.
- **`kb-roadmap` config-path drift** (`plugins/kb/skills/kb-roadmap/scripts/kb_roadmap.py`) — the pilot now reads `.kb-config/layers.yaml` and `.kb-config/artifacts.yaml`, with legacy fallback to the retired flat config files.

### Added

- **Multi-harness `/kb` install parity (Codex CLI, Gemini CLI, Kiro IDE)** — `scripts/install.py` now supports `--target codex`, `--target gemini`, and `--target kiro`, each writing the harness's documented native surface. Codex installs a reusable `kb` skill to `.agents/skills/kb/SKILL.md` (repo-local or `~/.agents/skills/` global), Gemini generates `.gemini/commands/kb.toml`, and Kiro installs `.kiro/skills/kb/SKILL.md`. `detect_targets()` probes all six harnesses; `--target all` fans out to every installer-supported harness. `scripts/test_install.py` covers the generated outputs, and the public docs now distinguish native command, native skill, and compatible-skill workflows explicitly.
- **Simulated-workspace regression coverage for `generate-index.py`** (`scripts/test_generate_index.py`, `.github/workflows/validate.yml`) — CI now generates a root artifact index inside a temporary KB and verifies pinned-category ordering, version-family deduplication, referenced-subpage hiding, and dual-theme output.
- **Automatic live-overview regeneration contract** (`plugins/kb/skills/kb-management/SKILL.md`, `plugins/kb/skills/kb-management/references/html-artifacts.md`, `plugins/kb/agents/kb-operator.md`, `plugins/kb/skills/kb-setup/templates/kb.prompt.md`) — overviews are now regenerated as part of every state-mutating `/kb` operation instead of being treated as a later optional refresh.
- **Top-level coverage for draft primitives** (`README.md`, `docs/REFERENCE.md`, `docs/glossary.md`, `AGENTS.md`, `CONTRIBUTING.md`) — the public spec now explicitly documents the optional `kb-roadmap` and `kb-journeys` skills, their `_kb-roadmaps/` and `_kb-journeys/` directories, and the current `plugins/kb/` source layout.

### Tooling

- **`check_consistency.py` forbidden-term scanning** — extended to cover all text file types and removed the `plugins/` exclusion so skill/agent docs are also checked.

## [3.4.0] — 2026-04-22

### Added

- **Codex CLI compatibility model** (`README.md`, `docs/REFERENCE.md`, `docs/first-run-acceptance.md`, `docs/examples/first-hour.md`, `plugins/kb/skills/kb-setup/SKILL.md`, `plugins/kb/skills/kb-setup/references/setup-flow.md`, `docs/glossary.md`) — documented Codex CLI as a compatible repo-local workflow, distinguished first-class supported harnesses from partial/manual paths, and updated onboarding plus harness-support guidance to leave room for additional CLIs and IDEs under the same model.

### Version bumps

- Root `VERSION`: 3.3.0 → 3.4.0.
- `plugin.json`: 3.3.0 → 3.4.0.
- `plugins/kb/plugin.json`: 3.3.0 → 3.4.0.
- `.claude-plugin/marketplace.json`: 3.3.0 → 3.4.0.
- `plugins/kb/skills/kb-setup/SKILL.md`: 3.3.0 → 3.4.0.
- `plugins/kb/skills/kb-management/SKILL.md`: 3.3.0 → 3.4.0.
- `plugins/kb/agents/kb-operator.md`: 3.3.0 → 3.4.0.

## [3.1.0] — 2026-04-20

### Added

- **Generic presentation template** (`plugins/kb/skills/kb-setup/templates/presentation-template.html`) — vendor-neutral reveal-style deck that adopters get via `/kb setup` Q13. Left-aligned section-title slides with a gradient underline, closing slide before an appendix divider, and a mandatory Changelog slide as the final slide.
- **Vendor-neutrality pre-push hook** (`scripts/hooks/pre-push` + `scripts/install-hooks.sh`) — runs `check_consistency.py`, `check_plugin_structure.py`, and `check_html_artifacts.py` before every push so forbidden terms, broken structure, and drift never reach the remote. Emergency bypass documented (`git push --no-verify`).
- **Blocklist guidance in CONTRIBUTING.md** — describes the optional `.forbidden-terms.txt` layered-vocabulary mechanism and how to install the pre-push hook locally.

### Fixed

- **Duplicate commands in VS Code** (`kb-management` + `kb:kb-management`): root `plugin.json` now declares only a `plugins` array pointing to `plugins/kb/` instead of listing skills/agents directly. Moved `plugins/kb/.claude-plugin/plugin.json` → `plugins/kb/plugin.json` (flat marketplace convention, matching common agent-plugin layouts). Added `x-skills` and `x-agents` to plugin manifest.
- **Physical consolidation under `plugins/kb/`**: skills and the agent are no longer duplicated between top-level `skills/`, `agents/` and symlinks inside `plugins/kb/`. The real directories now live at `plugins/kb/skills/kb-management/`, `plugins/kb/skills/kb-setup/`, `plugins/kb/agents/kb-operator.md`. Top-level `skills/` and `agents/` directories are removed. This prevents VS Code Agent Plugins from registering each skill twice (once as a root-plugin skill, once as a `kb:` sub-plugin skill).
- **`install.py`**: resolves skills/agents from per-plugin manifests (`x-skills`/`x-agents` in `plugins/<name>/plugin.json`) instead of from root `plugin.json` `skills`/`agents` keys (removed). Falls back to disk enumeration. Discovers skill/agent source paths by walking `plugins/<name>/skills/` and `plugins/<name>/agents/`.
- **`generate_plugins.py`**: no longer materialises symlinks — plugin dirs are the canonical source. Now only regenerates the per-plugin `plugin.json` manifest with `x-skills`/`x-agents` derived from the real directory contents. Still idempotent.
- **`check_plugin_structure.py`**: iterates `plugins/<name>/skills/` and `plugins/<name>/agents/` instead of the removed top-level dirs.
- **`.claude-plugin/marketplace.json`**: version bumped 2.0.0 → 3.0.0.
- **Remaining bare KB paths**: `rituals.md`, `spec-summary.md`, `migration-guide.md`, `troubleshooting.md` updated to use `_kb-` prefix convention consistently (`_kb-tasks/`, `_kb-decisions/`, `_kb-inputs/`, `_kb-references/`, `.kb-log/`).

### Changed

- **Configuration consolidated into `.kb-config/` directory**: flat `.kb-config.yaml`, `.kb-automation.yaml`, `.kb-artifacts.yaml` replaced by `.kb-config/layers.yaml`, `.kb-config/automation.yaml`, `.kb-config/artifacts.yaml`. All config lives inside the personal KB — workspace root no longer hosts config YAMLs. L2/L3 repos do not need config — the personal KB's `layers.yaml` is the single source of truth for layer topology. Updated: REFERENCE.md, both SKILL.md files, all templates, spec-summary, html-artifacts, glossary, first-hour, setup-flow, migration-guide, troubleshooting, kb-operator agent.

### Documentation additions

- **Built-in tools in SKILL frontmatter**: both `kb-management` and `kb-setup` now declare 13 built-in tools (`run_in_terminal`, `read_file`, `create_file`, `replace_string_in_file`, `multi_replace_string_in_file`, `list_dir`, `file_search`, `grep_search`, `semantic_search`, `manage_todo_list`, `vscode_askQuestions`, `fetch_webpage`, `memory`) so the chat session has all needed tools selected by default.
- **Setup questionnaire explanations**: each of the 13 interview questions now includes a brief `→` note explaining how the answer affects the resulting setup.
- **`docs/collaboration.md`**: added a dedicated human collaboration guide for shared KB workspaces, including layer responsibilities, review points, action-mode clarity, and failure recovery norms.
- **`docs/first-run-acceptance.md`**: added a deterministic onboarding acceptance path with explicit install-vs-init boundaries, expected first outputs, scaffold checks, and a team-lead rollout checklist.
- **Collaboration-safe output contract**: added `plugins/kb/skills/kb-management/references/output-contract.md`, tightened output semantics in `kb-management`, and updated examples so read-only, proposed, and applied actions are auditable for humans.

---

## [3.0.0] — 2026-04-19

### Breaking — Directory renames

All KB-managed folders use a `_kb-` prefix to clearly separate them from user files and non-KB directories:

| Old | New | Reason |
|-----|-----|--------|
| `inputs/` | `_kb-inputs/` | `_kb-` prefix — visible, sorted to top, unambiguously KB-managed |
| `ideas/` | `_kb-ideas/` | Same |
| `decisions/` | `_kb-decisions/` | Same |
| `tasks/` | `_kb-tasks/` | Same |
| `references/` | `_kb-references/` | Same |
| `workstreams/` | `_kb-workstreams/` | Same |
| `log/` | `.kb-log/` | Dot prefix — truly hidden infra you never browse |
| *(new)* | `.kb-scripts/` | Same — hidden infra |

Convention: `_kb-*` = visible KB structure (you browse these, KB agents manage them), `.kb-*` = hidden infrastructure.

Team KB contributor folders now **mirror personal KB structure** — `_kb-inputs/` + `_kb-references/` instead of the old `inputs/` + `outputs/` pattern.

**Migration**: `git mv inputs _kb-inputs && git mv ideas _kb-ideas && git mv decisions _kb-decisions && git mv tasks _kb-tasks && git mv references _kb-references && git mv workstreams _kb-workstreams && git mv log .kb-log`.

### Changed

- `docs/REFERENCE.md` — all L1/L2/L3 layout diagrams, required-files table, file format headings, and the five-layer ASCII overview updated to new directory names. Version bumped to 3.0.
- `docs/glossary.md` — Focus, Idea, Task paths updated.
- `docs/examples/day-in-the-life.md` — all path references updated.
- `docs/examples/first-hour.md` — all path references updated.
- `skills/kb-management/SKILL.md` — directory contract, log rule, flow primitives updated.
- `skills/kb-management/references/` — command-reference, evaluation-gate, html-artifacts, rituals, spec-summary updated.
- `skills/kb-setup/SKILL.md` — Step 3 (personal KB scaffold) and Step 4 (team KB scaffold) directory lists updated.
- `skills/kb-setup/references/` — setup-flow, migration-guide updated.
- `skills/kb-setup/templates/` — personal-kb-README, personal-kb-AGENTS, team-kb-README, team-kb-AGENTS, org-kb-README, kb.prompt, kb.instructions updated.
- `agents/kb-operator.md` — `_kb-inputs/` in capture loop.

### Version bumps

- Root `VERSION`: 2.2.0 → 3.0.0.
- `plugin.json`: 2.2.0 → 3.0.0.
- `docs/REFERENCE.md`: 1.0 → 3.0.
- `skills/kb-setup/SKILL.md`: 2.2.0 → 3.0.0.
- `skills/kb-management/SKILL.md`: 2.2.0 → 3.0.0.
- `agents/kb-operator.md`: 2.2.0 → 3.0.0.

---

## [2.2.0] — 2026-04-19

### Removed

- **`docs/concept/` (12 files) and `docs/spec/` (11 files)** — consolidated into a single `docs/REFERENCE.md`. The behavioral spec is the skill/agent files themselves; the reference doc retains only implementation-critical structure (architecture, layout, formats, HTML contract, security, marketplace).

### Changed

- `docs/REFERENCE.md` — new single-file reference replacing 23 concept/spec docs.
- All cross-references (`README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `agents/kb-operator.md`, `docs/roadmap.md`, `scripts/check_html_artifacts.py`, `skills/kb-management/references/spec-summary.md`) updated to point to `docs/REFERENCE.md`.
- `README.md` — replaced `<org>` placeholders with actual repo URL (`wlfghdr/agentic-kb`). Restructured install section as "Getting started": marketplace-first flow (connect → `/kb setup`), cross-harness install script as optional secondary path.
- `README.md` — rewrote problem section as direct questions ("Does this sound familiar?"), renamed "The solution" → "How it works".
- `index.html` — intro now leads with the same user-facing questions; problem section renamed to "Why existing approaches fail".
- `docs/concept/02-architecture.md` — L3 now has team-isolated directories (mirroring L2's person-directories). L5 clarified as reference-only (no bottom-up input). Added contributor-unit / cross-analysis summary to the ASCII diagram.
- `docs/spec/workspace-layout.md` — L3 directory layout updated with per-team `_kb-inputs/` + `_kb-references/` structure. Required-files table updated.

### Added

- `docs/concept/11-ideas.md` — Ideas as first-class incubation objects with lifecycle (`seed → growing → ready → shipped | archived`), `/kb develop` sparring flow, pattern detection (3+ signal convergence), annotations, freshness tracking.
- `docs/concept/12-vision-mission-goals.md` — VMG strategic steering model across all layers. Vision (years), Mission (quarters), Goals (weeks–quarters). Evaluation gate enhancement, task prioritization, cross-layer coherence checks, ritual integration.
- `/kb idea [text]`, `/kb develop [idea]` commands.
- `ideas/` directory in workspace layout (L1, L2, L3).
- `idea.md` template added to kb-management skill.
- `idea-create`, `idea-develop`, `idea-ship` log operations.
- Idea lifecycle management in kb-operator agent (Section 4).
- VMG-aligned evaluation gate scoring, goal status in rituals.
- `skills/kb-management/templates/report.html` — comprehensive slide-deck template with 12 slide types (Cover, Metrics, Progress, Decisions, Blocked, Ideas, Kanban, Daily Digest, Stakeholder Map, Pitch, Comparison, Closing), dark/light theme, slide engine with keyboard navigation, and sample data.
- Slide composition spec in `html-artifacts.md` — defines per-report-type slide recipes (Weekly Status, Daily Digest, Pitch, Roadmap Status, Topic Presentation) and ritual triggers for report generation.
- Stakeholder auto-update rule in `07-stakeholders.md` — agent detects relevance changes during processing and suggests updates to `stakeholders.md`.
- `stakeholder-update` log operation added to `logging.md`.

### Changed (continued)

- **Renamed `todo/` → `tasks/`** across entire spec. "todo" remains a recognized command synonym. Affects: `05-tasks.md` (renamed from `05-todos.md`), workspace-layout, commands, rituals, logging, glossary, skills, agent.
- `open-todos.html` → `open-tasks.html` in all artifact references.
- Evaluation gate (08) now offers idea creation at 1–2/5 when novelty detected, and checks VMG strategic alignment.
- Memory model (03) expanded from three to four types (added Incubation).
- Overview (01) renumbered principles 1–9, added Ideas (#4) and VMG (#5).
- Skills bumped to v2.2.0, agent bumped to v2.2.0.

### Version bumps

- Root `VERSION`: 2.1.0 → 2.2.0.
- `plugin.json`: 2.0.0 → 2.2.0.
- `skills/kb-setup/SKILL.md`: 2.1.0 → 2.2.0.
- `skills/kb-management/SKILL.md`: 2.2.0 (already bumped).
- `agents/kb-operator.md`: 2.2.0 (already bumped).

---

## [2.1.0] — 2026-04-18

### Added

- `docs/examples/first-hour.md` — zero-to-first-briefing walkthrough. Covers Stage 1 (marketplace install or `scripts/install`), Stage 2 (`/kb setup` wizard with suggested answers), Stage 3 (`/kb start-day`, `/kb <URL>`, `/kb end-day`), plus a failure-mode table pointing adopters back to the right doc/skill when any stage breaks.
- `skills/kb-setup/SKILL.md` — explicit "Scope boundary — install vs. init" section separating harness-level skill distribution (marketplace or `scripts/install`) from workspace-level KB scaffolding (this skill's job).
- `skills/kb-setup/SKILL.md` — "Placeholder → interview-answer mapping" table and a mandatory post-write `grep '{{[A-Z_0-9]*}}'` gate before the initial commit. A zero-hit scan is required; otherwise the skill halts and asks for the missing values.
- `docs/spec/setup.md` — mirror scope-boundary table; Step 5/6 rewritten to stop re-doing the installer's job.
- `docs/spec/ide-support.md` capability matrix — new row for the `kb-operator` Level-3 autonomous loop: native on Claude Code + OpenCode, not natively available in VS Code Copilot (cron fallback required). Linked from `agents/kb-operator.md` §Autonomous loop.
- `docs/roadmap.md` §Near-Term — "Auto-regeneration of always-current overviews" explicitly scheduled for v2.1, with Level-1/2/3 behavior and CI-diffable fixture as acceptance criteria.

### Changed

- `skills/kb-setup/SKILL.md` Step 1 prerequisites now **abort** when required tools (`git`, at least one harness CLI) are missing, with per-OS install commands. `gh` and SSH keys stay as warnings. No more "guide install if missing" half-measure.
- `docs/spec/html-artifacts.md` §Family 1 — clarified that automatic regeneration after every state-mutating `/kb` operation ships in v2.1. In v2.0 the reference implementation regenerates overviews on explicit invocation (`/kb present`, `/kb report`, `/kb end-day`, `/kb end-week`, `/kb status --refresh-overviews`). The Family 1 refresh-trigger column is now an aspirational contract until v2.1.
- `skills/kb-management/SKILL.md` — scope note matching the html-artifacts.md change. After a mutating operation, the skill **offers** the refresh instead of running it silently.
- `agents/kb-operator.md` §Artifact generation + §Autonomous loop — same scope split (v2.0 manual, v2.1 automatic); Level-3 loop no longer claims silent overview regeneration.

### Fixed

- CI: `markdown-lint` now passes on `main`. Disabled cosmetic `MD060`/`MD040`; added blank lines around headings and lists in `AGENTS.md`; escaped `|` inside table cells in `docs/glossary.md` and `docs/spec/workspace-layout.md`; removed the duplicate empty `[0.1.0]` heading in this file.
- CI: `consistency-and-versions` now passes on `main`. Added an `[Unreleased]` section as required by `scripts/check_consistency.py`.

### Version bumps

- Root `VERSION`: 2.0.0 → 2.1.0.
- `skills/kb-setup/SKILL.md`: 2.0.0 → 2.1.0.
- `skills/kb-management/SKILL.md`: 2.0.0 → 2.1.0.
- `agents/kb-operator.md`: 2.0.0 → 2.1.0.
- `docs/spec/setup.md`: 0.1 → 0.2.
- `docs/spec/html-artifacts.md`: 0.2 → 0.3.
- `docs/spec/ide-support.md`: 0.2 → 0.3.
- `docs/roadmap.md`: 2.0 → 2.1.

---

## [2.0.0] — 2026-04-18

### Changed

- Moved `examples/html/overview.html` to `index.html` at repo root — serves as GitHub Pages landing page and is easy to find/open locally.
- Added `index.html` template to kb-management skill — every generated KB gets a root index linking to reports, decisions, and todos.
- Updated all internal references and relative links accordingly.
- Version bump to 2.0.0 for initial public release.

---

## [0.2.0] — 2026-04-18

### Added

- **Always-current HTML overviews** regenerated after every state-mutating `/kb` operation: `inventory.html` (configured layers + external sources + workstreams + marketplace), `open-decisions.html`, `open-todos.html`, `index.html`. Watermark: `latest · YYYY-MM-DD HH:MM`. Spec: `docs/spec/html-artifacts.md` §"Family 1".
- **Daily summary** as a historical finding — generated by `/kb end-day`: `_kb-references/findings/YYYY-MM-DD-daily-summary.md` + rendered `_kb-references/reports/daily-YYYY-MM-DD.html`. Back-filled from the log if end-day was skipped.
- **Weekly summary** rendered artifact — paired with the existing weekly-summary finding: `_kb-references/reports/weekly-YYYY-WW.html`.
- `docs/overview.html` moved to `index.html` at repo root — self-contained one-page visual overview with SVG diagrams (five-layer architecture, memory model, multi-harness distribution), light + dark themes, watermark, changelog appendix.

### Changed

- **Harness compliance refactor** after verifying current docs for Claude Code, VS Code Copilot Chat, and OpenCode:
  - Moved marketplace manifest to `.claude-plugin/marketplace.json` at repo root (Claude Code spec).
  - Per-plugin manifest is now `<plugin>/.claude-plugin/plugin.json` with `name` / `version` / `description`.
  - Dropped `.opencode-plugin/` (not an OpenCode path) — real OpenCode layout is `.opencode/{skills,agents,commands}/`.
  - Agent files renamed from `<name>.agent.md` to `<name>.md` (cross-agent compatible; VS Code installer renames on copy).
  - Installer `scripts/install.py` rewritten: correct per-harness paths (`.claude/`, `.opencode/`, `.github/`), fallback global paths (`~/.claude/`, `~/.config/opencode/`, `~/.copilot/`), explicit `--target` options.
  - Added top-level `plugin.json` for VS Code Agent Plugin install via `chat.plugins.marketplaces`.
- Docs rewritten for reality: `docs/spec/marketplace-and-skills.md` v0.2, `docs/spec/ide-support.md` v0.2.
- Every ritual and every state-mutating command now regenerates live overviews as its last step.
- `docs/spec/commands.md` + `docs/spec/rituals.md` updated to reflect daily-summary generation in `end-day` and overview regeneration.
- `docs/concept/03-memory-model.md` updated: daily + weekly summaries are first-class historical findings.
- `scripts/check_consistency.py` forbidden-term list externalized to optional `.forbidden-terms.txt` (gitignored) — the spec itself no longer lists organization-specific terms.
- `README.md` trimmed and restructured around Problem → Solution → Install.

### Fixed

- Removed the one remaining internal-vocabulary reference ("Lane 2") from `docs/concept/06-workstreams.md`.
- `scripts/check_html_artifacts.py` theme-marker regex loosened to accept `[data-theme="light"]` / `[data-theme="dark"]` CSS selectors (the common idiomatic form).

---

## [0.1.0] — 2026-04-18

### Added

- Initial concept docs (`docs/concept/`): overview, architecture (5 layers), memory model, decisions, todos, workstreams, stakeholders, evaluation gate, flows, external links.
- Initial spec docs (`docs/spec/`): workspace layout, commands, rituals, automation levels, setup, marketplace + skills (multi-harness), IDE support, HTML artifacts (presentations + reports), file formats, security/privacy, logging.
- OSS scaffolding: `LICENSE` (Apache-2.0), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `AGENTS.md`, `CODEOWNERS`, issue/PR templates, dependabot config.
- Lean CI (`.github/workflows/validate.yml`): markdown lint, dead-link check, consistency + version sync check, HTML validation hook.
- Reference implementation: `skills/kb-management`, `skills/kb-setup`, `agents/kb-operator.md`; generator at `scripts/generate_plugins.py`; cross-harness installer at `scripts/install`.
