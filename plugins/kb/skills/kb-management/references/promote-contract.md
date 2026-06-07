# Promote Contract — staged review semantics

> **Version:** 6.3.0 | **Last updated:** 2026-06-02

This reference defines what `/kb promote` means once a source artifact is judged mature enough to move upward.

`/kb promote` is the **upward-after-maturation** path. It is parallel to (not a substitute for) [`capture-routing.md`](./capture-routing.md), which covers the **first-write destination** for new artifacts. If a capture's correct destination was clear from the start — pre-instructed by the user, matched by a configured rule, or confirmed when the agent reflected on the input — direct routing writes the artifact in the target layer without ever needing this promote flow.

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

### Backlink stub format

When a source-layer decision/task is replaced by a backlink (because the target layer now owns the canonical scope), the source file is **rewritten in place** using the standard backlink format defined in [`docs/REFERENCE.md`](../../../../../docs/REFERENCE.md) §4 "Backlink (promoted-record stub)". The minimum shape:

```markdown
---
status: promoted
canonical: <repo-relative path to the canonical target>
promoted-at: YYYY-MM-DD
promoted-by: @author          # optional at single-user layers, recommended at multi-user layers
---

# <original id-and-title line>

> **This record has been promoted.** The canonical version lives at
> `<canonical path>`. Edit there, not here.
```

Concrete rules during `/kb promote`:

1. The source file path stays stable; only its frontmatter and body are rewritten.
2. The `canonical:` path is repo-relative POSIX (e.g. `../../../team-observability-kb/_kb-decisions/D-2026-05-18-pricing-tier.md`) so migration helpers can rewrite it deterministically when layer paths change.
3. The original evidence trail, options, RACI, or development log content moves into the canonical target before the source body is replaced — nothing material stays behind.
4. The promote operation emits a log entry citing both the source and the canonical paths, so the diff is auditable from `.kb-log/` alone.
5. `/kb audit` rule K11 detects backlinks whose `canonical:` no longer resolves and offers a rewrite (or removal if the canonical record was deleted).

## Response expectations

The applied response should make all three locations visible when they exist:

- source path,
- temporary staged path,
- durable destination path and archived intake path.

For decision/task promotions, also state whether the source item stayed active with a distinct scope or was closed as superseded by the target item.

That lets another human audit the movement without inferring what happened from a git diff alone.

## Concurrency

Concurrent promotes (two contributors promoting the same artifact, or revising a source file after a promote) follow the deterministic rules in [`docs/concurrency.md`](../../../../../docs/concurrency.md):

- **Promote collisions** (same target path on the same day) write the second promote with an author-id suffix and append to `_kb-log/promote-conflicts.md`. Reconciliation is via `/kb sync`.
- **Backlink mutation** (editing a `status: promoted` source after promote) is refused by `/kb` and surfaces as a diverged-backlink warning at the next `/kb sync` or `/kb audit` (audit rule K14).
- These are application-level rules; they short-circuit Git conflicts that would otherwise surface as raw merge markers in finding bodies or decision frontmatter.

## Related

- [`../SKILL.md`](../SKILL.md)
- [`command-reference.md`](./command-reference.md)
- [`output-contract.md`](./output-contract.md)
- [`../../../../../docs/collaboration.md`](../../../../../docs/collaboration.md)
- [`../../../../../docs/concurrency.md`](../../../../../docs/concurrency.md)

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-06-02 | Added required version/changelog metadata so plugin specs and references are covered by the consistency check | Issue #144 |
| 2026-05-23 | Added the preamble that names this as the upward-after-maturation flow and points at [`capture-routing.md`](./capture-routing.md) as the parallel first-write-destination flow. Stops adopters from reading promote as the *only* way artifacts cross layers | Artifact layer routing |
| 2026-05-22 | Added "Concurrency" subsection pointing at [`docs/concurrency.md`](../../../../../docs/concurrency.md): promote collisions resolve via author-id suffix + `_kb-log/promote-conflicts.md` entry; backlink mutation after promote refuses `/kb` writes and surfaces a diverged-backlink warning. Closes audit finding #106 | Audit-tracker closeout |
| 2026-05-22 | Added "Backlink stub format" subsection codifying the `status: promoted` + `canonical:` + `promoted-at` frontmatter and the standardized banner body that replaces a source-layer record when canonical ownership shifts upward, with rules for path resolution, evidence migration, audit detection (K11), and migration-helper rewrites. Closes audit finding #111 | Concept/spec gap audit |
| 2026-05-06 | Added decision/task ownership semantics for promotion: one canonical record per scope, with source-layer decisions/tasks closed or archived unless their scope genuinely differs | Decision/task ownership follow-up |
| 2026-04-25 | Initial reference clarifying when `/kb promote` stages intake, when it skips staging, and what the destination-layer review must leave behind | Deep spec-audit follow-up |
