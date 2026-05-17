# GitHub Governance Profile

> **Version:** 1.0 | **Last updated:** 2026-05-17

This reference defines the generic GitHub setup package that `/kb setup` should generate when an adopter chooses GitHub Issues, GitHub Projects, or a GitHub repository as the operational backbone for shared KB work.

The goal is not just to create issue forms. The goal is to give the adopter a working issue-and-PR operating model with agent-readable rules, CI guardrails, and clear human approval boundaries.

## When Setup Proposes This Profile

Setup should propose the GitHub governance profile when phase 1 or discovery shows any of these signals:

- the team already coordinates in GitHub Issues or GitHub Projects,
- decisions, tasks, features, roadmap items, content updates, or bugs should be tracked in GitHub,
- the user wants PRs to close issues and carry validation evidence,
- the workspace has `.github/` workflows, CODEOWNERS, issue templates, or project references,
- the adopter asks for an issue-driven or PR-driven workflow.

If the user only wants read-only issue digests, setup may configure `connections.trackers[]` without this profile. If the user wants GitHub to be the canonical operational home for primitives, this profile is the default.

## Generated Package

The GitHub governance profile generates or stages these files for the selected repository:

```text
.github/ISSUE_TEMPLATE/config.yml
.github/ISSUE_TEMPLATE/feedback.yml
.github/ISSUE_TEMPLATE/idea.yml
.github/ISSUE_TEMPLATE/decision.yml
.github/ISSUE_TEMPLATE/task.yml
.github/ISSUE_TEMPLATE/bug.yml
.github/ISSUE_TEMPLATE/feature.yml
.github/ISSUE_TEMPLATE/roadmap_item.yml
.github/ISSUE_TEMPLATE/content_update.yml
.github/ISSUE_TEMPLATE/governance_change.yml
.github/PULL_REQUEST_TEMPLATE.md
.github/labeler.yml
.github/workflows/kb-github-governance.yml
agent-skills/kb-tracker-workflow/SKILL.md
```

Setup must also print a manual setup checklist for settings that are not reliably expressible as repository files: native issue types, GitHub Project fields, branch protection, required checks, CODEOWNERS owners, milestones, and labels.

## Operating Rules

### Issue-driven work

Every non-trivial change should start from an issue unless the adopter explicitly marks the PR as a small exception.

The issue should carry:

- native Type or configured kind,
- project membership when a GitHub Project is configured,
- status when a project status field is configured,
- assignee or accountable owner when work starts,
- milestone or roadmap bucket when the layer uses one,
- parent/sub-issue relationship when workstream parents are configured,
- links to KB artifacts, roadmap items, specs, decisions, or delivery work as relevant.

### Native metadata before labels

Use native GitHub metadata for canonical fields:

| Field | Preferred home |
|---|---|
| Kind/type | Native issue Type, or configured issue-form kind when native types are unavailable |
| Status | GitHub Project status field |
| Priority | Native priority field, project field, milestone, or board order |
| Milestone | Native milestone |
| Owner | Assignee plus body text when accountability differs |
| Parent/child | Native sub-issues or linked issue references |

Labels are for dimensions that native metadata does not model: area, component, risk, audience, version impact, documentation impact, workflow hints, or adopter-specific routing cues. Labels must not duplicate type, status, priority, or milestone.

### PR discipline

Pull requests should:

- explain what changed and why,
- reference or close the issue using a closing keyword when the PR completes the issue,
- match the issue scope or update/create follow-up issues when scope changes,
- list validation commands and manual checks,
- name affected KB artifacts or tracker items,
- include changelog/version impact when the adopter configured those policies,
- avoid merging, approving, or enabling auto-merge by the same agent that authored the PR.

### CI and local-agent parity

Any CI rule added by this profile must be visible in the repo-local skill. Agents should know the rule before CI has to reject the PR.

The default guardrail workflow checks:

- issue-form YAML parses,
- unresolved setup placeholders are absent,
- PRs include an issue reference or explicit exception marker,
- version-impact labels are present when the adopter enables that policy,
- the generated repo-local skill remains present.

Adopters can add stronger checks later, but setup must not create CI-only policy without matching agent-readable guidance.

## Manual Setup Checklist

After file generation, setup should print a checklist like this, filled with the adopter's configured values:

1. Create or verify native issue types: Feedback, Idea, Decision, Task, Bug, Feature, Roadmap Item, Content Update, Governance Change.
2. Create or verify the GitHub Project and status values, for example: Todo, In Progress, In Review, Done.
3. Add repository labels only for area, component, risk, version impact, and workflow hints.
4. Configure branch protection on the default branch: require PR review, block force pushes, block deletions, and require the GitHub governance check once stable.
5. Configure CODEOWNERS if the repository has real ownership boundaries.
6. Decide whether parent/sub-issues are required for workstream placement.
7. Decide whether version-impact labels are required, and if yes configure the workflow environment accordingly.
8. Run the generated guardrail workflow once before making it required.

## Skill Behavior After Setup

The generated `kb-tracker-workflow` skill should be the local operating manual. It must cover:

- classification before mutation,
- source-of-truth boundaries,
- native metadata and label discipline,
- decision issue completeness,
- task and feature routing,
- roadmap/spec/journey link checks where those features are enabled,
- PR closing-link and validation rules,
- confirmation before GitHub writes,
- no self-merge or self-approval by agents,
- CI/local-guidance parity.

The skill reads `.kb-config/layers.yaml` first. It must not bake in organization-specific repository names, project numbers, labels, milestones, or policy names.

## Verification

Setup is not complete for this profile until:

- every generated YAML file parses,
- `.kb-config/layers.yaml` declares the tracker and `primitive-storage` ownership,
- the generated PR template asks for issue links, affected KB/tracker artifacts, validation, and changelog/version impact,
- the generated guardrail workflow passes on a dry PR or local YAML parse check,
- the generated skill states the same rules that the workflow enforces,
- the manual setup checklist names the remaining GitHub UI/API settings.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-17 | Initial generic GitHub governance profile covering issue-driven work, native metadata, PR discipline, CI/local-agent parity, generated files, manual setup checklist, and verification | Tracker-backed onboarding hardening |
