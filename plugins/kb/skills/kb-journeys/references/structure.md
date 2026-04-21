# Reference: journey markdown structure

Every journey markdown file follows this contract. `kb-journeys render` validates it; `kb-journeys audit` reports violations.

## File-level metadata block

Required, immediately under the H1:

```markdown
# <tier>.<phase> — <Journey Title>

> **Sub-Journey**: <one-line path summary>
> **Tier**: <tier label>
> **Target duration**: <duration>
> **Design patterns**: <comma-separated>   (optional)
> **Version**: <n.n> | **Last updated**: YYYY-MM-DD
```

## Required sections (in order)

### 1. Entry Conditions

Unordered list, present-tense truths that must hold before the journey starts.

### 2. Exit Conditions

Unordered list, present-tense truths that hold when the journey completes.

### 3. Interfaces

A table of cross-journey edges:

| Direction | Sub-Journey | What |
|-----------|-------------|------|
| OUT → | `<slug>` | summary of handoff |
| IN ← | `<slug>` | summary of preconditions received |

### 4. Flow

Ordered steps. Each step is an `###` heading with id metadata:

```markdown
### Step <n>: <title> · `J<tier>.<phase>-S<n>` · `[ACTOR]`
```

Where:

- `<n>` — ordinal within the journey.
- id pattern — `J<tier>.<phase>-S<n>` — stable once assigned, must be unique across the journey.
- `[ACTOR]` — who drives the step (`[CLI]`, `[WEB UI]`, `[AGENT]`, `[SYSTEM]`, `[PERSONA]`, etc.). Controlled vocabulary configured in `.kb-config/layers.yaml` under `journeys.actors`.

Step body contains:

- Prose description.
- Optional `#### Readiness` with a chip span.
- Optional `#### Mock` with the mock envelope.
- Optional `#### Alternates` listing named failure routes (explicit, not implicit).

### 5. (Optional) Cross-references

`## Related` or `## Sources` — links to adjacent KB files (decisions, findings, roadmap items).

## Readiness chips

Every step that is visible to the user **should** declare readiness. Steps without readiness are marked draft in the generated HTML.

```markdown
#### Readiness
<span class="status-chip feasible">Green</span> — <one-line rationale>
```

Levels and chip classes are configurable via `.kb-config/layers.yaml` under `journeys.readiness-levels`. The default set is:

| Key | Chip class | Meaning |
|---|---|---|
| `feasible` | `feasible` | ready now / can be demoed |
| `partial` | `partial` | part of the step ready; rest needs work |
| `blocked` | `blocked` | not feasible in current state |

## Mock envelope

To make a mock extractable into a standalone page, wrap it with a `mock-begin` / `mock-end` comment pair **and** give the container a `data-mock="<slug>"` attribute:

```markdown
<!-- mock-begin: sign-up-screen -->
<div class="mockup-block" data-mock="sign-up-screen">
  <div class="mockup-header">
    <span>Sign-up · web UI</span>
    <span class="status-chip feasible">Green</span>
  </div>
  <div class="mockup-body">
    ... HTML mock content ...
  </div>
</div>
<!-- mock-end: sign-up-screen -->
```

Rules:

- `slug` must match `[a-z0-9][a-z0-9-]*`.
- Every `begin` must have a matching `end` with the same slug.
- Slugs must be unique within a journey file.
- Mocks may contain nested `<style>` / `<script>` blocks; the extractor lifts them into the standalone page.
- The closest preceding `id=` attribute on an ancestor step defines the back-link target. If none found, the standalone page links back to the journey file only.

## Journey id scheme

| Level | Pattern | Example |
|---|---|---|
| Journey | `<tier>.<phase>` | `1.3` |
| Sub-journey | `<tier>.<phase>.<sub>` | `1.4.2` |
| Step | `J<tier>.<phase>-S<n>` | `J1.3-S4` |
| Step within sub-journey | `J<tier>.<phase>.<sub>-S<n>` | `J1.4.2-S1` |
| Mock | `<journey-id>_<slug>` | `J1.3-S4_pr-preview` |

Ids are stable link targets. Rename is a deliberate operation (`kb-journeys rename-id`) that rewrites references across the KB.

## Overview file

A cross-journey overview lives at `_kb-journeys/overview.md`. It:

- Lists all journeys grouped by tier
- Provides a matrix of cross-journey interfaces
- Maps personas to journeys
- Declares which journeys are "entry points"

See `templates/journey-overview.md.hbs` for the scaffold.

## Audit checks

`kb-journeys audit` runs these checks and reports pass/fail:

1. File-level metadata block present and parseable
2. All required sections present and in order
3. All step ids match the pattern + are unique
4. All mock envelopes balanced (every `begin` has matching `end`, unique slugs)
5. Every visible step has a readiness chip (warn only)
6. Every interface table row references an existing journey slug
7. Every cross-reference link resolves
