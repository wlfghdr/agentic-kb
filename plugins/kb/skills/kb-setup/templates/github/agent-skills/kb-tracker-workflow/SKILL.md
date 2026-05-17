---
name: kb-tracker-workflow
description: Operate tracker-backed KB primitives using the local .kb-config/layers.yaml primitive-storage and connections.trackers settings. Use for intake, decisions, tasks, feature requests, roadmap items, tracker audits, and file-to-tracker promotion.
version: 1.0.0
triggers:
  - "tracker-backed primitive"
  - "tracker intake"
  - "decision issue"
  - "task issue"
  - "feature intake"
  - "roadmap item"
  - "pull request"
  - "PR"
  - "github project"
  - "issue type"
  - "branch protection"
tools:
  - read_file
  - grep_search
  - file_search
  - run_in_terminal
  - vscode_askQuestions
author: agentic-kb setup
license: Apache-2.0
---

# Skill: KB Tracker Workflow

This repo uses tracker-backed KB primitives and the generic GitHub governance profile. The tracker is the canonical operational home for the primitive families declared in `.kb-config/layers.yaml` under `primitive-storage`.

This skill is the local operating manual for issues, projects, labels, PRs, and tracker-backed KB artifacts. It keeps agents aligned with the repository's GitHub rules before CI has to reject a PR.

## Source-of-Truth Boundaries

- KB files own synthesis, evidence, reports, durable context, and file-backed primitives.
- Tracker items own operational state for every primitive family configured as `mode: tracker`.
- Hybrid primitives start in files and move to tracker ownership when they cross the configured sharing boundary.
- Pull requests own proposed repository changes and must link the issue or tracker item that explains why the change exists.
- Delivery systems outside GitHub may own execution state; link to them instead of copying their status into GitHub.

Never leave two active records pretending to own the same decision, task, feature, or roadmap item.

## Required Preflight

Before creating or updating any tracker item:

1. Read `.kb-config/layers.yaml`.
2. Find the active layer.
3. Read `connections.trackers[]` and `primitive-storage`.
4. Identify whether the requested primitive is `files`, `tracker`, or `hybrid`.
5. Search existing KB files and tracker items for duplicates when tools are available.
6. Show the proposed mutation and wait for explicit confirmation.

Before changing repository files for non-trivial work:

1. Identify the linked issue or explain the small exception.
2. Check native issue type, project membership, milestone, assignee, and status when the repo config requires them.
3. Check parent/sub-issue placement when workstream parents are configured.
4. Confirm the PR will use a closing keyword when it completes the issue.
5. Identify validation commands and governed-doc or changelog impact before editing.

## Classification

Classify every incoming item before mutating anything.

| If it is | Use |
|---|---|
| Observed user, customer, market, system, or internal signal | Feedback |
| Early idea that needs validation or shaping | Idea |
| Choice, trade-off, or alignment point | Decision |
| Follow-up work with owner/status/review visibility | Task |
| Defect, regression, or broken expected behavior | Bug |
| Product, service, process, or capability request | Feature |
| Time/phase/commitment planning item | Roadmap Item |
| Documentation, template, or knowledge artifact change | Content Update |
| Repository rule, CI, template, branch protection, label, or agent instruction change | Governance Change |

If the classification is unclear, ask for the missing signal instead of creating a broad issue.

## Required Shape for GitHub Work

For every non-trivial feature, bugfix, docs update, process fix, or refactor:

1. Start with a GitHub issue unless the PR keeps the configured small-exception marker.
2. Use native issue Type or the configured issue-form kind.
3. Add the issue to the configured GitHub Project when one exists.
4. Set assignee and project Status to `In Progress` when work starts, if those fields exist.
5. Attach the issue to its workstream parent or parent issue when the repo uses parent/sub-issues.
6. Open a PR that references the issue with `Closes #NNN`, `Fixes #NNN`, `Refs #NNN`, or the configured equivalent.
7. Keep the PR scope aligned with the issue; update the issue or create a follow-up when scope changes.
8. Run and report validation before handoff.
9. After merge, confirm the issue closed and project status moved to `Done` when automation does not do it.

Do not begin implementation while required project membership, owner, status, or parent placement is missing. Propose the missing setup first.

