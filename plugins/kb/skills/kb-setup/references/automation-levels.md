# Automation Levels — setup contract

> **Version:** 6.3.0 | **Last updated:** 2026-06-02

This reference defines what the setup interview means when it asks for automation level `1`, `2`, or `3`.

## Canonical levels

| Level | Meaning | Expected `automation.yaml` shape |
|------:|---------|----------------------------------|
| `1` | Manual only | `schedules:` may be omitted or left inactive; `auto-promote.enabled: false` |
| `2` | Scheduled rituals and digests | `schedules:` may run read/review flows such as `start-day`, `digest-parent`, `digest-connections`, `task-review`, and `end-week`; `auto-promote.enabled: false` |
| `3` | Scheduled flows plus guarded auto-promote | Same scheduled flows as level 2, plus `auto-promote.enabled: true` only when the user opted in and set a confidence threshold |

## Guardrails

- Level 1 is the default proof path for first-run acceptance.
- Level 2 may automate reads, summaries, and review preparation, but it does not silently promote material upward.
- Level 3 still requires explicit guardrails: confidence threshold, excluded workstreams, and the collaboration/output-contract rules for visible mutations.

## Scheduler ownership

`agentic-kb` does not ship a scheduler. At level 2 and level 3 the `schedules:` block describes the *intended cadence*; the trigger is the adopter's responsibility. Acceptable triggers include:

- OS cron / launchd / systemd timer invoking the harness CLI,
- a CI schedule (e.g. GitHub Actions cron) invoking the harness,
- a Claude Code "routine", an OpenCode automation, or any harness-native scheduler that supports invoking custom slash commands.

`kb-setup` phase 4 must surface this explicitly when level 2 or level 3 is chosen: the user will not get scheduled runs unless they wire the trigger themselves.

## Confidence threshold (level 3)

`auto-promote.confidence-threshold` is the integer evaluation-gate score (0–5) that an artifact must reach before it is eligible for auto-promote. Same scale as the gate in `docs/REFERENCE.md` §2. Default `4`. Full algorithm and eligibility filter live in `docs/REFERENCE.md` §6 ("`auto-promote.confidence-threshold` — what it is"). When `/kb setup` proposes level 3, it must:

1. confirm the threshold value with the user (default `4`, range `3..5`),
2. ask which workstreams should be excluded from auto-promote (defaults to none),
3. show one worked example of what would auto-promote under the chosen threshold so the user can sanity-check the expected blast radius,
4. note that the user still owns the scheduler trigger that fires `digest-parent`.

## Mapping during setup

When `/kb setup` writes `.kb-config/automation.yaml`:

1. ask for the user's desired level,
2. explain the matching behavior in plain language,
3. write only the schedule or auto-promote fields that the chosen level permits,
4. keep `auto-promote.enabled: false` unless the user explicitly selected level 3 and confirmed the guardrails (threshold + excluded workstreams + acknowledged scheduler ownership).

## Related

- [`../SKILL.md`](../SKILL.md)
- [`../../../../../docs/REFERENCE.md`](../../../../../docs/REFERENCE.md)
- [`../../../../../docs/first-run-acceptance.md`](../../../../../docs/first-run-acceptance.md)

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-06-02 | Added required version/changelog metadata so plugin specs and references are covered by the consistency check | Issue #144 |
| 2026-05-18 | Added explicit "Scheduler ownership" section (agentic-kb does not ship a scheduler; the adopter wires OS cron / CI / harness-native automation) and a "Confidence threshold (level 3)" section that requires the wizard to confirm threshold + excluded workstreams + a worked example before writing `auto-promote.enabled: true`. Closes audit findings #94 and #105 | Concept/onboarding/process audit |
| 2026-04-25 | Initial reference defining the setup interview contract for automation levels 1/2/3 and how they map into `.kb-config/automation.yaml` | Deep spec-audit follow-up |
