# Adoption engineering fix round

## What I fixed

1. **Canonical markdown source contract for shared reports**
   - Defined stable source-artifact locations and filenames for status, delivery, and roadmap-change reports under `_kb-references/reports/sources/<scope>/`.
   - Documented that markdown is the canonical collaboration artifact and HTML is derived output.
   - Added concrete examples in the day-in-the-life walkthrough.

2. **Ownership and approval boundaries**
   - Added explicit initiator vs approver rules in `docs/collaboration.md`.
   - Clarified that agents may draft and refresh evidence, but cannot auto-approve roadmap baseline changes.
   - Added required approval metadata to the roadmap-change template.

3. **Deterministic triggers**
   - Defined concrete emission/update triggers for status, delivery, and roadmap-change reports.
   - Wired the command/reference docs to reflect event-driven roadmap-change behavior and cadence-based plus signal-based status/delivery refreshes.

4. **Explicit KB feedback loop**
   - Added a step-by-step flow for how feedback from leaders, customers, demos, prototypes, support, analytics, and delivery reality enters the KB.
   - Kept roadmap and journeys first-class by requiring explicit links instead of collapsing everything into narrative prose.

5. **Validation coverage for the report family**
   - Added `scripts/check_report_artifacts.py`.
   - Added CI coverage in `.github/workflows/validate.yml`.
   - Validation now checks required report metadata, sections, canonical paths, and key ownership/approval contract references in the docs.

## Validation run

Passed locally:
- `python3 scripts/check_report_artifacts.py`
- `python3 scripts/test_kb_roadmap.py`
- `python3 scripts/test_kb_journeys.py`
- `python3 scripts/check_consistency.py`

## Residual tradeoffs

- The new report family is now well specified and validated at the template/doc-contract level, but there is still no full end-to-end `/kb report ...` implementation in this repo that writes these markdown source files automatically.
- Validation currently enforces the shared contract textually and structurally, not via a live report generator fixture.
- There were already unrelated in-flight modifications on this branch before this pass, especially in roadmap/journey files and generated manifests. I kept this round scoped to the adoption/collaboration/report-contract fixes.
