# Reference: `.kb-config/layers.yaml` `journeys:` block

Full schema with defaults.

```yaml
journeys:
  # Input + output directories.
  source-dir: _kb-journeys
  output-dir: _kb-journeys
  html-subdir: html
  mocks-subdir: html/mocks

  # Tier taxonomy. Each tier gets a color token referenced by name into
  # .kb-config/artifacts.yaml journeys-template.tokens CSS file.
  tiers:
    - { key: t1, label: "Tier 1", color-token: accent-1 }
    - { key: t2, label: "Tier 2", color-token: accent-2 }
    - { key: t3, label: "Tier 3", color-token: accent-3 }

  # Readiness chip taxonomy.
  readiness-levels:
    - { key: feasible, label: "Green",  chip-class: "feasible" }
    - { key: partial,  label: "Amber",  chip-class: "partial" }
    - { key: blocked,  label: "Red",    chip-class: "blocked" }

  # Allowed step actors. Rendered as chips.
  actors:
    - CLI
    - WEB UI
    - AGENT
    - SYSTEM
    - PERSONA

  # Mock envelope markers. Adopters rarely change these.
  mock-envelope:
    begin-marker: "<!-- mock-begin: "
    end-marker:   "<!-- mock-end: "
    container-selector: ".mockup-block"

  # Opt-in: embed shared-terminal-anim.js when terminal-style mocks are used.
  include-terminal-anim: false

  # Audit behavior.
  audit:
    readiness-required: false             # warn or fail on missing readiness chips
    interface-resolution: strict          # strict | lenient
    orphan-mocks: warn                    # warn | error | ignore

  # Link the journeys primitive to a roadmap scope for bidirectional traceability.
  roadmap-link:
    scope: <roadmap-scope-name>            # if declared, every journey step can cite
                                           # roadmap items, and roadmap items can link
                                           # back to their driving journey steps

  # Ownership metadata written by setup when it derives journey work from role/goals.
  ownership:
    layer: <layer-name>
    mode: co-located-with-roadmap           # co-located-with-roadmap | journey-only | layered-future
    rationale: <short plain-text reason>
```

## Validation rules

- `source-dir` and `output-dir` must be valid paths; `source-dir` may live outside the KB root.
- `tiers[].key` must be unique and valid CSS-identifier characters.
- `readiness-levels[].key` must be unique.
- `actors` names are free-form but should be stable once set (referenced from step metadata).
- `mock-envelope.begin-marker` must end with a space; the slug follows it directly.
- `ownership.layer`, when present, must match the layer entry that contains this `journeys:` block.
- `ownership.mode: layered-future` documents intent only; current setup does not synthesize inherited journey maps across layers.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-30 | Added setup-written ownership metadata and clarified that layered journey inheritance remains future work | Product-management surface integration |
