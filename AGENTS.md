# Agent Instructions

> **Version:** 0.13 | **Last updated:** 2026-05-22

This file is read first by any AI agent (and any human) working in this repository. It defines the ground rules. Layer-specific documents in `docs/` extend these rules — they never override them.

This repo is a **specification**, not a product. Work done here is documentation work: precise, versioned, cross-referenced. Code exists only to validate docs (CI).

---

## Rules

### 1. Spec-first, implementation-later

This repo defines *what* the system does and *how* it is shaped. It does not build it. Implementations live in companion repos. If a PR here proposes runtime code beyond CI tooling, reject it.

### 2. No vendor lock-in

The spec must remain IDE-agnostic, harness-agnostic, and vendor-neutral. Examples are welcome. Hardcoded product names, company names, or proprietary service references are not. The CI guards against a small list of forbidden terms; reviewers guard against the rest.

### 3. Every change is a versioned change

Any edit to a spec/concept doc MUST:

- append a row to that file's own `## Changelog` section (when the file has one — see "Which files have a per-file changelog" below),
- add a line under `## [Unreleased]` in the root `CHANGELOG.md`,
- bump the relevant version field if the change alters semantics (see [CHANGELOG.md](CHANGELOG.md) for PATCH/MINOR/MAJOR rules).

**Which files have a per-file changelog (and which do not):**

| File category | Per-file `## Changelog`? | Why |
|---------------|--------------------------|-----|
| Skill specs (`plugins/kb/skills/*/SKILL.md`) and skill references (`plugins/kb/skills/*/references/*.md`) | yes | They are standalone behavioral spec docs that adopters version-pin |
| Agent specs (`plugins/kb/agents/*.md`) | yes | Same reason |
| `docs/REFERENCE.md`, `docs/collaboration.md`, `docs/concurrency.md`, `docs/operating-model.md`, `docs/role-handbook.md`, `docs/glossary.md`, `docs/first-run-acceptance.md` | yes | Each is a standalone normative doc |
| `docs/roadmap.md`, `docs/examples/*.md` | yes (recommended) | Tracks how the example or roadmap drifted |
| `AGENTS.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` | yes | Long-lived governance docs |
| `README.md` | **no** | The root `CHANGELOG.md` is the single source of truth for the release narrative the README points at. A per-file changelog block on the README duplicates `CHANGELOG.md` and ages badly. The README footer links to `CHANGELOG.md` instead |
| Inline format examples inside fenced ``` ```markdown ``` ``` blocks (e.g. the `## Changelog` lines inside Topic / Brief / Spec format examples in `docs/REFERENCE.md` §4) | **no** | Those `## Changelog` lines document that *the file format* requires an inline changelog. They are spec content, not changelogs of the enclosing doc |
| Templates under `plugins/**/templates/` | **no** | Templates are scaffolded into adopter KBs; they carry their own inline changelog placeholders for the artifact they instantiate, not for the template |
| Generated artifacts (`index.html`, `dashboard.html`, plugin manifests under `plugins/*/plugin.json`) | **no** | Generated; the source they regenerate from carries the changelog |

When in doubt: if a reader would version-pin or audit the file directly, it gets a per-file changelog. If it is a derived view, a scaffolded copy, or a marketing entry point that links to the canonical changelog, it does not.

### 4. Cross-references stay live

Every link in a spec doc must resolve. CI enforces this via `lychee` (external) and `scripts/check_consistency.py` (internal). Broken links = red CI = not done.

### 5. Lean over exhaustive

A spec section that says the same thing three times is worse than one that says it once. When in doubt, cut. Examples belong in `docs/examples/`, not inline.

### 6. CI green is the definition of done

No PR is ready for review until CI is green. A red `main` is the top-priority fix for maintainers. Never skip hooks; never merge with failing checks.

### 7. Commit, push, keep the tree clean

Agents and contributors must not leave work stranded locally. Every completed unit of work ends in a commit on the target branch. No dirty repos, no stale branches. Agents should offer to commit/push/PR after substantive changes — and only push if CI is expected to stay green.

