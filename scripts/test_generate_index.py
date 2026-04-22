#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / 'scripts' / 'generate-index.py'


ARTIFACT_TEMPLATE = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <title>{title}</title>
  <meta name=\"description\" content=\"{summary}\">
</head>
<body>
  <h1>{title}</h1>
  <p>{summary}</p>
  {links}
</body>
</html>
"""


def write_html(path: Path, title: str, summary: str, links: str = '') -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        ARTIFACT_TEMPLATE.format(title=title, summary=summary, links=links),
        encoding='utf-8',
    )


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected to find {needle!r}")


def assert_not_contains(text: str, needle: str) -> None:
    if needle in text:
        raise AssertionError(f"did not expect to find {needle!r}")


def assert_before(text: str, first: str, second: str) -> None:
    first_index = text.find(first)
    second_index = text.find(second)
    if first_index == -1:
        raise AssertionError(f"missing marker {first!r}")
    if second_index == -1:
        raise AssertionError(f"missing marker {second!r}")
    if first_index >= second_index:
        raise AssertionError(f"expected {first!r} before {second!r}")


def main() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix='agentic-kb-index-test-'))
    try:
        config_dir = tempdir / '.kb-config'
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / 'artifacts.yaml').write_text(
            """index:
  pinned-categories:
    - Journey Maps
  category-order: recency
  dedup-versioned: true
  drop-referenced-subpages: true
""",
            encoding='utf-8',
        )

        write_html(
            tempdir / '_kb-references' / 'journey-map-2026-04-10.html',
            'Journey Map',
            'Pinned category should render before newer report categories.',
        )
        write_html(
            tempdir / '_kb-references' / 'reports' / 'weekly-status-2026-04-18.html',
            'Weekly Status',
            'Newer report used to verify pinned categories still come first.',
        )
        write_html(
            tempdir / '_kb-references' / 'reports' / 'strategy-report-v1-2026-04-17.html',
            'Strategy Report v1',
            'Older version that should be deduplicated away.',
        )
        write_html(
            tempdir / '_kb-references' / 'reports' / 'strategy-report-v2-2026-04-18.html',
            'Strategy Report v2',
            'Newest version that should remain after deduplication.',
        )
        write_html(
            tempdir / '_kb-references' / 'journeys' / 'launch-journey.html',
            'Launch Journey',
            'Hub page that links to sub-pages.',
            '<a href="step-1.html">Step 1</a><a href="step-2.html">Step 2</a>',
        )
        write_html(
            tempdir / '_kb-references' / 'journeys' / 'step-1.html',
            'Launch Journey Step 1',
            'Leaf page that should be hidden from the root index.',
        )
        write_html(
            tempdir / '_kb-references' / 'journeys' / 'step-2.html',
            'Launch Journey Step 2',
            'Second leaf page that should also be hidden from the root index.',
        )
        (tempdir / '_kb-references' / 'findings').mkdir(parents=True, exist_ok=True)
        (tempdir / '_kb-references' / 'topics').mkdir(parents=True, exist_ok=True)
        (tempdir / '_kb-ideas').mkdir(parents=True, exist_ok=True)
        (tempdir / '_kb-decisions').mkdir(parents=True, exist_ok=True)
        (tempdir / '_kb-references' / 'findings' / '2026-04-19-latency-spike.md').write_text(
            """# Latency spike in review path

Captured elevated review latency after the latest import batch, with a repeatable trace.
""",
            encoding='utf-8',
        )
        (tempdir / '_kb-references' / 'topics' / 'review-pipeline.md').write_text(
            """---
title: Review pipeline
summary: Living synthesis of the review pipeline bottlenecks and the current operating position.
---

# Review pipeline
""",
            encoding='utf-8',
        )
        (tempdir / '_kb-ideas' / 'async-triage.md').write_text(
            """# Async triage

Use an asynchronous triage pass to reduce operator wait time during inbox review.
""",
            encoding='utf-8',
        )
        (tempdir / '_kb-decisions' / 'decision-queue-ownership.md').write_text(
            """# Queue ownership

Clarify who owns queue health so escalations stop bouncing between contributors.
""",
            encoding='utf-8',
        )

        subprocess.run(
            ['python3', str(SCRIPT), str(tempdir), '--title', 'Simulated KB', '--description', 'Regression test'],
            check=True,
            cwd=REPO,
        )

        output = (tempdir / 'index.html').read_text(encoding='utf-8')

        assert_not_contains(output, '@import url(')
        assert_not_contains(output, 'fonts.googleapis.com')
        assert_not_contains(output, '<script src="https://')
        assert_not_contains(output, '<link rel="stylesheet" href="https://')
        assert_contains(output, 'data-theme="dark"')
        assert_contains(output, '[data-theme="light"]')

        assert_before(output, '<h2>Journey Maps', '<h2>Reports')
        assert_contains(output, 'strategy-report-v2-2026-04-18.html')
        assert_not_contains(output, 'strategy-report-v1-2026-04-17.html')
        assert_contains(output, 'launch-journey.html')
        assert_not_contains(output, 'step-1.html')
        assert_contains(output, '<h2>Findings')
        assert_contains(output, '<h2>Topics')
        assert_contains(output, '<h2>Ideas')
        assert_contains(output, '<h2>Decisions')
        assert_contains(output, '_kb-references/findings/2026-04-19-latency-spike.md')
        assert_contains(output, '_kb-references/topics/review-pipeline.md')
        assert_contains(output, '_kb-ideas/async-triage.md')
        assert_contains(output, '_kb-decisions/decision-queue-ownership.md')
        assert_contains(output, 'Latency spike in review path')
        assert_contains(output, 'Review pipeline')
        assert_contains(output, 'Items</div>')

        print('generate-index regression test: OK')
        return 0
    finally:
        shutil.rmtree(tempdir)


if __name__ == '__main__':
    raise SystemExit(main())
