#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "plugins" / "kb" / "skills" / "kb-roadmap" / "scripts" / "kb_roadmap.py"
DATE = "2026-04-24"
EXTERNAL_RESOURCE_RE = re.compile(
    r"<(?:script|link)[^>]*\s(?:src|href)\s*=\s*['\"](https?:|//)[^'\"]+['\"]",
    re.IGNORECASE,
)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n").rstrip() + "\n", encoding="utf-8")


class RoadmapFixtureTests(unittest.TestCase):
    def test_export_backed_roadmap_fixture_writes_triple_artifacts(self) -> None:
        tmpdir = Path(tempfile.mkdtemp(prefix="agentic-kb-roadmap-"))
        kb_root = tmpdir / "alice-kb"
        try:
            write(
                kb_root / ".kb-config" / "layers.yaml",
                """
                roadmap:
                  default-scope: platform-signals
                  output-dir: _kb-roadmaps
                  issue-trackers:
                    - name: jira-export
                      adapter: ticket-export-markdown
                      config:
                        path: exports/jira
                    - name: github-export
                      adapter: ticket-export-markdown
                      config:
                        path: exports/github
                  scopes:
                    platform-signals:
                      kind: detail
                      trackers:
                        - tracker: jira-export
                        - tracker: github-export
                  phases:
                    idea: [Backlog]
                    defined: [Defined]
                    committed: [Committed]
                    in-delivery: [In Progress]
                    shipped: [Done, Closed]
                """,
            )
            write(
                kb_root / "exports" / "jira" / "PROD-100.md",
                """
                ---
                key: PROD-100
                summary: Platform signals rollout
                status: Committed
                issueType: Initiative
                labels:
                  - workstream:platform-signals
                ---
                # PROD-100: Platform signals rollout
                """,
            )
            write(
                kb_root / "exports" / "jira" / "PROD-101.md",
                """
                ---
                key: PROD-101
                summary: Export-backed roadmap proof path
                status: In Progress
                issueType: Story
                labels:
                  - workstream:platform-signals
                ---
                # PROD-101: Export-backed roadmap proof path

                ## Parent
                - **PROD-100**
                """,
            )
            write(
                kb_root / "exports" / "github" / "PROD-101.md",
                """
                ---
                key: PROD-101
                summary: GitHub mirror of roadmap proof work
                status: In Progress
                issueType: Issue
                labels:
                  - workstream:platform-signals
                ---
                # GitHub mirror of roadmap proof work
                """,
            )
            write(
                kb_root / "exports" / "github" / "PROD-102.md",
                """
                ---
                key: PROD-102
                summary: Follow-up cleanups
                status: Backlog
                issueType: Issue
                labels:
                  - workstream:platform-signals
                ---
                # Follow-up cleanups
                """,
            )

            subprocess.run(
                [sys.executable, str(SCRIPT), str(kb_root), "--date", DATE],
                cwd=REPO,
                check=True,
            )

            output_dir = kb_root / "_kb-roadmaps" / "platform-signals"
            md_path = output_dir / f"roadmap-{DATE}.md"
            html_path = output_dir / f"roadmap-{DATE}.html"
            json_path = output_dir / f"roadmap-{DATE}.json"

            self.assertTrue(md_path.is_file())
            self.assertTrue(html_path.is_file())
            self.assertTrue(json_path.is_file())

            md = md_path.read_text(encoding="utf-8")
            html = html_path.read_text(encoding="utf-8")
            payload = json.loads(json_path.read_text(encoding="utf-8"))

            self.assertIn("## C. Correlation matrix", md)
            self.assertIn("## G. Decisions needed", md)
            self.assertIn("PROD-101", md)

            self.assertIn('data-theme="auto"', html)
            self.assertIn("Timeline", html)
            self.assertIn("Status board", html)
            self.assertNotRegex(html, EXTERNAL_RESOURCE_RE)

            self.assertEqual(payload["scope"], "platform-signals")
            self.assertEqual(payload["summary"]["total"], 4)
            self.assertEqual(payload["summary"]["correlated"], 1)
            self.assertEqual(payload["summary"]["single_tracker"], 2)

            correlation = next(item for item in payload["correlations"] if item["id"] == "PROD-101")
            self.assertEqual(correlation["appearances"], 2)
            self.assertEqual(correlation["trackers"], ["github-export", "jira-export"])
        finally:
            shutil.rmtree(tmpdir)


if __name__ == "__main__":
    unittest.main()