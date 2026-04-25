#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
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
            tempdir / '_kb-references' / 'journeys' / 'index.html',
            'Journey Overview',
            'Canonical overview page for the journey set.',
            '<a href="launch-journey.html">Launch</a><a href="team-journey.html">Team</a>',
        )
        write_html(
            tempdir / '_kb-references' / 'journeys' / 'launch-journey.html',
            'Launch Journey',
            'Peer journey page that should stay behind the overview.',
            '<a href="index.html">Overview</a><a href="team-journey.html">Team</a><a href="mocks/index.html">Mocks</a>',
        )
        write_html(
            tempdir / '_kb-references' / 'journeys' / 'team-journey.html',
            'Team Journey',
            'Second journey leaf that should stay behind the overview.',
            '<a href="index.html">Overview</a><a href="launch-journey.html">Launch</a><a href="mocks/index.html">Mocks</a>',
        )
        write_html(
            tempdir / '_kb-references' / 'journeys' / 'mocks' / 'index.html',
            'Journey Mocks',
            'Nested mocks index that should stay behind the overview.',
            '<a href="launch-step-1-mock.html">Standalone mock</a>',
        )
        write_html(
            tempdir / '_kb-references' / 'journeys' / 'mocks' / 'launch-step-1-mock.html',
            'Launch Journey Mock',
            'Standalone mock that should be hidden from the root index.',
        )

        # #21: markdown sources must also surface on the public index.
        finding = tempdir / '_kb-references' / 'findings' / '2026' / '2026-04-22-cache-hit-rate.md'
        finding.parent.mkdir(parents=True, exist_ok=True)
        finding.write_text(
            '# Finding: Cache hit rate drops on deploy\n\n'
            '**Date**: 2026-04-22\n**Workstream**: platform\n'
            '**Maturity**: emerging\n\n## TL;DR\n\nLatency spike.\n',
            encoding='utf-8',
        )
        topic = tempdir / '_kb-references' / 'topics' / 'deployment-strategy.md'
        topic.parent.mkdir(parents=True, exist_ok=True)
        topic.write_text(
            '# Topic: Deployment strategy\n\n**Maturity**: durable\n\n'
            '## Current position\n\nPrefer convergent delivery.\n',
            encoding='utf-8',
        )
        idea = tempdir / '_kb-ideas' / 'I-2026-04-22-swarm-as-code.md'
        idea.parent.mkdir(parents=True, exist_ok=True)
        idea.write_text(
            '# Idea: Swarm-as-code\n\n**Stage**: growing\n**Created**: 2026-04-22\n',
            encoding='utf-8',
        )
        archived_idea = tempdir / '_kb-ideas' / 'archive' / 'I-2026-01-01-old.md'
        archived_idea.parent.mkdir(parents=True, exist_ok=True)
        archived_idea.write_text(
            '# Idea: Old and archived\n\n**Stage**: archived\n', encoding='utf-8'
        )
        decision = tempdir / '_kb-decisions' / 'D-2026-04-22-cache-tier.md'
        decision.parent.mkdir(parents=True, exist_ok=True)
        decision.write_text(
            '# D-2026-04-22-cache-tier: Cache tiering shape\n\n'
            '- **Status**: gathering-evidence\n', encoding='utf-8'
        )
        note = tempdir / '_kb-notes' / '2026' / '04-22-review-sync.md'
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(
            '---\n'
            'type: meeting\n'
            'date: 2026-04-22\n'
            'authors: [@alice]\n'
            '---\n\n'
            '# Note: Review sync\n\n'
            '## TL;DR\n\n'
            'One visible promote and digest loop matters.\n',
            encoding='utf-8',
        )

        subprocess.run(
            [sys.executable, str(SCRIPT), str(tempdir), '--title', 'Simulated KB', '--description', 'Regression test'],
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
        assert_contains(output, '_kb-references/journeys/index.html')
        assert_not_contains(output, 'launch-journey.html')
        assert_not_contains(output, 'team-journey.html')
        assert_not_contains(output, 'mocks/index.html')
        assert_not_contains(output, 'launch-step-1-mock.html')

        # #21: markdown sources render with extracted titles and link to the .md.
        assert_contains(output, 'Cache hit rate drops on deploy')
        assert_contains(output, '2026-04-22-cache-hit-rate.md')
        assert_contains(output, 'Deployment strategy')
        assert_contains(output, 'deployment-strategy.md')
        assert_contains(output, 'Swarm-as-code')
        assert_contains(output, 'I-2026-04-22-swarm-as-code.md')
        assert_contains(output, 'Cache tiering shape')
        assert_contains(output, 'D-2026-04-22-cache-tier.md')
        assert_contains(output, 'Review sync')
        assert_contains(output, '04-22-review-sync.md')

        # #21: archived ideas must not leak into the public index.
        assert_not_contains(output, 'Old and archived')
        assert_not_contains(output, 'I-2026-01-01-old.md')

        # #21: category headings for markdown kinds exist.
        assert_contains(output, '<h2>Topics')
        assert_contains(output, '<h2>Notes')
        assert_contains(output, '<h2>Ideas')
        assert_contains(output, '<h2>Decisions')

        print('generate-index regression test: OK')
        return 0
    finally:
        shutil.rmtree(tempdir)


if __name__ == '__main__':
    raise SystemExit(main())
