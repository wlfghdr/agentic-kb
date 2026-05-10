---
applyTo: "**/.kb-config/**,**/_kb-inputs/**,**/_kb-references/**,**/_kb-notes/**,**/_kb-decisions/**,**/_kb-tasks/**,**/_kb-workstreams/**,**/.kb-log/**"
description: Routing rules for all KB operations
---

# KB Routing Rules

Use these rules when any `/kb` command is invoked.

## Layer detection

Read `.kb-config/layers.yaml` in the anchor layer root. It declares:

- `workspace.anchor-layer`
- `workspace.aliases`
- `layers[]` — named layer entries with `scope`, `role`, `parent`, `path`, and optional `connections` / `marketplace`

Given a file path, determine the layer by matching the path against the declared repo paths.

## Action inference

| User input | Action |
|---|---|
| URL / pasted text | Capture to the anchor layer |
| Path inside a declared layer repo | Run the operation in that layer context |
| Explicit layer name or alias | Disambiguates the target layer |
| Explicit keyword (`publish`, `connections`, `progress`) | Disambiguates the flow |

## Workstream routing

Read the anchor layer entry in `.kb-config/layers.yaml`. Its `workstreams[]` entries each have `name` and `themes`. Match captured content against themes to pick the workstream. If multiple match, flag a cross-workstream connection.

## Output contract

Every response ends with 1–3 concrete next-step suggestions.
