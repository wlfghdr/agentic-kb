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

## Response expectations

The applied response should make all three locations visible when they exist:

- source path,
- temporary staged path,
- durable destination path and archived intake path.

That lets another human audit the movement without inferring what happened from a git diff alone.

## Related

- [`../SKILL.md`](../SKILL.md)
- [`command-reference.md`](./command-reference.md)
- [`output-contract.md`](./output-contract.md)
- [`../../../../../docs/collaboration.md`](../../../../../docs/collaboration.md)

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-25 | Initial reference clarifying when `/kb promote` stages intake, when it skips staging, and what the destination-layer review must leave behind | Deep spec-audit follow-up |
