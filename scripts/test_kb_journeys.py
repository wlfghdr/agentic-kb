#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "plugins" / "kb" / "skills" / "kb-journeys" / "scripts" / "render_journeys.py"
TEMPLATE_DIR = REPO / "plugins" / "kb" / "skills" / "kb-journeys" / "templates"


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected to find {needle!r}")


def main() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="agentic-kb-journeys-test-"))
    try:
        source_dir = tempdir / "_kb-journeys"
        output_dir = source_dir / "html"
        source_dir.mkdir(parents=True, exist_ok=True)

        (source_dir / "overview.md").write_text(
            """# Journeys — Overview

## Journeys by tier

This overview is rendered into the generated index.
""",
            encoding="utf-8",
        )
        (source_dir / "1.1-signup.md").write_text(
            """# 1.1 — Sign-up Flow

> **Sub-Journey**: A new user signs up.
> **Tier**: Individual
> **Target duration**: 5 minutes
> **Version**: 0.1 | **Last updated**: 2026-05-08

## Entry Conditions
- User has an invite.

## Exit Conditions
- User reaches the dashboard.

## Interfaces
| Direction | Sub-Journey | What |
|-----------|-------------|------|
| OUT → | `1.2-activation` | Account created |

## Flow

### Step 1: Open sign-up · `J1.1-S1` · `[WEB UI]`
The user opens the sign-up screen.

#### Readiness
<span class="status-chip feasible">Green</span> — Demo-ready.

#### Mock
<!-- mock-begin: signup-screen -->
<div class="mockup-block" data-mock="signup-screen">
  <div class="mockup-header">
    <span class="mockup-title">Sign-up screen</span>
  </div>
  <div class="mockup-body">
    <style>.signup-box { border: 1px solid var(--border); padding: 12px; }</style>
    <div class="signup-box">Email field</div>
  </div>
</div>
<!-- mock-end: signup-screen -->
""",
            encoding="utf-8",
        )
        tokens = tempdir / "brand-tokens.css"
        tokens.write_text(
            """:root {
  --bg: #101820;
  --surface: #17212b;
  --surface2: #20303c;
  --border: #314250;
  --text: #f5f7fa;
  --text-dim: #98a8b8;
  --accent-1: #55ddaa;
  --accent-2: #22aacc;
  --accent-3: #6688ff;
  --warn: #ffb84d;
  --risk: #ff6b6b;
}
""",
            encoding="utf-8",
        )

        env = {
            **os.environ,
            "KB_JOURNEYS_DISABLE_MARKDOWN": "1",
            "KB_JOURNEYS_DISABLE_BS4": "1",
        }
        subprocess.run(
            [
                "python3",
                str(SCRIPT),
                "--source-dir",
                str(source_dir),
                "--output-dir",
                str(output_dir),
                "--template",
                str(TEMPLATE_DIR / "journey.html.hbs"),
                "--shared-css",
                str(TEMPLATE_DIR / "shared.css.hbs"),
                "--mock-template",
                str(TEMPLATE_DIR / "mock-standalone.html.hbs"),
                "--tokens",
                str(tokens),
            ],
            check=True,
            cwd=REPO,
            env=env,
        )

        journey_html = (output_dir / "1-1-signup.html").read_text(encoding="utf-8")
        overview_html = (output_dir / "index.html").read_text(encoding="utf-8")
        mocks_index = (output_dir / "mocks" / "index.html").read_text(encoding="utf-8")
        mock_page = (output_dir / "mocks" / "1-1-signup_signup-screen.html").read_text(encoding="utf-8")
        shared_css = (output_dir / "shared.css").read_text(encoding="utf-8")

        assert_contains(shared_css, "--bg: #101820;")
        assert_contains(journey_html, 'id="J1.1-S1"')
        assert_contains(journey_html, 'href="mocks/1-1-signup_signup-screen.html"')
        assert_contains(overview_html, "1-1-signup.html")
        assert_contains(overview_html, "This overview is rendered into the generated index.")
        assert_contains(mocks_index, "1-1-signup_signup-screen.html")
        assert_contains(mock_page, "../1-1-signup.html#J1.1-S1")

        print("kb-journeys regression test: OK")
        return 0
    finally:
        shutil.rmtree(tempdir)


if __name__ == "__main__":
    raise SystemExit(main())
