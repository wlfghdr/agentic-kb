# Migration Guide — kb-setup

For users who already have a knowledge base in another layout.

## Detection

`/kb setup` detects migration candidates:

- Existing git repo in the declared personal KB path.
- Presence of `topics/`, `findings/`, `decisions/`, `todo/`, or similar subdirs.
- No `.kb-config.yaml` at the root.

## Plan

Produce a **diff** before applying:

- Directories to create (missing required paths).
- Files to rename (e.g., `todo.md` → split into `todo/focus.md` + `todo/backlog.md`).
- Files to restructure (e.g., single `decisions/open.md` → individual `decisions/active/D-*.md` files).
- Files to move to `references/legacy/` (material that doesn't fit).

## Apply

Only after user confirmation:

- Use `git mv` to preserve history.
- Use `git commit` per logical chunk (not one giant commit).
- Append to `CHANGELOG.md` if the migrated KB has one.
- Never delete.

## Common migrations

### Single `todo.md` → split

```
Before: todo.md (mixed open + done)
After:
  todo/focus.md
  todo/backlog.md
  todo/archive/YYYY-MM.md   (done items grouped by completion month)
```

### Single `decisions.md` / `decisions/open.md` → individual files

```
Before: decisions/open.md (multiple decisions in one file)
After: decisions/active/D-YYYY-MM-DD-<slug>.md  (one per decision)
```

### Flat `inputs/digested/` → dated

```
Before: inputs/digested/*.md
After: inputs/digested/YYYY-MM/*.md (grouped by processed month)
```

### Missing `workstreams/`

Prompt the user for 1–5 parallel tracks. Create files.

### Missing foundation files

Create `me.md`, `context.md`, `stakeholders.md`, `sources.md` from templates and ask user to fill in minimum required fields.

## After migration

- Commit with message `chore(kb-setup): migrate to agentic-kb v<version> layout`.
- Run `/kb audit` to flag stale or ambiguous content.
- Run `/kb start-day` to verify the briefing is non-empty.
