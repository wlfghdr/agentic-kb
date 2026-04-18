# Workspace Layout

> **Version:** 0.1 | **Last updated:** 2026-04-18

This spec defines the on-disk layout implementations MUST scaffold. Users who follow this layout get the full command surface without extra configuration.

## Workspace Root

A workspace is the parent directory that contains all KB repos and harness configuration.

```
my-workspace/                       # workspace root (VS Code "workspace" / repo parent)
├── AGENTS.md                       # master index (all repos, keyword lookup, rules)
├── CLAUDE.md → AGENTS.md           # symlink for Claude Code compatibility
├── .github/
│   ├── prompts/
│   │   └── kb.prompt.md            # single /kb command entry point
│   └── instructions/
│       └── kb.instructions.md      # routing rules for all KB operations
├── .claude/                        # Claude Code: skills/ agents/ commands/ settings
├── .opencode/                      # OpenCode: skills/ agents/ commands/ config
├── my-kb/                          # L1 Personal KB — REQUIRED
├── team-kb/                        # L2 Team KB — optional, multiple allowed
├── org-unit-kb/                    # L3 Org-Unit KB — optional
├── agentic-kb-marketplace/         # L4 Marketplace — optional
└── [other project repos]
```

### AGENTS.md at the Root

The workspace root `AGENTS.md` is the **master index**. It lists every repo with a one-line description, points to each repo's own `AGENTS.md`, and contains a keyword lookup table that tells agents which file to read for which topic.

**`CLAUDE.md` is a symlink to `AGENTS.md`.** This keeps one canonical file while being discoverable by Claude Code (which looks for `CLAUDE.md`). On Windows, where symlinks require elevation, implementations MAY create `CLAUDE.md` as a copy plus a build-time consistency check.

### Harness Directories

| Directory | Purpose |
|-----------|---------|
| `.github/skills/` | VS Code Copilot Agent Skills (cross-agent compatible) |
| `.github/prompts/` | VS Code Copilot prompt files (slash commands) |
| `.github/instructions/` | VS Code Copilot scoped instructions |
| `.github/agents/` | VS Code Copilot custom agent personas (`*.agent.md`) |
| `.claude/skills|agents|commands/` | Claude Code artifacts |
| `.opencode/skills|agents|commands/` | OpenCode artifacts |

The `/kb setup` skill creates all three by default. Users can delete any they don't use.

## Personal KB (L1)

```
my-kb/
├── AGENTS.md
├── README.md
├── .kb-config.yaml                 # layer configuration (see 02-architecture.md)
├── .kb-automation.yaml             # automation level + schedules
│
├── inputs/                         # THE INBOX — drop anything here
│   └── digested/                   # auto-archive after processing
│       ├── 2026-04/
│       └── 2026-03/
│
├── references/
│   ├── topics/                     # living positions (see 03-memory-model.md)
│   ├── findings/                   # dated snapshots
│   ├── foundation/                 # identity
│   │   ├── me.md
│   │   ├── context.md
│   │   ├── sources.md              # external link index (see 10-external-links.md)
│   │   ├── stakeholders.md
│   │   └── naming.md               # optional
│   ├── legacy/                     # archived topics (after audit)
│   └── reports/                    # optional: generated HTML artifacts
│
├── decisions/
│   ├── active/                     # D-YYYY-MM-DD-slug.md
│   └── archive/                    # resolved + superseded
│
├── todo/
│   ├── focus.md                    # max 3 items — always in context
│   ├── backlog.md
│   └── archive/
│       └── YYYY-MM.md
│
├── log/
│   ├── YYYY-MM-DD.log              # today
│   └── YYYY-MM-DD.log              # yesterday
│                                   # older logs remain but are not loaded
│
└── workstreams/
    ├── <name>.md
    └── legacy/                     # archived workstreams
```

### The Inbox — The Single Most Important Thing

> **`inputs/` is the inbox. Drop anything there. The agent handles the rest.**

Text files, PDFs, screenshots, URLs pasted into a `.md` file, rough meeting notes, copy-pasted Slack messages — anything. No formatting required. No structure needed.

What happens next (see [../concept/09-flows.md](../concept/09-flows.md) for the flow detail):

1. `/kb review` scans `inputs/` for unprocessed items.
2. The agent reads each item and applies the [evaluation gate](../concept/08-evaluation-gate.md).
3. High-signal material → distilled into `references/findings/` or integrated into `references/topics/`.
4. If the input implies a decision point → creates a file in `decisions/active/`.
5. The original input → moved to `inputs/digested/YYYY-MM/`.
6. TODOs extracted → added to `todo/backlog.md`.
7. Agent routes to the correct workstream.
8. Agent suggests next steps.

## Team KB (L2)

```
team-kb/
├── AGENTS.md
├── README.md
├── decisions/
│   ├── active/                     # team decisions with RACIs
│   └── archive/
├── todo/
│   ├── focus.md                    # team focus with RACIs
│   └── backlog.md
├── log/
├── alice/                          # one directory per contributor
│   ├── inputs/
│   │   └── digested/
│   │       └── 2026-04/
│   └── outputs/
│       ├── topics/                 # living positions
│       └── findings/               # dated snapshots
└── bob/ ...
```

Contributor output structure mirrors personal memory (topics + findings) — see [../concept/03-memory-model.md](../concept/03-memory-model.md).

## Org-Unit KB (L3)

```
org-unit-kb/
├── AGENTS.md
├── README.md
├── decisions/
│   ├── active/
│   └── archive/
├── todo/
│   ├── focus.md
│   └── backlog.md
├── workstreams/                    # org-level workstream coordination
└── log/
```

Org-unit KBs don't have contributor directories — they aggregate from team KBs via promote flows.

## Marketplace (L4)

See [`marketplace-and-skills.md`](marketplace-and-skills.md) for the required package layout.

## Required Files per KB

| Layer | Required files |
|-------|---------------|
| L1 Personal | `AGENTS.md`, `README.md`, `.kb-config.yaml`, `inputs/`, `references/{topics,findings,foundation}/`, `decisions/active/`, `todo/focus.md`, `log/` |
| L2 Team | `AGENTS.md`, `README.md`, `decisions/active/`, `todo/focus.md`, `log/`, per-contributor `inputs/outputs/` |
| L3 Org-Unit | `AGENTS.md`, `README.md`, `decisions/active/`, `todo/focus.md`, `workstreams/`, `log/` |
| Workspace root | `AGENTS.md`, `CLAUDE.md → AGENTS.md`, `.github/prompts/kb.prompt.md`, `.github/instructions/kb.instructions.md` |

`/kb setup` (see [setup.md](setup.md)) verifies these post-scaffold.

## Symlinks — Rules

- `CLAUDE.md → AGENTS.md` at workspace root AND at every KB repo root.
- No other symlinks are required by the spec. Implementations MAY add skill-directory symlinks; they MUST be documented in the harness section of the implementation's README.
- Symlinks should be relative (`ln -s AGENTS.md CLAUDE.md`), never absolute.

## What `/kb setup` Creates

The onboarding skill creates every file listed above from templates. See [setup.md](setup.md) for the full interactive flow and template sources.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §3 |
