# Agent Instructions

> **Version:** 0.3 | **Last updated:** 2026-04-25

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

- append a row to that file's own `## Changelog` section,
- add a line under `## [Unreleased]` in the root `CHANGELOG.md`,
- bump the relevant version field if the change alters semantics (see [CHANGELOG.md](CHANGELOG.md) for PATCH/MINOR/MAJOR rules).

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
| 2026-04-25 | v4.0.0 release alignment — kb-setup skill caught up from 3.4.4 to 4.0.0, README status row updated from v3.4.0 to v4.0.0, manifests and skill/agent versions all set to 4.0.0 | v4.0.0 release alignment |
| 2026-04-25 | Added an explicit artifact-control rule: external-read preflights and post-generation QA sweeps must stay visible in repo instructions; bumped AGENTS version to 0.2 | Follow-up to the v3.5.0 artifact contract update |
| 2026-04-22 | Updated behavioral-spec paths to `plugins/kb/` and added the collaboration guide to the mandatory shared-workspace reading list | Doc drift review |
| 2026-04-18 | Initial file | Spec bootstrapping |
| 2026-04-18 | Added blank lines around `### N.` rule headings and rule 3's bullet list (markdownlint MD022/MD032); no semantic change | CI fix |
