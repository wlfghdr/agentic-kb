# Adoption Quality Review

Date: 2026-05-10
Branch: `fix/issue-34b`
Reviewer stance: independent quality pass, strict on real adoption risk

## Passed areas

- The new **roadmap → delivery report → status report → roadmap change report** storyline is consistently described across `docs/collaboration.md`, `docs/REFERENCE.md`, `plugins/kb/skills/kb-management/references/html-artifacts.md`, `plugins/kb/skills/kb-management/references/command-reference.md`, and `docs/examples/day-in-the-life.md`.
- The three new report source templates are directionally useful. They keep the artifacts small, reviewable, and visibly linked back to roadmap and journey context instead of pretending HTML alone is the source of truth.
- The adoption pass did not obviously destabilize the roadmap/journey helper surfaces. Focused regression checks passed:
  - `python3 scripts/test_kb_roadmap.py`
  - `python3 scripts/test_kb_journeys.py`

## Concerns

- The collaboration model is much clearer than before, but it is still stronger as a **conceptual model** than as an **operating contract**. A team could agree with the narrative and still implement the artifacts in incompatible ways.
- The new shared report family is documented and templated, but not yet backed by an equally crisp storage, naming, freshness, and ownership contract.

## Actionable findings

### 1. High: report source artifacts have no canonical file-location and naming contract

**Why this matters**
The docs repeatedly say status, delivery, and roadmap-change markdown files are durable shared artifacts, but they do not clearly say where those markdown sources live, how they are named, or how another person/agent determines which one is current. HTML output location is defined. Markdown source location is not.

That creates immediate adoption risk: two teams can both be "following the spec" while storing report sources in different places, with no reliable way to discover the latest source of truth.

**Evidence**
- `docs/REFERENCE.md` defines the templates and relationships, but not the source-file path convention.
- `plugins/kb/skills/kb-management/references/html-artifacts.md` says the markdown sources are durable shared artifacts, but again does not assign a canonical directory/filename pattern.
- `plugins/kb/skills/kb-management/references/command-reference.md` adds concrete commands for these report kinds, which raises the expectation that discovery and storage rules are settled.

**Suggested fix**
Add a small but explicit contract, for example:
- canonical directory for markdown report sources
- filename pattern per report kind
- whether reports are immutable snapshots, rolling current files, or both
- how `latest` is resolved
- whether HTML renders from a specific source file or from the current state model

### 2. Medium: ownership boundaries are still advisory, not operational

**Why this matters**
The role guidance is helpful, but it is still too soft for shared execution. "Lead / PM," "engineering / delivery owners," and "domain owners / reviewers" overlap enough that a real team could still ask: who must open the roadmap change report, who approves it, and who is accountable when status and delivery disagree?

This is most dangerous for roadmap-change reporting, because that artifact exists specifically when shared expectations are shifting.

**Evidence**
- `docs/collaboration.md` uses role expectations phrased as "should keep" and "should challenge," but does not define a default accountable owner/reviewer pattern.
- The report templates each have an `Owner` field, but there is no rule for who that should default to by report type.

**Suggested fix**
Add a default accountability matrix, even if lightweight:
- Status report: owner, required inputs, default reviewer
- Delivery report: owner, evidence sources, escalation rule when evidence conflicts
- Roadmap change report: owner, who must acknowledge/approve, and when engineering can initiate vs when PM/lead must initiate

### 3. Medium: emission/update triggers are still too subjective for reliable team habits

**Why this matters**
The model explains what each artifact is for, but not tightly enough when each artifact must be created or refreshed. Phrases like "whenever the baseline itself moves" and "changes enough that future status reports would otherwise look confusing" are sensible, but too interpretive for consistent team behavior.

This will produce drift between teams, and even within one team over time.

**Evidence**
- `docs/collaboration.md` and `plugins/kb/skills/kb-management/references/html-artifacts.md` describe the interplay well but stop short of concrete trigger thresholds.
- The templates include `Cadence`, but the surrounding contract does not define recommended defaults by report type.

**Suggested fix**
Add explicit default trigger rules, for example:
- status report: weekly, or after major decision/blocker change
- delivery report: per sprint/release/demo cadence
- roadmap change report: required on scope, sequencing, commitment-date, owner, or milestone-baseline changes above a stated threshold
- clarify whether a roadmap-change report is mandatory before the next status report when baseline shifts materially

### 4. Medium: the new report family lacks validation/linting coverage, so doc drift is likely

**Why this matters**
The new artifacts are important enough to steer cross-role collaboration, but the validation evidence in this branch is still concentrated on roadmap and journeys. That means the new report-source contract can drift silently, especially because it spans docs, templates, and command-reference text.

**Evidence**
- The new templates exist under `plugins/kb/skills/kb-management/templates/`.
- The documented validation summary in `tmp/integration-pass-summary.md` covers roadmap/journeys helper checks, not these new report-source artifacts.
- I ran `python3 scripts/test_kb_roadmap.py` and `python3 scripts/test_kb_journeys.py`; both passed, but there is no parallel check here for report-source consistency.

**Suggested fix**
Add a minimal consistency test or audit rule that checks:
- referenced report templates exist
- command-reference names match template/report-kind names
- the docs agree on canonical report kinds
- any future path contract for report sources stays aligned across docs

## Bottom line

This pass is a meaningful improvement. The shared artifact story is now coherent enough for humans to understand the intended operating model.

However, I would **not** call the adoption path fully clean yet. The main remaining risk is not conceptual confusion about roadmap/journey interplay. It is operational ambiguity around **where the report sources live, who owns each one, and exactly when they must be emitted**. Those gaps are fixable, but they are real enough to cause uneven team adoption if left as-is.
