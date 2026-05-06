# Promote Contract — staged review semantics

This reference defines what `/kb promote` means once a source artifact is judged mature enough to move upward.

## Canonical flow

Promotion is an applied mutation with immediate destination-layer review. It is not a mailbox drop that waits for a second command before the destination layer becomes coherent.

1. run the promotion safety check,
2. move the source artifact into the destination flow,
3. complete the destination-layer review in the same operation,
4. write the durable destination result,
5. archive any temporary intake copy under the destination digested path,
6. log both the intake and the reviewed result.

## When staging happens

| Target layer shape | Promote behavior |
|--------------------|------------------|
| Single-user contributor layer | Skip staging; write the durable reviewed result directly into the destination layer's canonical location |
| Multi-user contributor layer with contributor-scoped intake | Stage under `<target>/<contributor>/_kb-inputs/`, review immediately, then archive that staged copy under `digested/YYYY/MM/` |
| `role: consumer` layer | Refuse with a clear message and point to the next valid contributor-capable layer |

## Decision and task ownership during promotion

Decision and task records are not copied upward as parallel active items. Before promoting a decision or task, determine the owning scope:

- If the target layer owns the same decision question and accountable decider, the target decision becomes canonical. Close the source decision as `superseded` or archive it with a backlink to the canonical target decision.
- If the target layer owns the same task scope and accountable owner, the target task becomes canonical. Close, archive, or replace the source task with a backlink to the canonical target task.
- If the source layer still has its own decision to make, keep the source decision active only after stating the narrower source-layer scope, recommendation, or accountable owner that differs from the target decision.
- If the source layer still has its own work to track, keep the source task active only after stating the narrower source-layer scope, sub-task, or accountable owner that differs from the target task.
- If the promotion only provides evidence for an existing target decision, append the evidence trail in the target layer and leave the source as a finding, note, or closed handoff record rather than opening another decision.
- If the promotion only contributes to an existing target task, link the source note/finding or create a clearly scoped sub-task rather than duplicating the target task.

The response must name the canonical path whenever a promoted decision or task is created, resolved, or superseded.

## Response expectations

The applied response should make all three locations visible when they exist:

- source path,
- temporary staged path,
- durable destination path and archived intake path.

For decision/task promotions, also state whether the source item stayed active with a distinct scope or was closed as superseded by the target item.

That lets another human audit the movement without inferring what happened from a git diff alone.

## Related

- [`../SKILL.md`](../SKILL.md)
- [`command-reference.md`](./command-reference.md)
- [`output-contract.md`](./output-contract.md)
- [`../../../../../docs/collaboration.md`](../../../../../docs/collaboration.md)

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-06 | Added decision/task ownership semantics for promotion: one canonical record per scope, with source-layer decisions/tasks closed or archived unless their scope genuinely differs | Decision/task ownership follow-up |
| 2026-04-25 | Initial reference clarifying when `/kb promote` stages intake, when it skips staging, and what the destination-layer review must leave behind | Deep spec-audit follow-up |
