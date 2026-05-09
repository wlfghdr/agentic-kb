# Integration Pass Summary

Date: 2026-05-08

## Goal

Close the major contract drift around `kb-roadmap` and `kb-journeys` without hiding those draft surfaces from the published marketplace story.

## What changed

### `kb-roadmap`

- Updated `plugins/kb/skills/kb-roadmap/scripts/kb_roadmap.py` to resolve inputs from the published `roadmap.plan-sources[]` / `roadmap.delivery-sources[]` config path, while keeping legacy `issue-trackers[]` / `scopes.<name>.trackers[]` compatibility.
- Added scope resolution so default/detail scopes can be resolved from configured workstreams, and roll-up scopes aggregate child scopes with de-duplication by `(tracker, id)`.
- Added helper-runtime output parity for `_kb-roadmaps/index.html` and the documented roll-up filename pattern `roadmap-<scope>-<date>.*`.
- Kept the higher-order `/kb roadmap` draft command surface visible in docs, but tightened the docs to distinguish the shipped helper runtime from the broader future behavior.

### `kb-journeys`

- Rebuilt `plugins/kb/skills/kb-journeys/scripts/render_journeys.py` so a render pass now emits:
  - `shared.css`
  - one HTML page per discovered journey
  - `index.html` from `overview.md` plus discovered journey cards
  - standalone mock pages and `mocks/index.html`
- Fixed the fallback HTML corruption path: when `python-markdown` is absent, the built-in renderer now preserves step anchors, raw HTML, and mock envelopes instead of collapsing the flow into escaped `<pre>` output.
- Updated `plugins/kb/skills/kb-journeys/scripts/extract_mocks.py` with a no-`beautifulsoup4` fallback path so extraction degrades cleanly instead of hard-failing.
- Added overview-card styling to the shared CSS baseline.

### Docs / manifests / CI

- Patched the roadmap/journey behavioral docs so they stay published, but are explicit about which parts are implemented by the shipped helper scripts today.
- Removed stale claims such as `kb-journeys/templates/overview.html.hbs` and unimplemented `status-*.{md,html,json}` roadmap artifacts.
- Kept draft future surfaces visible where they matter, but labeled them as behavioral-spec targets when the helper runtime still does not implement them.
- Bumped the framework patch version to `3.4.1` across `VERSION`, marketplace manifests, and the README badge/status copy.
- Added CI coverage for the two draft helper surfaces in `.github/workflows/validate.yml`.

## Regression coverage added

- `scripts/test_kb_roadmap.py`
  - verifies published source-config ingestion
  - verifies detail and roll-up artifact naming
  - verifies `_kb-roadmaps/index.html` refresh
- `scripts/test_kb_journeys.py`
  - exercises the no-dependency fallback path
  - verifies journey step anchors survive render
  - verifies overview index generation
  - verifies standalone mock emission and back-links

## Validation run

Passed locally:

- `python3 scripts/check_consistency.py`
- `python3 scripts/check_plugin_structure.py`
- `python3 scripts/test_generate_index.py`
- `python3 scripts/test_kb_roadmap.py`
- `python3 scripts/test_kb_journeys.py`
- `python3 scripts/check_html_artifacts.py`
- `python3 -m py_compile plugins/kb/skills/kb-journeys/scripts/render_journeys.py plugins/kb/skills/kb-journeys/scripts/extract_mocks.py plugins/kb/skills/kb-roadmap/scripts/kb_roadmap.py`

## Precise doc narrowing that remained necessary

- `kb-roadmap` still does not implement the full interactive `sync` / `tune` / `review-tier-4` / write-back tracker flows in the local helper script. Those behaviors remain in the behavioral spec and are now documented that way instead of being implied as already shipped runtime.
- `kb-roadmap` roll-up scopes now work in the helper script, but they currently reuse the shared timeline/findings/status-board layout rather than a distinct leadership-only `X1`–`X7` render.
- `kb-roadmap` archive/retention handling remains reserved in the folder contract but is not auto-executed by the helper script yet.

## Remaining work after this pass

- Implement the broader interactive roadmap flows if the local helper runtime is expected to match the full behavioral spec, not just the current published marketplace story.
- Add a true structural `kb-journeys audit` helper if CI needs journey-shape validation beyond render/extract regression checks.
