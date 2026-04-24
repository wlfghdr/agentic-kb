# First-Run Acceptance Path

> **Version:** 0.1 | **Last updated:** 2026-04-20

This document defines the canonical **first-run acceptance path** for `agentic-kb`.

Its purpose is not to explain every option. Its purpose is to answer one practical question:

**Can a human or team lead verify, step by step, that a fresh user reached the same working contract as everyone else?**

If the answer is not clearly yes, onboarding is not good enough yet.

## What this acceptance path covers

This path starts at **nothing installed** and ends at the first useful `/kb` outputs in a newly initialized workspace.

It is intentionally narrow:

- one user,
- one personal KB,
- no team or org KB yet,
- one documented harness path at a time,
- manual automation level,
- builtin HTML styling.

That narrowness is a feature. A team rollout needs one deterministic baseline before it can safely branch into variants.

## Contract: install vs. init

The first-run contract has exactly two phases.

### Phase A — Install into the harness

Goal: make `/kb setup` callable.

This phase ends when the harness exposes the `kb` plugin or the equivalent installed skills.

### Phase B — Initialize the workspace

Goal: create a valid KB workspace and prove it produces the expected first outputs.

This phase ends when `/kb status` and `/kb start-day` succeed in the new workspace.

## Acceptance baseline

Use this baseline unless a test explicitly covers another variant.

| Item | Baseline |
|------|----------|
| User name | `alice` |
| Workspace root | `<workspace>/demo-agentic-kb` |
| Personal KB name | `alice-kb` |
| Themes | `caching`, `reliability`, `observability` |
| Workstream count | 1 |
| Team KB | skipped |
| Org KB | skipped |
| Marketplace clone for authoring | skipped |
| Automation | level 1 |
| HTML styling | builtin |

## Harness-specific install end conditions

### Claude Code

Install path:

```text
/plugin marketplace add https://github.com/wlfghdr/agentic-kb
/plugin install kb@agentic-kb
```

Install phase is accepted when:

- `/kb setup` is available,
- the harness exposes the installed plugin without restart ambiguity,
- the user can invoke `/kb setup` from the intended workspace.

### VS Code Copilot Chat

Install path:

- add `wlfghdr/agentic-kb` to `chat.plugins.marketplaces`,
- install the plugin from the Extensions view.

Install phase is accepted when:

- `/kb setup` is available in Copilot Chat,
- the plugin is visible as installed,
- the same command surface is available after reopening the workspace.

### OpenCode

Install path:

```bash
git clone https://github.com/wlfghdr/agentic-kb
cd agentic-kb
scripts/install --target opencode --global
```

Install phase is accepted when:

- the skills are discoverable by OpenCode,
- `/kb setup` is available in the target workspace.

### Gemini CLI

Install path:

```bash
git clone https://github.com/wlfghdr/agentic-kb
cd agentic-kb
scripts/install --target gemini --global
```

Install phase is accepted when:

- `.gemini/commands/kb.toml` or `~/.gemini/commands/kb.toml` exists,
- `/kb setup` is available in Gemini CLI,
- the generated command body does not contain VS Code-only setup guidance.

### Kiro IDE

Install path:

```bash
git clone https://github.com/wlfghdr/agentic-kb
cd agentic-kb
scripts/install --target kiro --global
```

Install phase is accepted when:

- `.kiro/skills/kb/SKILL.md` or `~/.kiro/skills/kb/SKILL.md` exists,
- `/kb setup` is available from the Kiro slash menu,
- the installed skill matches the documented skill format (`name` + `description` frontmatter).

### Codex CLI

Install path:

- clone this repo and run `scripts/install --target codex` (repo-local) or `--global`
- in Codex CLI, operate from the initialized workspace so `AGENTS.md` and `.agents/skills/kb/SKILL.md` are in scope

Install phase is accepted when:

- `.agents/skills/kb/SKILL.md` or `~/.agents/skills/kb/SKILL.md` exists,
- Codex can operate against the same repo-local KB files without path/layout drift,
- the docs call out that Codex uses `AGENTS.md` plus the skill picker or `$kb`, not a custom `/kb` slash command.

## Canonical first-run scenario

## Step 1 — Preconditions

Required before starting:

- `git` installed,
- one first-class supported harness installed, or a Codex CLI workflow attached to an already initialized workspace,
- write access to the target workspace path.

Recommended:

- `gh` installed,
- authenticated git remote access.

Expected result:

- missing required tools stop the flow early with a clear fix,
- optional tools warn, but do not invalidate the baseline.

## Step 2 — Install phase

Run the harness-specific install path.

Expected result:

- `/kb setup` becomes callable,
- the user does not need to guess whether install succeeded.

Failure if:

- `/kb setup` is unavailable,
- the docs imply setup can proceed anyway,
- the user must infer success from hidden files alone.

## Step 3 — Start `/kb setup`

From the intended workspace root:

```text
/kb setup
```

Expected result:

- the skill clearly enters initialization mode,
- it does not re-explain plugin installation as if the user were still in Phase A,
- it asks setup questions in a stable order.

## Step 4 — Answer the baseline questions

Use these answers:

| Question | Baseline answer |
|----------|-----------------|
| Your name | `alice` |
| Role and themes | `engineer on distributed systems — caching, reliability, observability` |
| Vision, mission, goals | short text or skip |
| Workspace root | current directory / `<workspace>/demo-agentic-kb` |
| Personal KB | create new, `alice-kb`, no remote |
| Team KB | skip |
| Org KB | skip |
| Marketplace | skip |
| Workstreams | `platform-signals` |
| IDE targets | current harness only |
| Integrations | skip |
| Automation | `1` |
| HTML styling | `builtin` |

Expected result:

