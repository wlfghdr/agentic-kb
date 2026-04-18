# Automation Levels

> **Version:** 0.1 | **Last updated:** 2026-04-18

The system supports three levels of automation. Users pick a level during onboarding and can change it anytime in `.kb-automation.yaml`.

## Levels

### Level 1 — Agent-Assisted (default)

- User triggers commands (`/kb`, `/kb start-day`, …).
- Agent processes, user reviews and confirms.
- User commits and pushes.

**Who this fits**: new users, low-trust settings, highly sensitive content.

### Level 2 — Semi-Automated

- Git hooks (or the harness's background task runner) trigger processing on events — commit, push, fetch.
- Scheduled agent runs for:
  - Daily team KB check (new contributions → auto-digest)
  - Weekly TODO staleness check
- Human approves promotions and publishes.

**Who this fits**: experienced users who trust the evaluation gate but want to keep cross-layer promotions under human control.

### Level 3 — Fully Automated

- Autonomous agent loop:
  1. Pull all repos.
  2. Detect changes (git diff).
  3. Process new inputs with the review gate.
  4. Update TODOs.
  5. Promote if confidence exceeds threshold.
  6. Commit + push.
  7. Notify the user of actions taken (log, notification, or periodic summary).
- Requires an explicit trust configuration: what may auto-promote, what needs human review.

**Who this fits**: power users, leads managing many workstreams, anyone comfortable treating the agent as a junior colleague with clear guardrails.

## Configuration — `.kb-automation.yaml`

```yaml
level: 2                            # 1=manual, 2=semi-auto, 3=full-auto

schedules:
  start-day: daily 08:00
  team-digest: daily 08:00
  todo-review: daily 08:30
  end-week: friday 15:00

auto-promote:
  enabled: false                    # Level 3 only
  confidence-threshold: 0.9
  require-evidence: true
  exclude-topics: [product-vision, core-topics]    # too sensitive for auto

commit-push:
  auto-commit: false                # offer, don't execute
  auto-push: false                  # never push silently
  respect-branch-protection: true   # open a PR instead of pushing

notifications:
  channel: terminal                 # terminal | slack | email | none
```

## Implementation Notes

- **Schedules** are advisory. The harness's background automation (cron, Claude Code task runner, OpenCode daemon) is responsible for firing them. The agent itself doesn't run continuously.
- **`auto-promote`** at Level 3 MUST always log the decision to promote, with the same gate rationale as a manual promote. The log is the audit trail.
- **`respect-branch-protection: true`** is the default. Setting it to `false` is only allowed for local-only KBs with no remote.
- **`notifications.channel: terminal`** is the default because no external integration is required. Slack and email are implementation extensions.

## Automation and the Evaluation Gate

Automation **never bypasses the gate**. At Level 3, the gate still runs — its threshold just determines whether a gate-approved promotion proceeds automatically or is queued for human review.

## Git Hooks (Level 2/3)

Recommended hooks:

| Hook | Purpose |
|------|---------|
| `post-merge` | Trigger digest on team/org KB fetch |
| `post-commit` | Update log, push if auto-push enabled |
| `pre-commit` | Run consistency + version checks |
| `pre-push` | Run the full local CI suite |

Implementations MAY provide a bootstrap script that installs these hooks on first setup. They MUST be idempotent — running twice changes nothing.

## Failure Policy

If any automated operation fails:

- **Level 1**: surface to user immediately.
- **Level 2**: surface as a queued `inputs/` item to be reviewed.
- **Level 3**: surface as a queued item, plus a notification via the configured channel, plus a log line tagged `automation-failure`.

Never silent. Never masked.

---

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-18 | Initial version | Extracted from source spec §8 |
