#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / 'scripts' / 'generate-dashboard.py'


FOCUS_MD = """# Focus

> Max 6 items. Top item is "Next up".

- [ ] Draft promote-contract v1 <!-- workstream: agent-orchestration -->
- [ ] Open team discussion on shared feature store <!-- source: retro -->

## Waiting

- (none)
"""

BACKLOG_MD = """# Backlog

- (empty)
"""

ARTIFACTS_YAML = """dashboard:
  panels:
    - focus-tasks
    - backlog
"""


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected to find {needle!r}")


def assert_not_contains(text: str, needle: str) -> None:
    if needle in text:
        raise AssertionError(f"did not expect to find {needle!r}")


def main() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix='agentic-kb-dashboard-test-'))
    try:
        (tempdir / '_kb-tasks').mkdir(parents=True, exist_ok=True)
        (tempdir / '_kb-tasks' / 'focus.md').write_text(FOCUS_MD, encoding='utf-8')
        (tempdir / '_kb-tasks' / 'backlog.md').write_text(BACKLOG_MD, encoding='utf-8')
        (tempdir / '.kb-config').mkdir(parents=True, exist_ok=True)
        (tempdir / '.kb-config' / 'artifacts.yaml').write_text(ARTIFACTS_YAML, encoding='utf-8')

        subprocess.run(
            ['python3', str(SCRIPT), str(tempdir), '--title', 'Simulated KB'],
            check=True,
            cwd=REPO,
        )

        output = (tempdir / 'dashboard.html').read_text(encoding='utf-8')

        # Real focus items are surfaced.
        assert_contains(output, 'Draft promote-contract v1')
        assert_contains(output, 'Open team discussion on shared feature store')

        # Bug 1: (none) under ## Waiting must not be counted as a focus task.
        assert_not_contains(output, '>(none)<')

        # Bug 2: HTML comment metadata must not leak into rendered titles.
        assert_not_contains(output, '<!-- workstream:')
        assert_not_contains(output, '<!-- source:')

        # Bug 3: placeholder `- (empty)` under Backlog must not render or count.
        assert_not_contains(output, '>(empty)<')
        assert_contains(output, '0 items total')

        print('generate-dashboard regression test: OK')
        return 0
    finally:
        shutil.rmtree(tempdir)


if __name__ == '__main__':
    raise SystemExit(main())
