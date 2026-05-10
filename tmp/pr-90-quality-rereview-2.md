# PR #90 Quality Re-review, round 2

Verdict: **merge-ready**

Scope reviewed: only the two remaining delivery-report findings.

## Findings

1. **`choose_delivery_signal()` fix looks correct**
   - The merged delivery row now uses the preferred correlated copy and preserves `In Progress` for an item whose merged phase is `in-delivery`.
   - Focused repro returned `In Progress`, not `shipped (...)`.

2. **`item_journey_links()` fix looks correct**
   - Journey linkage now scans `raw_records` / correlated copies, so an explicit step citation found only on the non-preferred tracker copy is still linked.
   - Focused repro returned `J1.2-S2` with the expected citation note.

3. **Regression coverage is present and relevant**
   - `scripts/test_kb_report_runtime.py` now asserts both cases directly:
     - `PLAT-301` for the merged delivery-signal edge case
     - `PLAT-401` for the non-preferred correlated journey citation case

## Checks run

- `python3 scripts/test_kb_report_runtime.py` ✅
- Focused Python repro for `choose_delivery_signal()` ✅
- Focused Python repro for `item_journey_links()` ✅

No remaining issue found in the two requested areas.