## Native Metadata

Prefer native GitHub metadata for canonical fields:

| Field | Rule |
|---|---|
| Type/kind | Native issue Type or configured issue-form kind |
| Status | GitHub Project status field, not a status label |
| Priority | Native priority/project field, milestone, or board order |
| Milestone | Native milestone for release, phase, or time bucket |
| Owner | Assignee plus body text when accountability differs |
| Parent/child | Native sub-issues or explicit linked parent issue |

Labels are only for dimensions that native metadata does not cover: area, component, risk, audience, version impact, documentation impact, or workflow hints. Do not create labels for type, status, priority, or milestone.

## Decision Issues

A good Decision issue includes:

- decision question,
- realistic options and trade-offs,
- recommendation when known,
- evidence and linked intake,
- owner or decider,
- target date when timing matters,
- outcome, rationale, and follow-up links once decided.

When a Decision is resolved, update linked tasks, roadmap items, specs, reports, or KB summaries instead of leaving the outcome only in a comment.

## Routing and Handoff

When intake becomes execution work:

1. Keep the original tracker item as the context source unless ownership explicitly moves.
2. Create or propose the destination issue/ticket/spec/PR.
3. Include outcome, audience, acceptance signal, decisions, evidence, and source links.
4. Link back from the destination to the source item.
5. Close, route, or mark the source item when it no longer needs action there.

Do not mirror downstream status into the source item. Link to the downstream system or issue instead.

## Roadmap, Journey, and Spec Consistency

If the repository enables `roadmaps`, `journeys`, `delivery`, or `operations` in `.kb-config/layers.yaml`, check the relevant chain before mutating roadmap-shaped work:

- roadmap item -> decision or evidence -> journey step or spec when applicable,
- feature/task -> parent roadmap item or brief when applicable,
- PR -> issue -> KB artifact or tracker item that explains why the change exists,
- incident/release follow-up -> task or decision with a clear owner.

Flag missing links instead of inventing them. Small child tasks may inherit context from a parent, but should still name the affected artifact when obvious.

## PR Discipline

- PRs must explain what changed and why.
- PRs must include validation commands or a clear reason validation is not needed.
- Each completed issue needs its own closing keyword.
- Apply exactly one version-impact label only when the repository has configured that policy.
- Update changelogs and governed docs when the repository rules require it.
- Agents may open PRs, push commits, and respond to review, but must not merge, approve, or enable auto-merge on PRs they authored.

## CI and Agent-Guidance Parity

When changing `.github/workflows/`, issue templates, PR templates, labeler rules, branch protection guidance, or validation scripts:

1. Update this skill or the relevant local agent instruction in the same PR.
2. Explain the rule in prose, including edge cases.
3. Keep the CI check and local guidance aligned.
4. If a rule is advisory only, say so explicitly.

## Behavior

- For `files`, create or update the normal KB file.
- For `tracker`, create or update the configured tracker item only after confirmation, then write KB summaries or backlinks only when useful.
- For `hybrid`, keep early exploration in files and propose tracker promotion when the item crosses the configured sharing boundary.
- Never use labels to duplicate native type, status, priority, or milestone metadata.
- Never post comments, change status, apply labels, link issues, or create items without confirmation.
- Log every confirmed write-back with target identifier, action, and evidence.

## Typical Read-Only Checks

Use equivalent GitHub UI/API calls if `gh` is unavailable.

```bash
gh issue view <number> --json number,title,type,assignees,milestone,labels,projectItems,url
gh pr view <number> --json number,title,body,labels,closingIssuesReferences,reviewDecision,statusCheckRollup,url
```

Typical mutations require human confirmation first:

```bash
gh issue edit <number> --add-assignee @me --milestone <milestone>
gh issue comment <number> --body "Linked follow-up: <url>"
gh pr edit <number> --add-label version/patch
```

## Output

Respond with:

1. Classification.
2. Canonical record and proposed/applied route.
3. Issue/project/parent/milestone/assignee/status health when relevant.
4. Affected KB artifacts, roadmap items, journeys, specs, releases, or incidents when relevant.
5. PR closing-link and validation status when relevant.
6. Whether anything was applied or only proposed.
7. Missing fields or follow-up cleanup.
