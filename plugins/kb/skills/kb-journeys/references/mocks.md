# Reference: mock extraction

## Why this exists

A journey markdown file often embeds UI or terminal mocks that illustrate a step. Readers and reviewers need to link to a specific mock in isolation — for a Slack message, a PR review comment, a presentation, or to iterate the mock without scrolling through the whole journey. The extractor turns every inline mock into its own standalone HTML page and back-links both directions.

## Envelope

A mock is wrapped with begin/end HTML comments **and** carries a `data-mock="<slug>"` attribute on the container:

```html
<!-- mock-begin: sign-up-screen -->
<div class="mockup-block" data-mock="sign-up-screen">
  <div class="mockup-header">
    <span class="mockup-title">Sign-up · web UI</span>
    <span class="status-chip feasible">Green</span>
  </div>
  <div class="mockup-body">
    <!-- mock content: HTML, nested <style>, nested <script> -->
  </div>
</div>
<!-- mock-end: sign-up-screen -->
```

Both markers are required. The extractor ignores containers without matching comment markers — this prevents accidental extraction of non-mock `<div>` blocks.

## Extraction rules

1. Parse the journey HTML (already rendered from markdown).
2. Find every `<!-- mock-begin: <slug> -->` ... `<!-- mock-end: <slug> -->` pair.
3. Collect the container node between them, plus any `<style>` / `<script>` elements nested inside.
4. Compute the back-link target: walk ancestors + previous siblings for the nearest `id="J...-S..."` attribute (the step anchor). If none found, back-link to the journey file only.
5. Render the standalone page using `templates/mock-standalone.html.hbs`.
6. Write to `<html-subdir>/mocks/<journey-id>_<slug>.html`.
7. Patch the source journey HTML: inside `.mockup-header`, insert or replace the standalone link:
   ```html
   <a class="mock-standalone-link" href="mocks/<journey-id>_<slug>.html">↗ Open standalone</a>
   ```
8. Collect metadata for the mocks index.

## Standalone page layout

Structure of `mocks/<journey-id>_<slug>.html`:

```html
<!DOCTYPE html>
<html ...>
  <head>
    <link rel="stylesheet" href="../shared.css">
    <!-- mock-local styles lifted verbatim -->
  </head>
  <body>
    <div class="mock-standalone-bar">
      <div class="crumbs">
        <a href="../index.html">Overview</a> ·
        <a href="../<journey-slug>.html#<step-anchor>">Journey</a> ·
        <span class="title"><mock-title></span>
      </div>
      <a class="back-link" href="../<journey-slug>.html#<step-anchor>">← Back to journey step</a>
    </div>
    <div class="mock-standalone-wrap">
      <!-- the mock container, lifted verbatim -->
    </div>
    <!-- mock-local scripts lifted verbatim -->
  </body>
</html>
```

## Mocks index

`mocks/index.html` is a generated page listing every extracted mock. Format:

- Grouped by journey (headings)
- Each entry: slug · title · step id (linked) · "Open standalone" link
- Summary line at the top: total count per tier, last generated timestamp

## Safety

- **Script lifting is verbatim, not sanitized.** Mock authors own their scripts. The extractor does not run them, only copies them.
- **No network fetches.** The extractor operates purely on local files.
- **No secrets sweep beyond baseline.** Adopters wanting secret-scrubbing before extraction wire `scripts/pre-extract.py` via config.

## Idempotency

Running the extractor twice with no source change produces byte-identical output. The source-file patch step is idempotent — it replaces an existing `.mock-standalone-link` anchor rather than appending.

## Integration with `render`

`kb-journeys render` runs the extractor as its last step. `kb-journeys extract-mocks` is the extractor-only command, useful when only mock content changed.