### 8. Additive over destructive

When in doubt, add a section rather than rewrite one. The changelog makes intent traceable. Deletions require a justification in the PR description.

### 9. Honor the doc structure

- `docs/REFERENCE.md` — architecture, layout, formats, and contracts. The implementation-critical reference.
- `docs/examples/` — illustrative walkthroughs. Not normative.
- `docs/roadmap.md` — open items, explicitly unresolved.
- `docs/glossary.md` — authoritative terms.
- `plugins/kb/skills/*/SKILL.md` + `plugins/kb/agents/*.md` — the behavioral spec. These ARE the spec.

The skills and agent files are the source of truth for behavior. `REFERENCE.md` is the source of truth for structure and formats.

### 10. One canonical term per concept

If a concept has a term in `docs/glossary.md`, use that term everywhere. Don't invent synonyms mid-doc. If a better term is found, update the glossary and all references in the same PR.

### 11. Keep artifact control points explicit

If a change affects capture, reporting, presentations, or any artifact flow that reads beyond local KB files, the instructions and spec must keep two control points visible:

- external reads require a preflight summary before fetch,
- HTML artifacts are not complete at file-write; they complete only after the defined QA sweep passes.

Keep this stated once, crisply, and point to the owning contract instead of restating the whole checklist.

---

## Before Starting Any Task

