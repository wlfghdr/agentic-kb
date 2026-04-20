# Output Contract — collaboration-safe review

This document defines the response contract for `agentic-kb` operations where humans need to review or trust what an agent did.

The top-level rule stays the same: keep output terse. But terse does not mean ambiguous.

## Required action modes

Every meaningful response must make the operation mode obvious.

### 1. Read-only analysis

Use when the agent inspected state and changed nothing.

Examples:
- `/kb`
- `/kb status`
- `/kb start-day`
- `/kb diff team`
- `/kb audit` when no fixes were applied

Required wording signal in **What I did**:
- `checked`
- `reviewed`
- `briefed`
- `inspected`
- `compared`

Never use wording that sounds like a file mutation happened.

### 2. Proposed mutation

Use when the agent is recommending a change but has not applied it.

Examples:
- promotion recommendation
- suggested topic update
- suggested decision creation
- suggested external fetch before consent

Required wording signal in **What I did**:
- `proposed`
- `suggested`
- `prepared`
- `identified a candidate`

The response must not make the user infer whether the change already happened.

### 3. Applied mutation

Use when files or tracked state actually changed.

Examples:
- capture wrote a finding
- digest created a digest finding
- promote copied material into another layer
- decision opened or updated
- task changed

Required wording signal in **What I did**:
- `captured`
- `wrote`
- `updated`
- `promoted`
- `digested`
- `created`
- `moved`

The response must say where the mutation landed.

## Four required sections

Every normal response still uses the same four sections:

1. **What I did**
2. **Where it went**
3. **Gate notes**
4. **Suggested next steps**

In collaborative contexts, those sections have stricter meaning.

## Section rules

### 1. What I did

Must communicate all of these when relevant:

- action mode: read-only, proposed, or applied,
- scope: personal, team, org, or marketplace,
- whether external material was fetched,
- whether cross-layer movement happened.

Good examples:

- `Checked personal KB status, read-only.`
- `Proposed a team promotion candidate, no files changed.`
- `Captured the article as a finding after fetching the URL.`
- `Digested new team changes into the personal KB and updated VMG.`

### 2. Where it went

For read-only operations, list what was inspected.

For mutations, list exact target paths.

For cross-layer operations, show source and destination clearly enough that a human reviewer can audit the movement.

Good examples:

- `Read alice-kb/.kb-config/layers.yaml and alice-kb/_kb-tasks/focus.md.`
- `Wrote alice-kb/_kb-references/findings/2026-04-20-cache-paper.md.`
- `Moved alice-kb/_kb-references/findings/... -> team-kb/alice/_kb-inputs/...`.

### 3. Gate notes

Gate notes must make uncertainty and provenance visible enough for trust.

When relevant, include:

- score or matched questions,
- whether confidence was low or borderline,
- whether novelty or duplication was detected,
- whether the source was local only or externally fetched.

Good examples:

- `4/5, externally fetched, likely durable, overlaps partially with existing topic.`
- `2/5, local-only, captured as finding only, not strong enough for decision impact.`
- `n/a, read-only briefing.`

### 4. Suggested next steps

This section must distinguish clearly between:

- actions already applied,
- actions merely suggested.

Do not list something as a next step if it already happened in the same operation unless the next step is a follow-up form of that action.

Good examples:

- `Promote this finding to team.`
- `Open a decision from the conflict.`
- `Refresh HTML overviews.`

Bad example:

- `Capture the article.` when the article was already captured.

## External material rule

If external material was fetched, say so explicitly.

Minimum acceptable disclosure:

- in **What I did**: mention that the URL or external material was fetched,
- in **Gate notes**: indicate that the judgment used externally fetched content.

If the user has not yet consented to fetch and consent is required by the skill, the response must stay in **proposed mutation** mode until consent is given.

## Cross-layer action rule

For `promote`, `digest`, and `publish`, the response must make layer movement explicit.

Minimum acceptable disclosure:

- source layer,
- destination layer,
- whether the action was proposed or applied,
- the concrete destination path or artifact.

A human reviewer should not need to inspect git diff first to understand what moved where.

## Collaboration-safe examples

### Capture example

```text
What I did: Captured the article as a personal finding after fetching the URL.
Where it went: Wrote alice-kb/_kb-references/findings/2026-04-20-cache-paper.md and updated alice-kb/_kb-references/topics/caching.md.
Gate notes: 4/5, externally fetched, informs an open decision, likely durable, partial overlap with existing caching topic.
Suggested next steps:
- Promote this finding to team.
- Update the related decision with this evidence.
- Refresh HTML overviews.
```

### Promote example

```text
What I did: Promoted one personal finding to the team KB.
Where it went: Moved alice-kb/_kb-references/findings/2026-04-20-cache-paper.md -> team-kb/alice/_kb-inputs/2026-04-20-cache-paper.md.
Gate notes: Reused existing gate result, team-relevant, no secret or PII indicators detected.
Suggested next steps:
- Ask the team KB to digest the promoted finding.
- Open a shared decision if the team needs alignment.
```

### Digest example

```text
What I did: Digested new team signals into the personal KB, applied mutation.
Where it went: Read team-kb/alice/_kb-references/findings/... and wrote alice-kb/_kb-references/findings/2026-04-20-team-digest.md; updated alice-kb/_kb-references/foundation/vmg.md.
Gate notes: Mixed evidence set, local synthesis from team inputs, one unresolved conflict remains between platform and reliability positions.
Suggested next steps:
- Open a decision for the unresolved conflict.
- Review the updated VMG before promoting anything upward.
```

## Related

- `SKILL.md`
- `command-reference.md`
- `../../../../docs/collaboration.md`
- `../../../../docs/examples/first-hour.md`
- `../../../../docs/examples/day-in-the-life.md`
