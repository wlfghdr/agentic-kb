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

# Canonical idea uses `**Stage**:` per REFERENCE.md and idea.md template.
IDEA_STAGE_MD = """# Idea: Swarm-as-code

**Stage**: growing
**Created**: 2026-04-22
**Workstream**: agent-orchestration
**Sparring rounds**: 2

## Seed

Declarative swarm topology in the KB itself.
"""

# Legacy idea using `**Status**:` — parser should accept it as an alias
# so pre-3.5 files still render instead of silently defaulting to `seed`.
IDEA_STATUS_LEGACY_MD = """# Idea: Legacy alias test

**Status**: ready
**Created**: 2026-04-22
**Workstream**: kb-internals
**Sparring rounds**: 1
"""

ARTIFACTS_YAML = """dashboard:
  panels:
    - focus-tasks
    - backlog
    - active-ideas
    - topics
"""

TOPIC_MD = """# Topic: Deployment strategy

**Maturity**: durable
**Updated**: 2026-04-22

## Current position

Prefer convergent delivery paths that keep shared review cost low.

## Changelog

| Date | What changed | Source |
|------|-------------|--------|
| 2026-04-22 | Initial topic stub for dashboard visibility regression coverage | Issue #22 |
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
        (tempdir / '_kb-ideas').mkdir(parents=True, exist_ok=True)
        (tempdir / '_kb-ideas' / 'I-2026-04-22-swarm-as-code.md').write_text(IDEA_STAGE_MD, encoding='utf-8')
        (tempdir / '_kb-ideas' / 'I-2026-04-22-legacy.md').write_text(IDEA_STATUS_LEGACY_MD, encoding='utf-8')
        (tempdir / '_kb-references' / 'topics').mkdir(parents=True, exist_ok=True)
        (tempdir / '_kb-references' / 'topics' / 'deployment-strategy.md').write_text(TOPIC_MD, encoding='utf-8')
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

        # #35: idea with `**Stage**: growing` renders with the correct badge.
        assert_contains(output, 'Swarm-as-code')
        assert_contains(output, 'growing')

        # #35 back-compat: legacy idea with `**Status**: ready` still renders
        # with the correct badge rather than silently defaulting to `seed`.
        assert_contains(output, 'Legacy alias test')
        assert_contains(output, 'ready')

        # #22: topics are first-class dashboard state and must render as a
        # dedicated panel with their maturity badge.
        assert_contains(output, 'Topics')
        assert_contains(output, 'Deployment strategy')
        assert_contains(output, 'durable')

        print('generate-dashboard regression test: OK')
        return 0
    finally:
        shutil.rmtree(tempdir)


if __name__ == '__main__':
    raise SystemExit(main())
