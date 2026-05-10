# PR #90 merge conflict resolution

Resolved the `origin/main` merge conflicts on `fix/issue-34b` and kept the branch aligned with current `main` while preserving the PR #90 work.

## What was kept from main
- 5.6.0 framework/manifests/versioning surface
- current kb-management / kb-setup / roadmap/journey setup-proposed product-management model
- current CI and regression suite additions from main

## What was preserved from PR #90
- shared report source contract for `status`, `delivery`, and `roadmap-change`
- roadmap/journey operating-model clarifications across README, reference docs, collaboration guide, and day-in-the-life example
- richer `kb-journeys` helper runtime behavior and fallback coverage
- roadmap helper/runtime contract clarifications and roll-up/root-index regression coverage
- CI validation for shared report artifacts and journey helper regression

## Validation
Ran:
- `python3 scripts/test_kb_roadmap.py`
- `python3 scripts/test_kb_journeys.py`
- `python3 scripts/test_html_templates.py`
- `python3 scripts/test_generate_dashboard.py`
- `python3 scripts/test_generate_index.py`
- `python3 scripts/test_acceptance_fixture.py`
- `python3 scripts/test_kb_migrations.py`
- `python3 scripts/check_report_artifacts.py`
- `python3 scripts/check_html_artifacts.py`

All passed.
