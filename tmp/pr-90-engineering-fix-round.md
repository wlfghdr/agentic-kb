# PR #90 engineering fix round

## What changed
- Fixed delivery report generation to build from a deduped per-item view keyed by item id, with explicit tracker precedence, explicit delivery-signal selection, and no guessed journey-step attachment.
- Tightened journey linkage so delivery rows only cite journey steps when the source item explicitly references them; otherwise the report now says linkage is absent and records the traceability gap.
- Fixed roadmap-change diffing so a single item can emit multiple baseline changes in one run instead of stopping after the first changed field.
- Replaced the roadmap-change template's unresolved `draft | approved` text with a truthful runtime approval status placeholder, currently rendered as `draft`.

## Regression coverage
- Expanded `scripts/test_kb_report_runtime.py` to cover multi-tracker delivery dedupe, explicit journey citation mapping, absence of guessed linkage, multi-field roadmap diffs, and the runtime approval-status value.

## Validation
- `python3 scripts/test_kb_report_runtime.py`
- `python3 -m py_compile plugins/kb/skills/kb-management/scripts/generate_report.py scripts/test_kb_report_runtime.py`

## Re-review focus
- Delivery report rows for multi-tracker scopes, especially dedupe, chosen delivery signal, and journey linkage behavior.
- Roadmap-change output for compound changes on a single item.
- Approval-status rendering in the roadmap-change markdown source.
