# Adoption-oriented engineering pass

## What changed

- Added an explicit shared-artifact collaboration model to `docs/collaboration.md`.
  - Defined the recurring artifact set for software-engineering teamwork: status report, delivery report, roadmap change report, and ritual summaries.
  - Clarified ownership expectations across lead/product/engineering/domain-review roles.
  - Added the roadmap → delivery report → status report → roadmap change report operating loop.

- Strengthened report contracts in `plugins/kb/skills/kb-management/references/html-artifacts.md`.
  - Declared markdown report-source artifacts as first-class shared KB artifacts, not just HTML outputs.
  - Added explicit report variants for status, delivery, and roadmap-change.
  - Clarified how those reports relate to daily and weekly summaries.

- Strengthened report command guidance in `plugins/kb/skills/kb-management/references/command-reference.md`.
  - Added `/kb report status [scope]`, `/kb report delivery [scope]`, and `/kb report roadmap-change [scope]`.
  - Added intent-level guidance for when each report kind should be used and what upstream artifacts it should pull from.

- Added reusable source templates under `plugins/kb/skills/kb-management/templates/`:
  - `report-status.md`
  - `report-delivery.md`
  - `report-roadmap-change.md`

- Updated top-level docs for adoption clarity:
  - `docs/REFERENCE.md` now calls out shared collaboration artifacts explicitly.
  - `docs/examples/day-in-the-life.md` now shows the recurring shared-artifact rhythm behind the daily workflow.

## Why these changes matter

The repo already had strong roadmap and journey concepts, but recurring cross-role collaboration was still implied more than operationalized. These changes make adoption easier by giving teams a smaller, clearer set of shared artifacts to rally around, especially for daily status, delivery truth, and baseline-change communication.

## Validation run

Passed:

- `python3 scripts/check_consistency.py`
- `python3 scripts/check_plugin_structure.py`
- `python3 scripts/test_kb_roadmap.py`
- `python3 scripts/test_kb_journeys.py`

## Quality follow-up to pay attention to

A separate quality session should review:

1. Whether the new `/kb report ...` variants should stay as documented aliases or become a stricter formal command grammar across prompts, setup docs, and acceptance docs.
2. Whether adopter-facing setup scaffolding should also create a `reports/sources/` folder convention so these markdown report sources have a canonical in-KB home.
3. Whether the HTML generators and prompt/runtime logic should explicitly consume these new source templates, rather than only documenting them.
4. Whether daily/weekly ritual docs should add examples showing a status report or delivery report being refreshed from real artifacts.
