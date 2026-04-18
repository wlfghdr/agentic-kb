# Agent Instructions

> **Version:** 0.1 | **Last updated:** 2026-04-18

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

### 9. Honor the layered doc structure
- `docs/concept/` — the "why" and "what". Stable, conceptual.
- `docs/spec/` — the "how". Precise, implementation-ready.
- `docs/examples/` — illustrative walkthroughs. Not normative.
- `docs/roadmap.md` — open items, explicitly unresolved.
- `docs/glossary.md` — authoritative terms.

Don't move content across these boundaries without a clear reason.

### 10. One canonical term per concept
If a concept has a term in `docs/glossary.md`, use that term everywhere. Don't invent synonyms mid-doc. If a better term is found, update the glossary and all references in the same PR.

---

## Before Starting Any Task

1. Read this file.
2. Read [README.md](README.md).
3. Identify which docs your change touches (`docs/concept/`, `docs/spec/`, or both).
4. Draft the change.
5. Update the per-file changelog, the root `CHANGELOG.md`, and `VERSION` if applicable.
6. Run local checks (see [CONTRIBUTING.md](CONTRIBUTING.md)).
7. Open a PR with a description that answers: what changed, why, what it breaks (if anything).

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial file | Spec bootstrapping |
