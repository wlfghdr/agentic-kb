# Test Report: First-Run Walkthrough + Command Surface

> **Date:** 2026-04-21 · **Branch:** `claude/test-installation-commands-YZtqM` · **Persona:** Nova Kaspari (convergence-guild @ retail)

This report captures a systematic, end-to-end dry-run of agentic-kb v3.3.0: installation,
`/kb setup`, capture/promote flow, and the other commands in the stable surface. It was
produced by an AI agent acting as a first-time adopter, following the spec strictly. Every
spec inconsistency the agent hit on the way was filed as a GitHub issue (#14–#31).

---

## 1. Installation

`scripts/install.py` was exercised for all three supported harnesses
(`claude-code`, `vscode-copilot`, `opencode`):

- POSIX symlink path works; `--force` reinstall works; subsequent runs idempotent.
- Auto-detection via `detect_targets()` finds `.claude/`, `.github/`, `.opencode/`.
- Installed artifacts resolve and SKILL.md files are readable through the symlink.

**Gap found:** no drift detection between source and installed version — the "skip
(exists)" branch hides stale installs after a marketplace update. Filed as **#29**.

---

## 2. `/kb setup` questionnaire

Ran through all 13 question blocks (Q1–Q13 + conditional Q11b/c/d) as Nova Kaspari,
producing:

- `nova-kb/` (L1 personal KB) with VMG, foundation, `.kb-config/{layers,automation,artifacts}.yaml`,
  workspace aliases `nk` / `cg`, automation level 2, three workstream stubs
  (`agent-orchestration`, `retail-ai-core`, `forecasting-long-tail`).
- `convergence-guild-kb/` (L2 team KB) with contributor dir.
- Workspace-level `AGENTS.md` + harness prompts.

**Gaps found while scaffolding strictly by spec:**

- Placeholder mapping table in `kb-setup/SKILL.md` is incomplete —
  `{{ALIAS_INDEX}}` and `{{WORKSPACE_ROOT}}` have no declared source. **#20**
- `presentation-template.html` legitimately contains `{{…}}`, but the
  post-write zero-placeholder grep gate would block the initial commit on it.
  **#17**
- `_kb-references/strategy-digests/` is referenced by triage + command-ref
  but not in the scaffold/directory contract. **#19**
- `docs/examples/first-hour.md` + `docs/first-run-acceptance.md` say
  "12 question blocks" and shift numbering (skipping VMG). Actual is 13+.
  **#27**
- `docs/REFERENCE.md` §3 mandates `.github/prompts/kb.prompt.md` at the
  workspace root — breaks for Claude-Code-only or OpenCode-only setups. **#28**

---

## 3. Capture + promote flow (user's primary question)

> *Funktioniert simplen `/kb` dass es zuerst in personal kb processed wird,
> dann promoted wird (zumindest bei weiterem `/kb` ausführen oder es wird vorgeschlagen)?*

**Answer: Nein, nicht automatisch.** The capture path itself works — `/kb
"paper summary"` correctly writes `_kb-references/findings/YYYY-MM-DD-slug.md` to the
personal KB under the 5-question gate. But the *promote-candidate surfacing* loop
is broken in two independent places:

1. Bare `/kb` triage looks for `maturity: durable` in finding/topic frontmatter
   (`kb.prompt.md:51`). The `finding.md` + `topic.md` templates never write that
   field, and no capture step sets it. A fresh capture is invisible to triage,
   forever. **#14**
2. Even if maturity is set manually, audit K1 fires on every finding the system
   scaffolded (template/audit mismatch). **#31** — same root cause as #14.
3. Open-decision triage signal never fires: template writes `- **Status**:
   gathering-evidence` (markdown bullet); triage expects YAML `status: proposed`
   frontmatter. Different format **and** different vocabulary. **#15**

**What *does* work:** the explicit `/kb promote <file>` path. Composite local+team
review as pitched in v3.3.0 is coherent when invoked by hand.

**What's missing for the pitched loop:** a setter for `maturity` during capture,
and a triage rule that actually matches the template output.

Tested by creating two obvious team-relevant findings
(`2026-04-21-bounded-autonomy-paper.md` with gate 5/5,
`2026-04-21-forecasting-retro.md` with gate 4/5). Bare `/kb` surfaced neither.

---

## 4. Other commands

| Command | State | Issue |
|---------|-------|-------|
| `/kb idea` | Works, but no canonical `idea.md` template — shape must be reverse-engineered. | #16 |
| `/kb develop` | Documented in SKILL + README but missing from `command-reference.md`. | #25 |
| `/kb decide` | Writes a decision file; triage + audit K4 can't read it (see §3). | #15 |
| `/kb task` / `/kb todo` | Canonicity conflict: SKILL says `task`, command-reference says `todo`. | #24 |
| `/kb digest` | Watermark location undefined (`strategy-digests/` not in scaffold). | #19 |
| `/kb rituals` | Three different stale-item thresholds across spec (7d vs 14d vs per-task-file). | #26 |
| `/kb present` | Works; but `presentation-template.html` triggers the post-write grep gate during setup. | #17 |
| `/kb audit` | K1/K4/K5 all reference fields the templates never emit. | #31 |
| `/kb status` / dashboard | Focus parser counts `(none)` under `## Waiting` as a task; renders HTML-comment metadata raw; conflates sections. | #23 |
| Root `index.html` | Only indexes HTML artifacts — findings, topics, ideas, decisions invisible on the public face. | #21 |
| Dashboard panels | No topics panel — durable accreting knowledge never shows up. | #22 |
| Rule-9 live overviews | Three of five have no generator (`inventory.html`, `open-decisions.html`, `open-tasks.html`). | #18 |
| Evaluation gate | Q5 has inverted polarity vs Q1–Q4; examples' ✅/❌ counts don't add up to the reported score. | #30 |

---

## 5. Leanness & Adoptability

The **"one command" promise is strong** — newcomers learn `/kb` and the system
does the right thing most of the time. Quality of the persisted material is
genuinely high because the 5-question gate forces a beat of thought at every
write.

**But the effective surface is not as lean as pitched:**

- 15 distinct subcommands (README §Commands: capture, review, promote, digest,
  decide, idea, develop, task/todo, rituals, present, report, audit, status,
  setup, plus bare `/kb` triage).
- Setup asks 13 question blocks + 3 conditional sub-blocks. A first-time user
  cannot finish in 15 minutes as first-hour.md claims (see #27).
- The two parallel "here's what's on your plate" surfaces — bare-`/kb` triage
  and `dashboard.html` — don't share data. Triage reports `Open decisions: 0`
  while the dashboard panel lists three open decisions, because they parse
  different fields.
- The promote loop (arguably the most important one for adoption) is wired
  through a `maturity:` field that no template ever writes (#14, #31).

**Concrete recommendations for leanness:**

1. Fix the promote loop end-to-end — set `maturity` on capture based on the
   gate score, read it from triage.
2. Collapse the three missing live-overview generators into the dashboard
   (#18 option 2).
3. Make root `index.html` pointer-index the actual markdown content (#21).
4. Pick one task verb (`task`) and one status vocabulary; cross-link once from
   a new `references/task-lifecycle.md` (#24, #26).
5. Drop `presentation-template.html` from the user workspace; keep it in the
   skill's `templates/` and instantiate on `/kb present` (#17).

These five fixes are ~2 PRs of work, tighten the feedback loop from first
capture to team awareness, and remove four of the seven spec inconsistencies
adopters will hit in the first hour.

---

## 6. Issue index

All 18 findings filed on `wlfghdr/agentic-kb`:

| # | Title | Labels |
|---|-------|--------|
| 14 | Bare `/kb` never suggests promotion — `maturity:` never set | bug, spec-gap |
| 15 | Triage open-decisions signal never fires (format/vocab mismatch) | bug, spec-gap |
| 16 | Missing `idea.md` template | bug, docs |
| 17 | Post-scaffold zero-placeholder check vs `presentation-template.html` | bug, spec-gap |
| 18 | Three of five "live overviews" have no generator | bug, spec-gap |
| 19 | `strategy-digests/` referenced but not in scaffold | bug, spec-gap |
| 20 | Placeholder table missing `ALIAS_INDEX` / `WORKSPACE_ROOT` | spec-gap, docs |
| 21 | Root `index.html` only shows HTML artifacts | bug, ux |
| 22 | Dashboard has no topics panel | enhancement, ux |
| 23 | Dashboard focus-parser bugs | bug |
| 24 | `/kb task` vs `/kb todo` canonicity conflicts | docs |
| 25 | Command-reference missing `/kb idea` and `/kb develop` | docs |
| 26 | Stale-task thresholds inconsistent (7 vs 14 days) | spec-gap, docs |
| 27 | first-hour.md claims 12 question blocks, misnumbers past VMG | docs |
| 28 | REFERENCE.md §3 mandates VS-Code-only prompt path | docs |
| 29 | `install.py` has no drift detection | enhancement, install |
| 30 | Evaluation gate Q5 inverted-logic | bug, docs |
| 31 | Audit K1 fires on every fresh finding | bug, spec-gap |

Chain: **#14 + #31** are the most urgent — they block the headline
capture→promote→team-share loop. **#15** makes the open-decisions signal
unusable. Fixing #31 coordinately resolves #14, #15, #16, #30 via a single
templates-vs-audit reconciliation pass.