1. Read this file.
2. Read [README.md](README.md).
3. Read [docs/collaboration.md](docs/collaboration.md) if the change affects shared layers, human handoffs, or multi-user behavior.
4. Read [plugins/kb/skills/kb-management/references/html-artifacts.md](plugins/kb/skills/kb-management/references/html-artifacts.md) if the change affects artifact generation, external-source reads during generation, or artifact completion criteria.
5. Identify which docs your change touches (`docs/REFERENCE.md`, plugin skill docs, or agent docs).
6. Draft the change.
7. Update the per-file changelog, the root `CHANGELOG.md`, and `VERSION` if applicable.
8. Run local checks (see [CONTRIBUTING.md](CONTRIBUTING.md)).
9. Open a PR with a description that answers: what changed, why, what it breaks (if anything).

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-22 | Bumped AGENTS version to 0.13 to track the audit-tracker closeout sweep (#106, #109, #110) and Rule 3 refinement: Rule 3 now carries an explicit "which files have a per-file changelog" table (skill/agent specs, long-lived docs/*, governance docs = yes; README, templates, generated artifacts, and inline `## Changelog` lines inside fenced format examples = no); concurrency contract added (`docs/concurrency.md`); README command list trimmed to the canonical reference; `scripts/check_consistency.py` extended with a command-list drift check; pre-v5.0 release history split into `CHANGELOG.archive.md`. AGENTS rules unchanged in semantics — Rule 3 just made explicit | Audit-tracker closeout |
| 2026-05-22 | Bumped AGENTS version to 0.12 to track the concept/spec-gap audit sweep #4 closeout (#107, #108, #111, #112, #113): backlink format codified in `docs/REFERENCE.md` §4 + promote-contract.md + new K11 audit rule; retro `status: open \| tracked \| closed` lifecycle codified in §4 + template + command-reference.md + new K12 audit rule; HTML artifact lifecycle (commit/host/merge) codified in §6 + html-artifacts.md; marketplace versioning/dependencies/install-mode/priority codified in §11 + publish-contract.md; level-1 ritual UX codified in kb-setup Step 7d + command-reference.md triage scan. AGENTS rules unchanged in semantics | Concept/spec-gap audit |
| 2026-05-15 | Bumped AGENTS version to 0.11 to track the v6.1.0 release-readiness closeout: `[Unreleased]` content moved into the v6.1.0 release, current roadmap/journey surfaces are documented as stable setup-proposed product-management flows, first-run acceptance covers delivery/operations and retros, and CI now guards manifest version drift. AGENTS rules unchanged in semantics | Release-readiness audit |
| 2026-05-14 | Bumped AGENTS version to 0.10 to track the daily-reality role-coverage extension landing under `[Unreleased]`: new `docs/role-handbook.md`, new retro note variant (template + `/kb note retro` verb + REFERENCE §4 Note-format extension), workstream template enriched with status/owner/cadence/linked-delivery and shipment/milestone tables, and three new day-in-the-life scenes (PM/EM/on-call SRE). AGENTS rules unchanged in semantics | Daily-reality gap audit across software-company roles |
| 2026-05-10 | v6.0.0 release alignment — bumped AGENTS version to 0.9 to track the v5 adoption-arc closeout (canonical `/kb brief`, `/kb spec`, `/kb release`, `/kb incident` verbs; REFERENCE ↔ template format alignment for the four delivery/operations artifacts; removal of residual fixed-ladder L1/L2/L3/L4 vocabulary; year-nested archive and weekly-summary path corrections; five missing changelog sections added). AGENTS rules unchanged in semantics | v6.0.0 adoption + daily-usage gap audit |
| 2026-04-30 | v5.5.1 release alignment — bumped AGENTS version to 0.8 to track the HTML landing-page value-prop correction. AGENTS rules unchanged in semantics | HTML value-prop correction |
| 2026-04-30 | v5.5.0 release alignment — bumped AGENTS version to 0.7 to track the product-management roadmap/journey surface integration. AGENTS rules unchanged in semantics | Product-management surface integration |
| 2026-04-29 | v5.4.2 release alignment — bumped AGENTS version to 0.6 to track the draft-skill discoverability fix (the packaged `/kb` dispatcher now routes `/kb roadmap` and `/kb journeys`; kb-management's trigger surface picks up roadmap/journey keywords; the visual landing page advertises the two opt-in subcommands). AGENTS rules unchanged in semantics | v5.4.2 draft-skill discoverability fix |
| 2026-04-25 | v5.2.0 release alignment — bumped AGENTS version to 0.5 to track the kb-management trigger expansion (skill now fires on natural-language feature keywords, not only on `/kb`) and the kb-setup goal-oriented question-flow rework. AGENTS rules unchanged in semantics | v5.2.0 trigger + setup rework |
| 2026-04-25 | Concept audit follow-up: bumped AGENTS version to 0.4 and recorded the missing 4.1.0 / 5.0.0 / 5.1.0 / 5.1.1 alignment entries that had been skipped here, so the file reflects the framework's current 5.1.x state instead of stopping at 4.0.0 | Concept-audit drift correction |
| 2026-04-25 | v5.1.0 release alignment — public command surface and migration-helper docs now match the 5.1.0 release; AGENTS file unchanged in semantics, only carrying the missing changelog row | v5.1.0 follow-up closeout |
| 2026-04-25 | v5.0.0 release alignment — flexible layer graph became the canonical model; AGENTS rules unchanged, but the surrounding spec they reference now uses layer/scope/parent terminology | v5.0.0 flexible layer model |
| 2026-04-25 | v4.1.0 release alignment — generic marketplace extension contract added to the spec; AGENTS rules unchanged, recorded here for traceability | v4.1.0 marketplace extension |
| 2026-04-25 | v4.0.0 release alignment — kb-setup skill caught up from 3.4.4 to 4.0.0, README status row updated from v3.4.0 to v4.0.0, manifests and skill/agent versions all set to 4.0.0 | v4.0.0 release alignment |
| 2026-04-25 | Added an explicit artifact-control rule: external-read preflights and post-generation QA sweeps must stay visible in repo instructions; bumped AGENTS version to 0.2 | Follow-up to the v3.5.0 artifact contract update |
| 2026-04-22 | Updated behavioral-spec paths to `plugins/kb/` and added the collaboration guide to the mandatory shared-workspace reading list | Doc drift review |
| 2026-04-18 | Initial file | Spec bootstrapping |
| 2026-04-18 | Added blank lines around `### N.` rule headings and rule 3's bullet list (markdownlint MD022/MD032); no semantic change | CI fix |
