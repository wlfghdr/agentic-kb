# GitHub Governance Setup Checklist

Use this checklist after `/kb setup` stages the generic GitHub governance profile.

## Native Issue Types

Create or verify the issue types your repository uses. Suggested generic set:

- Feedback
- Idea
- Decision
- Task
- Bug
- Feature
- Roadmap Item
- Content Update
- Governance Change

If your GitHub plan does not support custom issue types, keep the issue forms and record the mapping in `.kb-config/layers.yaml` under `connections.trackers[].issue-types`.

## GitHub Project

Create or verify the project that represents shared operating state.

Suggested status values:

- Todo
- In Progress
- In Review
- Done

Use project fields for status, priority, and planning buckets when available. Do not recreate those fields with labels.

## Labels

Use labels for dimensions that native metadata does not model:

- `area/*`
- `component/*`
- `risk/high`
- `needs-clarification`
- `needs-decision`
- `needs-review`
- `version/none`, `version/patch`, `version/minor`, `version/major` if your repository uses version-impact labels

Avoid labels for type, status, priority, milestone, or project phase.

## Branch Protection

Recommended default-branch protection:

- require pull requests before merging,
- require at least one human review for non-trivial changes,
- require conversation resolution,
- block force pushes,
- block branch deletion,
- require the generated GitHub governance workflow after it has passed on at least one PR,
- require project-specific validation workflows after they are stable.

Agents may open PRs, but should not merge, approve, or enable auto-merge on PRs they authored.

## CODEOWNERS

If the repository has real ownership boundaries, add CODEOWNERS entries for those areas. Keep ownership aligned with how humans review the work; do not create fake owners just to satisfy a template.

## First Verification

1. Open a small test PR that references a test issue.
2. Confirm `.github/workflows/kb-github-governance.yml` passes.
3. Confirm the repo-local `kb-tracker-workflow` skill names the same rules the workflow enforces.
4. Make the workflow required only after the test PR proves it is stable.
