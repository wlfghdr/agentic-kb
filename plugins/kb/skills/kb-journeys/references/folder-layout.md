# Reference: folder layout

## Default layout

```
my-kb/
├── _kb-journeys/
│   ├── overview.md                     # cross-journey master map
│   ├── <journey-slug>.md               # single-file journey
│   ├── <complex-journey>/              # multi-file journey
│   │   ├── README.md
│   │   ├── <phase-a>.md
│   │   └── <phase-b>.md
│   ├── html/                           # generated; do not hand-edit
│   │   ├── index.html
│   │   ├── shared.css
│   │   ├── <journey-slug>.html
│   │   └── mocks/
│   │       ├── index.html
│   │       └── <journey-id>_<slug>.html
│   └── scripts/                        # optional adopter overrides
└── .kb-log/YYYY-MM-DD.log
```

## Configuration

Defaults in the active layer's `journeys:` block inside `.kb-config/layers.yaml`:

```yaml
journeys:
  source-dir: _kb-journeys
  output-dir: _kb-journeys
  html-subdir: html
  mocks-subdir: html/mocks
```

Adopters can split source from output — e.g. source in a linked product repo declared under the same layer's `connections.product-repos[]`, output written into the KB:

```yaml
journeys:
  source-dir: ../linked-product-repo/docs/journeys
  output-dir: _kb-journeys
  html-subdir: html
  mocks-subdir: html/mocks
```

When `source-dir` is outside the KB, the skill reads but never writes there. The generated HTML and extracted mocks always go to `output-dir`.

## Naming

- Single-file journey: `<tier>.<phase>-<slug>.md` (e.g. `1.3-bugfix-loop.md`).
- Multi-file journey: directory named `<tier>.<phase>-<slug>/` with a `README.md` as the index.
- Sub-journeys in a multi-file journey: `<tier>.<phase>.<sub>-<slug>.md`.
- Overview file: `overview.md` at the root of `source-dir`.

Hyphen, not dot, separates tier.phase from the slug in the filename (dots in filenames break some tools). The tier.phase is the canonical id; the filename derives from it.

## Generated filenames

- Per-journey HTML: replace dots with dashes — `1-3-bugfix-loop.html`.
- Mock standalone: `<journey-id-dashed>_<slug>.html` — `1-3-bugfix-loop_pr-preview.html`.

## Retention

The journey primitive has no retention policy — journey markdown is source and lives indefinitely. Generated HTML is regenerable, so no archive is needed.