- every answer maps to a concrete artifact or config effect,
- the skill does not ask hidden prerequisite questions later,
- the user can complete setup without already knowing the internal file model.

## Step 5 — Scaffold verification

After setup finishes, the workspace should contain at least:

```text
demo-agentic-kb/
├── AGENTS.md
├── CLAUDE.md
└── alice-kb/
    ├── AGENTS.md
    ├── README.md
    ├── .kb-config/
    │   ├── layers.yaml
    │   ├── automation.yaml
    │   └── artifacts.yaml
    ├── _kb-inputs/
    ├── _kb-references/
    │   ├── foundation/
    │   ├── findings/
    │   ├── topics/
    │   └── reports/
    ├── _kb-ideas/
    ├── _kb-decisions/
    ├── _kb-tasks/
    ├── _kb-workstreams/
    ├── .kb-log/
    ├── .nojekyll
    └── index.html
```

Acceptance checks:

- no literal `{{PLACEHOLDER}}` tokens remain (except inside `_kb-references/templates/presentation-template.html` or its branded sibling — those placeholders are filled per-artifact by `/kb present`, see `kb-setup/SKILL.md` §Post-write check),
- `.kb-config/layers.yaml` exists,
- `_kb-tasks/focus.md` exists,
- at least one workstream file exists,
- at least one topic stub exists,
- `index.html` exists.

Failure if any of these are missing without explicit explanation.

## Step 6 — First status call

Run:

```text
/kb status
```

Expected output characteristics:

- clearly read-only,
- reports clean initial state,
- points to the correct personal KB,
- suggests the next useful actions.

A good minimal result looks like:

```text
What I did: checked your KB status.
Where it went: read alice-kb/.kb-config/layers.yaml, alice-kb/_kb-tasks/focus.md, alice-kb/.kb-log/...
Gate notes: n/a.
Suggested next steps:
- Run /kb start-day
- Capture a first source with /kb <URL-or-text>
```

## Step 7 — First briefing

Run:

```text
/kb start-day
```

Expected output characteristics:

- clearly read-only,
- no invented work,
- no false claims about pending items,
- references the empty initial focus/decision state,
- suggests a concrete first capture or task.

A good minimal result looks like:

```text
What I did: briefed you for the day.
Where it went: read alice-kb/_kb-tasks/focus.md, alice-kb/_kb-decisions/, alice-kb/.kb-log/<today>.log.
Gate notes: n/a.
Suggested next steps:
- Capture something with /kb <URL-or-text>
- Add your first focus item with /kb todo "..."
```

## Step 8 — First capture

Run:

```text
/kb https://example.com/article-about-caches
```

Expected result:

- the agent states whether it fetched external content,
- it applies the gate,
- it writes a finding,
- it may update a topic,
- it logs the operation,
- it proposes sensible next actions.

Minimum expected artifact outcomes:

- one new file in `_kb-references/findings/`,
- possible update to one topic in `_kb-references/topics/`,
- one new `.kb-log/<date>.log` entry,
- archived or marked-digested input if applicable.

## Optional Step 9 — Lean roadmap proof

If the adopter also wants to prove the roadmap surface, use the narrowest path first:

1. export a small Jira or GitHub issue set to markdown,
2. bind those export directories through `roadmap.issue-trackers[]` with `adapter: ticket-export-markdown`,
3. run the roadmap pilot against the KB root,
4. verify that `_kb-roadmaps/<scope>/roadmap-<date>.md|.html|.json` is written,
5. confirm at least one correlated item appears in the JSON sidecar before enabling live tracker adapters.

Acceptance checks:

- no tracker tokens or auth are required for the first proof run,
- the JSON sidecar shows the expected `correlated` vs `single_tracker` counts,
- the HTML artifact is self-contained,
- the user can inspect the source exports and the generated roadmap side by side.

## Team lead verification checklist

A team lead can treat onboarding as accepted only if all of these are true:

- every user can reach `/kb setup` without ad hoc rescue steps,
- every user ends up with the same baseline folder contract,
- every user gets the same first useful `/kb status` and `/kb start-day` behavior,
- no user needed hidden knowledge about install vs. init,
- the first capture path makes external fetch behavior explicit,
- the resulting workspace is understandable by another human reviewer.

If any of these fail, the rollout is not deterministic enough yet.

## Failure signals that must create follow-up work

Create or reopen an issue if any of these occur:

- `/kb setup` exists, but the install path is still ambiguous,
- the scaffold differs by harness in undocumented ways,
- setup succeeds, but `/kb status` or `/kb start-day` is structurally wrong,
- placeholder tokens survive setup,
- the first capture path hides whether external material was fetched,
- a second human cannot quickly verify the same contract from the produced workspace.

## Related

- [README.md](../README.md)
- [REFERENCE.md](./REFERENCE.md)
- [first-hour.md](./examples/first-hour.md)
- [plugins/kb/skills/kb-setup/SKILL.md](../plugins/kb/skills/kb-setup/SKILL.md)
- [plugins/kb/skills/kb-setup/references/setup-flow.md](../plugins/kb/skills/kb-setup/references/setup-flow.md)

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-24 | Added Gemini CLI and Kiro IDE install-phase acceptance checks, updated Codex CLI to the `.agents/skills/` workflow, and added an export-backed roadmap proof step | Harness and roadmap proof correction |
| 2026-04-22 | Exempted the presentation template placeholder scan from scaffold acceptance because those `{{…}}` markers are intentionally deferred for `/kb present` | Fixes #17 |
| 2026-04-22 | Added Codex CLI acceptance guidance and clarified the difference between first-class supported harnesses and compatible CLI workflows | Compatibility expansion |
| 2026-04-20 | Initial deterministic first-run acceptance path for onboarding verification | Issue #6 |
