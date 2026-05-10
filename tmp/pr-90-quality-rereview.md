# PR #90 Quality Re-review

Verdict: **needs-fix**

I reviewed only the latest fix round against the three original findings and ran focused runtime checks.

## Result

1. **High – delivery report runtime is still not merge-safe**
   - The duplicate-row problem is fixed, and the template no longer blindly attaches the first journey step.
   - But the new merge logic still produces misleading delivery evidence in realistic multi-tracker conflicts:
     - `choose_delivery_signal()` returns `shipped (...)` if *any* correlated record is shipped, even when the merged delivery-facing item phase is `in-delivery`.
     - `item_journey_links()` only inspects the merged item's single `raw` payload, so explicit step citations on the other correlated tracker copy are dropped.
   - Repro 1: plan=`Done` with `journey: J1.1-S1`, delivery=`In Progress`.
     - Output row was: `| PLAT-1 Edge case item | in-delivery | J1.1-S1 | shipped (plan-export) | ... |`
     - That is the same core failure mode as the original finding: wrong delivery signal selection for a multi-tracker item.
   - Repro 2: plan=`Committed`, delivery=`In Progress` with the journey citation only on the delivery record.
     - Output row showed `n/a` and `No explicit journey-step mapping found...` even though the correlated delivery record had an explicit step citation.
   - Practical implication: the report can still overstate shipped status and still miss valid journey linkage depending on which tracker copy carries the evidence.

2. **Medium – roadmap-change diffing looks fixed**
   - The previous `break` is gone.
   - Focused runtime test coverage now checks multiple emitted rows for one item (`phase`, `target`, `owner`).

3. **Medium – approval status text looks fixed for this scope**
   - The unresolved literal `draft | approved` is gone.
   - Generated output now renders `**Approval status**: draft`, which is at least concrete and runtime-honest for the current source-report flow.

## Checks run

- `python3 scripts/test_kb_report_runtime.py` ✅
- Two targeted ad hoc runtime repros against `generate_report.py` ❌ revealed the remaining high issue above.

## Recommendation

Do not merge yet. The high finding should stay open until delivery-signal selection and journey-step linkage are computed from the full correlated item group, not from a single merged/raw copy or any shipped record in the group.
