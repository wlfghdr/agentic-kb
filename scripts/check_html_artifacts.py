#!/usr/bin/env python3
"""
Validate any checked-in HTML artifacts produced by the reference implementation.

The spec repo itself does NOT ship presentations or reports (the template lives
elsewhere). This check is therefore a placeholder that:

  - Scans for .html files under `examples/html/` (opt-in location for example artifacts).
  - If any are found, verifies the minimum contract from docs/REFERENCE.md §6:
      * self-contained (no external <script src=...> or <link rel=stylesheet href=...> pointing
        outside the file — allowed: data: URIs, inline)
      * both light and dark theme present (strings 'theme="light"' / 'theme="dark"' or CSS classes)
      * watermark string on the intro slide (pattern "v<num>.<num> · <date>")
      * appendix with a "Changelog" heading
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CANDIDATE_DIRS = [REPO / "examples" / "html"]

EXTERNAL_RESOURCE_RE = re.compile(
    r"<(?:script|link)[^>]*\s(?:src|href)\s*=\s*['\"](https?:|//)[^'\"]+['\"]",
    re.IGNORECASE,
)
EXTERNAL_CSS_IMPORT_RE = re.compile(r"@import\s+url\((['\"]?)(https?:|//)", re.IGNORECASE)
LIGHT_THEME_PATTERNS = [
    r"""theme[-"':=\s]*["']?light""",
    r"prefers-color-scheme:\s*light",
]
DARK_THEME_PATTERNS = [
    r"""theme[-"':=\s]*["']?dark""",
    r"prefers-color-scheme:\s*dark",
]
WATERMARK_RE = re.compile(r"v\d+\.\d+\s*[·•\-–]\s*\d{4}-\d{2}-\d{2}")
CHANGELOG_HEADING_RE = re.compile(r"<h[1-6][^>]*>\s*Changelog\s*</h[1-6]>", re.IGNORECASE)


def check_artifact(path: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(REPO)
    text = path.read_text(encoding="utf-8", errors="ignore")

    if EXTERNAL_RESOURCE_RE.search(text):
        errors.append(f"{rel}: contains an external <script|link> resource — artifacts must be self-contained")
    if EXTERNAL_CSS_IMPORT_RE.search(text):
        errors.append(f"{rel}: contains an external CSS @import — artifacts must be self-contained")

    if not any(re.search(p, text, re.IGNORECASE) for p in LIGHT_THEME_PATTERNS):
        errors.append(f"{rel}: light theme marker not found")
    if not any(re.search(p, text, re.IGNORECASE) for p in DARK_THEME_PATTERNS):
        errors.append(f"{rel}: dark theme marker not found")

    if not WATERMARK_RE.search(text):
        errors.append(f"{rel}: no watermark in the form 'v<major>.<minor> · <YYYY-MM-DD>' found")

    if not CHANGELOG_HEADING_RE.search(text):
        errors.append(f"{rel}: no 'Changelog' heading found (expected in appendix)")

    return errors


def main() -> int:
    files: list[Path] = []
    for d in CANDIDATE_DIRS:
        if d.is_dir():
            files.extend(sorted(d.rglob("*.html")))

    if not files:
        print("No HTML artifacts to validate (nothing under examples/html/). OK.")
        return 0

    errors: list[str] = []
    for p in files:
        errors.extend(check_artifact(p))

    if errors:
        print("HTML artifact check failed:\n")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\nTotal: {len(errors)} error(s).")
        return 1

    print(f"HTML artifact check: OK ({len(files)} file(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
