# Concurrency

> **Version:** 6.2.0 | **Last updated:** 2026-05-24

This guide defines what `agentic-kb` does when two contributors mutate shared layer state at the same time. The structural spec ([`docs/REFERENCE.md`](./REFERENCE.md)) defines layout and formats; the collaboration guide ([`docs/collaboration.md`](./collaboration.md)) defines the human contract. This guide names the concrete conflict cases and the rules `/kb promote`, `/kb sync`, and Git itself follow when contributors collide.

The user-facing `/kb sync [layer]` command contract is canonical in [`command-reference.md`](../plugins/kb/skills/kb-management/references/command-reference.md#digests--layer-flow): it covers both contributor-scoped cross-reference reconciliation and the concurrency reconciliation cases in this guide.

## Why a separate guide

`agentic-kb` is offline-first and Git-native. There is no central server arbitrating concurrent writes. Two contributors can independently promote, decide, or update a topic on the same day; the resolution has to be predictable from rules in the spec, not from whoever pushes last.

This guide does not invent a lock manager. It defines deterministic outcomes for the three concurrency cases the spec did not previously name: **promote collisions**, **backlink mutation**, and **topic merges**.

## Case 1 — Promote collisions (same artifact, two authors, same day)

Scenario: Alice and Bob both promote a finding with the same slugified title to the team layer on the same day, or both promote different decisions whose paths collide.

### Rule

1. The first promote writes its target file under the canonical path (`<target-layer>/_kb-references/findings/YYYY/YYYY-MM-DD-<slug>.md` or the matching `_kb-decisions/D-YYYY-MM-DD-<slug>.md`).
2. The second promote detects the path collision before writing. It must:
   - **append the author-id suffix** to its target filename — `YYYY-MM-DD-<slug>-<author>.md` (e.g. `2026-05-22-cache-strategy-bob.md`),
   - **write a conflict log entry** under `_kb-log/promote-conflicts.md`:

     ```markdown
     2026-05-22T14:32:11Z | promote-conflict | team-observability | _kb-references/findings/2026/2026-05-22-cache-strategy.md | second promote rewrote target to ...-bob.md; original promoted by @alice at 14:08:02Z
     ```

   - **point both contributors at a reconciliation step**: the response names the canonical path, the suffixed path, and offers `/kb sync <layer>` as the next step so a human decides whether the two records reflect (a) the same finding written twice (deduplicate keeping the first) or (b) genuinely different evidence (rename the suffixed file with a more descriptive slug and keep both).
3. The conflict log is append-only. `/kb audit` rule K13 (`promote-conflict-unresolved`) reports any entry older than 7 days that has no matching dedup/rename mutation in `.kb-log/`.

### Why suffix, not last-write-wins

Suffix preserves both contributors' work and forces a human read of the disagreement. Last-write-wins is silently destructive and erodes trust in the shared layer. A merge conflict in Git would have the same effect, but with worse UX (HTML/yaml conflict markers in a finding body); the suffix rule short-circuits the conflict at the application level before Git ever sees it.

### Decisions and tasks under split ownership

When both contributors promote a decision/task with the same scope and the target layer applies the §1 canonical-ownership rule (see [`docs/REFERENCE.md`](./REFERENCE.md) §1), the suffix rule still applies during the write, but the reconciliation step is the canonical-record-merge flow from `promote-contract.md`:

- one of the two suffixed records becomes canonical;
- the other is rewritten as a backlink stub per [`docs/REFERENCE.md`](./REFERENCE.md) §4 "Backlink (promoted-record stub)";
- both contributors' source-layer records become backlinks to the canonical winner.

## Case 2 — Backlink mutation after promote

Scenario: Alice promotes `D-2026-05-18-pricing-tier.md` from her personal layer to the team layer. The source record becomes a backlink stub (`status: promoted` + `canonical:` per [`docs/REFERENCE.md`](./REFERENCE.md) §4). Three days later, Alice edits the source file — not the canonical target.

### Rule

1. The source file's frontmatter `status: promoted` is the agent's signal that the file is not the source of truth. Any `/kb` mutation that targets a `status: promoted` file MUST:
   - **refuse the mutation**, naming the canonical path,
   - **offer two paths**: edit the canonical target instead, or unpromote the source (rewrite frontmatter to a working status, log the demotion, and accept that the canonical target now diverges).
2. If the source file is edited outside `/kb` (a contributor opens the markdown file and types into it directly), the divergence is detected at the next read by `/kb sync` or `/kb audit`:
   - `/kb sync` lists every `status: promoted` file whose mtime is newer than its `promoted-at:` frontmatter date as a **diverged backlink**.
   - `/kb audit` rule K11 (`backlink-broken`) already covers the unresolvable-canonical case; rule K14 (`backlink-diverged`) covers the mutated-source case.
3. The reconciliation step is human: either revert the source edit (the canonical record is authoritative), or copy the source edit upward to the canonical record (the source contributor still owns the thinking; the backlink resync happens on next promote).

### Why no automatic resync

Automatic resync would silently overwrite either the source or the canonical record, depending on direction. Both options lose information. The diverged-backlink warning is loud and reviewable; the human picks the direction.

## Case 3 — Topic merges (concurrent edits to the same shared topic)

Scenario: Alice and Bob both update `team-observability-kb/_kb-references/topics/cache-strategy.md` on the same afternoon. They push to the same branch. Git surfaces a merge conflict in the topic body.

### Rule

1. Topic files use a **section format with authored sub-sections** so concurrent edits land as coexisting sections instead of conflict markers:

   ```markdown
   # Topic: cache-strategy

   **Maturity**: emerging
   **External anchors**: [links]

   ## Position — @alice 2026-05-22

   Living prose owned by alice.

   ## Position — @bob 2026-05-22

   Living prose owned by bob.

   ---
   ## Changelog
   | Date | What changed | Source |
   ```

   The `## Position — @<author> <YYYY-MM-DD>` heading is the canonical author-sectioned form when more than one contributor edits the same topic. Each author writes inside their own section. Cross-references between sections are explicit (`see @bob's section above`).

2. When Git surfaces a merge conflict on a topic body and the section format is in use, the resolution is mechanical: each author's section is preserved, the conflict markers are removed, and the per-author dates are kept as they stood at the conflict. No `merge=ours` attribute applies — topic conflicts surface to a human because they reflect a real interpretation disagreement.

3. When two authors are editing the **same author-section** (e.g. both editing `## Position — @alice`), the conflict is a real disagreement on the same content. Standard Git resolution applies; the agent does not auto-resolve.

4. Topic convergence — the moment when the team decides a single position — is an **explicit operation**, not an emergent property of resolving merge conflicts. Convergence is recorded by:
   - rewriting the topic to a single `## Position` heading (no author suffix),
   - moving the per-author sections into the topic's inline `## Changelog` with `What changed: @alice and @bob converged on …`,
   - opening or resolving a decision (`D-YYYY-MM-DD-cache-strategy.md`) that names the convergence and cites both source sections.

5. `/kb audit` rule K15 (`topic-author-sections-unconverged`) reports topics that have carried more than one `## Position — @<author>` heading for longer than `freshness.topic-days` (default 60). Long-running disagreement is fine, but it should not be invisible.

### Why explicit author sections

Markdown's merge behavior is byte-level. Two paragraphs of living prose by two authors will conflict on every shared line break. Author-sectioned topics make merges trivial when authors edit independently and surface the real disagreement when they don't. The format is opt-in for single-author topics — only multi-user shared topics need it.

## Case 4 — Concurrent writes to logs and dashboards

Scenario: Two contributors regenerate `dashboard.html` or append to `.kb-log/YYYY-MM-DD.log` on the same minute.

### Rule

- **Live HTML overviews** (`index.html`, `dashboard.html`) are covered by the `.gitattributes` `merge=ours` policy in [`docs/REFERENCE.md`](./REFERENCE.md) §6 "HTML artifact lifecycle". The merge resolves to the local copy; the next regeneration from KB state converges deterministically. No application-level rule is needed.
- **`.kb-log/YYYY-MM-DD.log`** is append-only. Two authors appending to the same daily log produce a Git merge conflict only if their entries land on the same line — which the canonical `HH:MM:SSZ | operation | scope | target | details` format prevents in practice (entries are line-separated with timestamps). When a conflict does occur (clock skew, manual edits), standard Git resolution applies; both entries are kept.
- **Conflict-log files** (`_kb-log/promote-conflicts.md`, `_kb-log/exceptions.md`, `_kb-log/auto-promote-staged.md`) are also append-only and follow the same rule.

## Test fixtures (planned)

The rules in this guide are the normative contract — the parallel-promote, backlink-mutation, and topic-merge cases above stand on their own as executable spec language for adopters and tool builders.

Regression fixtures that exercise the same cases are **planned**, not shipped in this release:

- `tests/fixtures/concurrency/` will carry the input KB state and expected outcome for each case (suffix rule, diverged-backlink detection, author-sectioned topic merge).
- `scripts/test_concurrency.py` will run them and gate CI once the fixtures land.

Until those exist, the rules above are the only contract; CI does not currently exercise the concurrency cases. Adopters writing their own adapters or migration helpers should validate manually against the rules; the path names are reserved so the future fixtures land where this doc already points.

## Related

- [`docs/REFERENCE.md`](./REFERENCE.md) §1 "Two orthogonal axes" — layer role and artifact visibility.
- [`docs/REFERENCE.md`](./REFERENCE.md) §4 "Backlink (promoted-record stub)" — backlink format consumed by case 2.
- [`docs/REFERENCE.md`](./REFERENCE.md) §6 "HTML artifact lifecycle" — `merge=ours` for live overviews referenced in case 4.
- [`docs/collaboration.md`](./collaboration.md) "Failure modes and recovery" — human-facing summary of the same cases.
- [`plugins/kb/skills/kb-management/references/command-reference.md`](../plugins/kb/skills/kb-management/references/command-reference.md#digests--layer-flow) — `/kb sync [layer]` user-facing command contract.
- [`plugins/kb/skills/kb-management/references/promote-contract.md`](../plugins/kb/skills/kb-management/references/promote-contract.md) — promote semantics consumed by cases 1 and 2.
- [`plugins/kb/skills/kb-management/references/audit.md`](../plugins/kb/skills/kb-management/references/audit.md) — K11 (broken backlink), K13 (unresolved promote conflict), K14 (diverged backlink), K15 (unconverged author-sectioned topic).

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-05-24 | Version aligned to 6.2.0 | Version alignment |
| 2026-05-24 | Added the bidirectional command-reference link so adopters can see that `/kb sync [layer]` covers both contributor-scoped cross-reference reconciliation and the concurrency reconciliation cases in this guide. Closes #124 | `/kb sync` contract reconciliation |
| 2026-05-22 | Initial concurrency guide closing audit finding #106 — promote collisions resolve via author-id suffix + `_kb-log/promote-conflicts.md` entry; backlink mutation after promote refuses `/kb` writes against `status: promoted` source files and surfaces a diverged-backlink warning at the next `/kb sync` / `/kb audit`; topic merges land as author-sectioned `## Position — @<author> <date>` blocks so concurrent edits coexist; `.kb-log/` and live overviews follow append-only and `merge=ours` rules already declared in REFERENCE.md §6. New `/kb audit` rules K13–K15 surface unresolved conflicts, diverged backlinks, and long-running author disagreement. Closes audit finding #106 | Concept/spec-gap audit closeout |
