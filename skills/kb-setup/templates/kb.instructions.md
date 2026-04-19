---
applyTo: "**/.kb-config.yaml,**/.inputs/**,**/.references/**,**/.decisions/**,**/.tasks/**,**/workstreams/**,**/.kb-log/**"
description: Routing rules for all KB operations
---

# KB Routing Rules

Use these rules when any `/kb` command is invoked.

## Layer detection

Read `.kb-config.yaml` in the personal KB root. It declares:

- `layers.personal.path` — always `.`
- `layers.teams[]` — zero or more team KBs
- `layers.org-unit` — zero or one org-unit KB
- `layers.marketplace` — zero or one marketplace
- `layers.company` — zero or one company source list

Given a file path, determine the layer by matching the path against the declared repo paths.

## Action inference

| User input | Action |
|---|---|
| URL / pasted text | Capture to L1 |
| Path inside personal KB | L1 operation (review/update-topic/decide) |
| Path inside a team repo | L2 operation |
| Path inside an org-unit repo | L3 operation |
| Explicit keyword (`team`, `org`, `publish`) | Disambiguates |

## Workstream routing

Read `.kb-config.yaml → layers.personal.workstreams`. Each entry has `name` and `themes` (keyword list). Match captured content against themes to pick the workstream. If multiple match, flag cross-workstream connection.

## Output contract

Every response ends with 1–3 concrete next-step suggestions.
