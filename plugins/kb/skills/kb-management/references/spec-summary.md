# Spec Summary — for the kb-management skill

Condensed reference for the skill's runtime. For the full spec, see the `agentic-kb` repo's `docs/`.

## Layers

| L | Name | Required | Repo scope |
|---|------|----------|-----------|
| 1 | Personal | ✅ | one per user |
| 2 | Team | ❌ | shared team repo, contributor dirs |
| 3 | Org-Unit | ❌ | shared org-unit repo |
| 4 | Marketplace | ❌ | skills/agents/plugins repo |
| 5 | Company | ❌ | consumed top-down |

## Personal KB layout

```
my-kb/
├── .kb-config/
│   ├── layers.yaml
│   ├── automation.yaml
│   └── artifacts.yaml
├── _kb-inputs/
│   └── digested/YYYY-MM/
├── _kb-references/
│   ├── topics/              living, inline changelog
│   ├── findings/            YYYY-MM-DD-slug.md, immutable
│   ├── foundation/          me, context, vmg, sources, stakeholders, naming
│   ├── legacy/
│   └── reports/             generated HTML
├── _kb-decisions/
│   ├── active/              D-YYYY-MM-DD-slug.md
│   └── archive/
├── _kb-tasks/
│   ├── focus.md             max 6 items
│   ├── backlog.md
│   └── archive/YYYY-MM.md
├── .kb-log/YYYY-MM-DD.log
├── .kb-scripts/                 optional utility scripts
└── _kb-workstreams/<name>.md
```

## Team KB layout

```
team-kb/
├── _kb-decisions/{archive}/          RACIs required
├── _kb-tasks/{focus,backlog}.md        RACIs required
├── .kb-log/
├── <contributor>/
│   ├── _kb-inputs/digested/YYYY-MM/
│   └── _kb-references/{topics,findings}/
```

## Org-Unit KB layout

Same as team minus per-contributor dirs. Adds `_kb-workstreams/`.

## Marketplace layout

See `agentic-kb` spec `docs/REFERENCE.md` §9 Marketplace.

## Config file keys

### `.kb-config/layers.yaml`

```yaml
workspace:
  root: /path/to/workspace
  user: alice
  aliases: { kb: my-kb, tk: team-kb }

layers:
  personal:
    path: .
    workstreams:
      - { name: <string>, themes: [<keyword>...] }
  teams: [{ name, path, contributor-dir }]
  org-unit: { name, path }
  marketplace: { enabled, repo, path }
  company: { enabled, sources: [] }
```

### `.kb-config/automation.yaml`

```yaml
level: 1 | 2 | 3
schedules: { <ritual>: <cron-ish string> }
auto-promote: { enabled, confidence-threshold, require-evidence, exclude-topics }
commit-push: { auto-commit, auto-push, respect-branch-protection }
notifications: { channel: terminal|slack|email|none }
```

### `.kb-config/artifacts.yaml`

```yaml
styling:
  source: builtin | website | template
  reference-url: <string>
  reference-file: <path>
  themes: [light, dark]
  default-theme: auto | light | dark
watermark:
  enabled: true
  position: intro-slide | every-slide
  format: "v{version} · {date}"
  style: subtle | normal
appendix:
  changelog: true
  sources: true
  hidden-by-default: false
output:
  directory: _kb-references/reports
  filename-template: "{slug}-v{version}.html"
github-pages:
  enabled: false
  branch: gh-pages
  index-file: index.html
```

## Log line format

```
HH:MM:SSZ | <op> | <scope> | <target> | <details>
```

Ops: `capture`, `digest`, `publish`, `promote`, `update-topic`, `task-add`, `task-done`, `decide`, `decide-resolve`, `audit`, `report`, `presentation`, `skipped`, `install`, `ritual-*`, `automation-failure`, `correction`.

Scopes: `personal`, `team-kb`, `team-kb/<contrib>`, `org-unit`, `marketplace`, `personal→team`, `team→personal`, `personal→marketplace`, `workspace`.
