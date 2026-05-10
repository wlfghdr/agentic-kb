# PR #90 Quality Review

Verdict: **not merge-ready**

Current PR state:
- `gh pr view 90` reports `mergeStateStatus: DIRTY`, so the branch is not currently mergeable.
- Validation in the PR description passed locally: `check_consistency`, `check_plugin_structure`, `check_report_artifacts`, `test_kb_roadmap`, `test_kb_journeys`, and `test_kb_report_runtime` all passed on PR head `885c596`.

Findings:

1. **High – delivery report runtime can misstate reality for multi-tracker scopes**
   - In `plugins/kb/skills/kb-management/scripts/generate_report.py:248-297`, `fill_delivery()` iterates raw roadmap JSON `items` directly, without deduping correlated entries by item id. A single work item that appears in both plan and delivery sources can therefore be counted twice, show the wrong delivery signal, and push other commitments out of the top-5 table.
   - It also assigns the first available journey step to every commitment (`line 255`), even when no explicit item-to-journey link exists.
   - I reproduced this with two items and two journeys: the generated delivery report duplicated `A-1`, omitted `B-1` from the commitments table, and attached the same journey step to unrelated rows.
   - **Fix guidance:** build the delivery report from a deduped/merged per-item view keyed by `id`, choose an explicit precedence rule for plan vs delivery status, and only emit journey-step evidence when a real mapping exists. Otherwise say linkage is heuristic or absent. Add a regression with at least two correlated items and two journeys.

2. **Medium – roadmap-change reporting under-reports compound baseline changes**
   - In `generate_report.py:305-313`, `diff_roadmaps()` stops at the first differing field per item because of the `break`. If phase, target, owner, or lane all change together, only one change is emitted.
   - That drifts from the documented model for roadmap-change reports, which is supposed to explain the baseline changes and downstream impact clearly.
   - **Fix guidance:** emit one row per changed field, or one aggregated row listing all changed dimensions for that item. Add a regression where one item changes both phase and target (and ideally owner/lane too).

Runtime-honesty note:
- `plugins/kb/skills/kb-management/templates/report-roadmap-change.md` still emits `**Approval status**: draft | approved` as unresolved template text instead of a truthful runtime state like `draft` or `pending approval`. That is worth tightening while fixing the above.
