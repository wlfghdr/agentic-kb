# Automation Levels — setup contract

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

## Mapping during setup

When `/kb setup` writes `.kb-config/automation.yaml`:

1. ask for the user's desired level,
2. explain the matching behavior in plain language,
3. write only the schedule or auto-promote fields that the chosen level permits,
4. keep `auto-promote.enabled: false` unless the user explicitly selected level 3 and confirmed the guardrails.

## Related

- [`../SKILL.md`](../SKILL.md)
- [`../../../../../docs/REFERENCE.md`](../../../../../docs/REFERENCE.md)
- [`../../../../../docs/first-run-acceptance.md`](../../../../../docs/first-run-acceptance.md)

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-25 | Initial reference defining the setup interview contract for automation levels 1/2/3 and how they map into `.kb-config/automation.yaml` | Deep spec-audit follow-up |
