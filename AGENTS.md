# Agent Instructions

This file is read first by any AI agent (and any human) working in this repository. It defines the ground rules. Layer-specific documents in `docs/` extend these rules — they never override them.

This repo is a **specification**, not a product. Work done here is documentation work: precise, versioned, cross-referenced. Code exists only to validate docs (CI).

---

## Rules

### 1. Spec-first, implementation-later

This repo defines *what* the system does and *how* it is shaped. It does not build it. Implementations live in companion repos. If a PR here proposes runtime code beyond CI tooling, reject it.

### 2. No vendor lock-in

The spec must remain IDE-agnostic, harness-agnostic, and vendor-neutral. Examples are welcome. Hardcoded product names, company names, or proprietary service references are not. The CI guards against a small list of forbidden terms; reviewers guard against the rest.

### 3. Git is the change record

Docs, skills, agents and templates carry no version numbers, dates, or changelog sections, and neither do the KB artifacts the spec defines. Git history and PR review are the per-file record; CI (`scripts/check_no_file_versioning.py`) rejects reintroduced versioning.

- Use a Conventional Commit PR title (`fix:`, `docs:`, `feat:`, `feat!:` for breaking spec changes). PRs are squash-merged and the title becomes the release note.
- Never edit the root `VERSION`, the plugin manifest versions, or the root `CHANGELOG.md` in a change PR. release-please generates them in its release PR.

### 4. Cross-references stay live

Every link in a spec doc must resolve. CI enforces this via `lychee` (external) and `scripts/check_consistency.py` (internal). Broken links = red CI = not done.

### 5. Lean over exhaustive

A spec section that says the same thing three times is worse than one that says it once. When in doubt, cut. Examples belong in `docs/examples/`, not inline.

### 6. CI green is the definition of done

No PR is ready for review until CI is green. A red `main` is the top-priority fix for maintainers. Never skip hooks; never merge with failing checks.

### 7. Commit, push, keep the tree clean

Agents and contributors must not leave work stranded locally. Every completed unit of work ends in a commit on the target branch. No dirty repos, no stale branches. Agents should offer to commit/push/PR after substantive changes — and only push if CI is expected to stay green.

### 8. Additive over destructive

When in doubt, add a section rather than rewrite one. The PR description makes intent traceable. Deletions require a justification in the PR description.

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
7. Leave the root `CHANGELOG.md` and `VERSION` to the release-please PR.
8. Run local checks (see [CONTRIBUTING.md](CONTRIBUTING.md)).
9. Open a PR with a description that answers: what changed, why, what it breaks (if anything).
