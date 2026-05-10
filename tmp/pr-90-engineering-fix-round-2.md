# PR #90 Engineering Fix Round 2

Implemented only the two remaining Quality findings in `plugins/kb/skills/kb-management/scripts/generate_report.py`.

## What changed

1. **Merge-safe delivery signal selection**
   - `choose_delivery_signal()` now selects evidence from the merged item's preferred tracker copy instead of treating any shipped correlated copy as authoritative.
   - This keeps an `in-delivery` merged item from reporting `shipped (...)` just because another correlated copy is shipped.

2. **Journey linkage across correlated copies**
   - `merge_item_group()` now preserves all correlated raw records and source titles on the merged item.
   - `item_journey_links()` now scans every correlated raw/body/path payload, so explicit journey-step citations found only on the other tracker copy are still linked.

3. **Regression coverage**
   - Extended `scripts/test_kb_report_runtime.py` with the exact remaining repro shapes:
     - plan `Done` + delivery `In Progress` must render an `in-delivery` row with `In Progress`, not `shipped (...)`
     - journey citation present only on the delivery-side copy must still map to the cited step

## Validation

- `python3 scripts/test_kb_report_runtime.py` ✅

## Please re-review

Focused re-review requested on:
- merged delivery rows for multi-tracker items where correlated copies disagree on phase
- delivery report journey linkage when the explicit step citation exists only on the non-preferred correlated copy
