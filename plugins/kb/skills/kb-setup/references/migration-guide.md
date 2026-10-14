# Migration Guide — kb-setup

For users who already have a knowledge base in another layout.

## Detection

`/kb setup` detects migration candidates:

- Existing git repo in any declared layer path.
- Presence of `topics/`, `findings/`, `decisions/`, `tasks/`, or similar subdirs.
- No `.kb-config/layers.yaml` at the root.

Two dedicated helpers cover the mechanical parts of the migration:

- `/kb migrate layer-model` — preview or apply the `.kb-config/layers.yaml` conversion from the retired fixed ladder to the list-based graph.
- `/kb migrate archives` — preview or apply the year-based archive moves.

## Plan

Produce a **diff** before applying:

- Directories to create (missing required paths).
- Files to rename (e.g., `todo.md` → split into `_kb-tasks/focus.md` + `_kb-tasks/backlog.md`).
- Files to restructure (e.g., single `decisions/open.md` → individual `_kb-decisions/D-*.md` files).
- Files to move to `_kb-references/legacy/` (material that doesn't fit).

## Apply

Only after user confirmation:

- Use `git mv` to preserve history.
- Use `git commit` per logical chunk (not one giant commit).
- Never delete.

## Common migrations

### Single `todo.md` → split

```
Before: todo.md (mixed open + done)
After:
  _kb-tasks/focus.md
  _kb-tasks/backlog.md
  _kb-tasks/archive/YYYY/MM.md   (done items grouped by completion year/month)
```

### Single `decisions.md` / `decisions/open.md` → individual files

```
Before: decisions/open.md (multiple decisions in one file)
After: _kb-decisions/D-YYYY-MM-DD-<slug>.md  (one per decision)
```

### Flat `_kb-inputs/digested/` → dated

```
Before: _kb-inputs/digested/*.md
After: _kb-inputs/digested/YYYY/MM/*.md (grouped by processed year and month)
```

### Fixed ladder → layer graph

```
Before: layers.personal / layers.teams / layers.org-unit / layers.marketplace / layers.company
After:  workspace.anchor-layer + layers[] list with scope, role, parent, path, and per-layer features
```

### Missing `_kb-workstreams/`

Prompt the user for 1–5 parallel tracks. Create files.

### Missing foundation files

Create `me.md`, `context.md`, `stakeholders.md`, `sources.md` from templates and ask user to fill in minimum required fields.

### Pre-7.0 tracker connections

Run `/kb audit` rule K17 or rerun `/kb setup`. For an unambiguous live adapter missing `connections.trackers[].capabilities`, preview the normalized capability list and any legacy roadmap `auth-env` name as a diff on the canonical connection. A legacy roadmap tracker with write capabilities also creates or selects its canonical `connections.trackers[]` entry and, when absent, adds `primitive-storage.roadmap-items` ownership in that same diff. Ambiguous destinations and conflicting ownership require an explicit user choice and are not overwritten. Persist only after confirmation. Explicit empty lists and generic, export-backed, or custom adapters stay read-only until the user verifies their implemented operations and authentication source.

## After migration

- Commit with message `chore(kb-setup): migrate to agentic-kb v<version> layout`.
- Run `/kb audit` to flag stale or ambiguous content.
- Run `/kb start-day` to verify the briefing is non-empty.
