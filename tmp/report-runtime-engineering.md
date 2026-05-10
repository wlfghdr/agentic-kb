# Report runtime engineering summary

## What now works

- Added a real shared-report runtime at `plugins/kb/skills/kb-management/scripts/generate_report.py`.
- The runtime now materializes canonical markdown source artifacts for:
  - status report
  - delivery report
  - roadmap change report
- It derives report content from actual KB state instead of template placeholders only:
  - latest roadmap JSON snapshot per scope from `_kb-roadmaps/<scope>/`
  - previous roadmap snapshot for roadmap-change diffs
  - journey markdown under `_kb-journeys/`
  - decision records under `_kb-decisions/`
  - scope-related findings under `findings/`
- It renders a self-contained HTML companion for each generated markdown source into `_kb-references/reports/`.
- Roadmap change reports now compare the latest two roadmap snapshots and surface concrete baseline changes such as phase, target, ownership, sequence, additions, and removals.
- Added an end-to-end integration test at `scripts/test_kb_report_runtime.py` that simulates a KB, generates two roadmap snapshots, then proves delivery, roadmap-change, and status reports are created with linked evidence.

## Validation run

Passed:
- `python3 scripts/test_kb_report_runtime.py`
- `python3 scripts/test_kb_roadmap.py`
- `python3 scripts/test_kb_journeys.py`
- `python3 scripts/check_report_artifacts.py`

## What still does not work yet

- The runtime uses heuristic linkage between roadmap items and journey signals. It does not yet have an explicit cross-artifact mapping contract.
- HTML rendering is practical and self-contained, but it does not yet reuse the richer `report.html` deck template or versioned artifact naming rules.
- The runtime does not yet refresh the root HTML artifact index after generating reports.
- It does not yet persist changelog/version history across report regenerations.
- It does not yet integrate with a top-level `/kb report ...` command dispatcher; this is the underlying generation path.
- Approval state is documented in the generated source artifacts, but there is no separate approval workflow engine yet.

## Engineering judgment

This is a small but honest runtime path: it turns real KB state into reviewable shared report sources plus rendered HTML, keeps roadmap/journey/report interplay intact, and makes roadmap-change reporting materially grounded instead of speculative.
