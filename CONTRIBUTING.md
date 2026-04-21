# Contributing to agentic-kb

Thanks for your interest! This repo is a **specification**, not yet an implementation. Contributions are welcome in the following forms:

- **Issues** — clarifications, gaps, contradictions, missing pieces in the spec.
- **Pull Requests** — edits to docs, new examples, CI improvements, additional spec rules.
- **Discussions** — open questions, design alternatives, use cases we haven't anticipated.

## Before You Start

Read:

1. [README.md](README.md) — the one-page orientation.
2. [AGENTS.md](AGENTS.md) — rules for both humans and AI agents working in this repo.
3. [docs/REFERENCE.md](docs/REFERENCE.md) — architecture, layout, formats.
4. [docs/roadmap.md](docs/roadmap.md) — what's open, what's intentionally deferred.
5. [docs/collaboration.md](docs/collaboration.md) — required when a change affects shared layers, handoffs, or multi-user behavior.

## Rules for Changes

### Every doc change must…

1. **Update the doc's own changelog** — each long-lived spec/concept file has a `## Changelog` section at the bottom. Append a newest-first entry: `| YYYY-MM-DD | what changed | source |`.
2. **Update `CHANGELOG.md`** — add an `Added`/`Changed`/`Fixed`/`Removed` line under `## [Unreleased]`.
3. **Bump version fields where applicable** — if a spec rule changes semantics, bump the doc's version. If a command surface changes, bump the root `VERSION` (PATCH for prose, MINOR for new rules, MAJOR for breaking).
4. **Pass CI** — markdown lint, dead-link check, consistency check. A red PR is not ready for review (see [AGENTS.md](AGENTS.md) rule 6).
5. **No domain lock-in** — this spec is intentionally IDE-agnostic, harness-agnostic, and vendor-neutral. Examples are welcome, but the rules must not hardcode any specific product, company, or tool.

### PR checklist

- [ ] Spec doc changelog updated (if a spec doc changed)
- [ ] Root `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] `VERSION` bumped if the change is user-visible
- [ ] `make check` passes locally (or CI green)
- [ ] No vendor-specific terms added to spec docs (see `scripts/check_consistency.py` guard list)

## Proposing Bigger Changes

For anything that touches the command surface, the workspace layout, or the file formats, open a discussion first. These are the parts that implementations depend on — breaking them is a MAJOR bump.

If a change alters shared-workspace behavior, human approval boundaries, or promotion/digest semantics, update [docs/collaboration.md](docs/collaboration.md) in the same PR.

For the reference implementation (skills + agent), most work will happen in a companion marketplace repo. See [`docs/REFERENCE.md`](docs/REFERENCE.md) §9 Marketplace — PRs to the companion repo need to reference the spec version they target.

## Running Checks Locally

```bash
# Markdown lint
npx markdownlint-cli2 "docs/**/*.md" "*.md"

# Dead link check
lychee --config .lychee.toml .

# Consistency + version sync + vendor-neutrality guard
python3 scripts/check_consistency.py
```

CI runs all three on every push and pull request.

## Pre-push Hook

Install a local pre-push hook that runs the same validation CI runs — this catches vendor-specific leaks, broken links, and drift before they ever reach the remote:

```bash
./scripts/install-hooks.sh
```

## Vendor-Neutrality Blocklist

This spec is vendor-neutral. The consistency check reads an optional `.forbidden-terms.txt` at the repo root (gitignored) — one case-insensitive term per line, `#` for comments. Maintainers and forks can layer their own internal vocabulary there without that vocabulary ever appearing in the public spec. If `check_consistency.py` fails with a `FORBIDDEN term` error, either rephrase the doc in vendor-neutral language or justify adding an exemption.

The pre-push hook enforces this before every push. Emergency bypass: `git push --no-verify` (use sparingly).

## Code of Conduct

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Be kind, be precise, be honest about what you don't know.
