#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "plugins" / "kb" / "skills" / "kb-roadmap" / "scripts" / "kb_roadmap.py"
DATE = "2026-05-08"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n").rstrip() + "\n", encoding="utf-8")


class RoadmapFixtureTests(unittest.TestCase):
    def test_export_backed_fixture_writes_triple_artifacts(self) -> None:
        tmpdir = Path(tempfile.mkdtemp(prefix="agentic-kb-roadmap-"))
        kb_root = tmpdir / "alice-kb"
        try:
            write(
                kb_root / ".kb-config" / "layers.yaml",
                f"""
                layers:
                  - name: alice-personal
                    path: .
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

            subprocess.run([sys.executable, str(SCRIPT), str(kb_root), "--date", DATE], cwd=REPO, check=True)

            output_dir = kb_root / "_kb-roadmaps" / "platform-signals"
            self.assertTrue((output_dir / f"roadmap-{DATE}.md").is_file())
            self.assertTrue((output_dir / f"roadmap-{DATE}.html").is_file())
            self.assertTrue((output_dir / f"roadmap-{DATE}.json").is_file())

            payload = json.loads((output_dir / f"roadmap-{DATE}.json").read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["correlated"], 1)
            self.assertEqual(payload["summary"]["total"], 3)
            self.assertEqual(payload["summary"]["single_tracker"], 1)
        finally:
            shutil.rmtree(tmpdir)

    def test_rollup_scope_refreshes_root_index(self) -> None:
        tmpdir = Path(tempfile.mkdtemp(prefix="agentic-kb-roadmap-rollup-"))
        kb_root = tmpdir / "kb"
        try:
            write(
                kb_root / ".kb-config" / "layers.yaml",
                f"""
                layers:
                  - name: personal
                    path: .
                    roadmap:
                      default-scope: product
                      output-dir: _kb-roadmaps
                      scopes:
                        product:
                          kind: detail
                          label: Product
                          description: Product detail scope.
                        exec:
                          kind: roll-up
                          label: Exec
                          description: Exec roll-up scope.
                          aggregates: [product]
                      plan-sources:
                        - name: plan-export
                          adapter: ticket-export-markdown
                          path: plan
                      delivery-sources:
                        - name: delivery-export
                          adapter: ticket-export-markdown
                          path: delivery
                      phases:
                        idea: []
                        defined: []
                        committed: []
                        in-delivery: [In Progress]
                        shipped: [Done]
                        archived: []
                """,
            )
            write(
                kb_root / "plan" / "ABC-101.md",
                """
                ---
                key: ABC-101
                summary: Planned item
                status: In Progress
                issueType: Story
                labels: [demo]
                ---
                # ABC-101: Planned item
                """,
            )
            write(
                kb_root / "delivery" / "ABC-101.md",
                """
                ---
                key: ABC-101
                summary: Delivered item
                status: Done
                issueType: Story
                labels: [demo]
                ---
                # ABC-101: Delivered item
                """,
            )

            subprocess.run([sys.executable, str(SCRIPT), str(kb_root), "--scope", "product", "--date", DATE], cwd=REPO, check=True)
            subprocess.run([sys.executable, str(SCRIPT), str(kb_root), "--scope", "exec", "--date", DATE], cwd=REPO, check=True)

            detail_json = json.loads((kb_root / "_kb-roadmaps" / "product" / f"roadmap-{DATE}.json").read_text(encoding="utf-8"))
            exec_json = json.loads((kb_root / "_kb-roadmaps" / "exec" / f"roadmap-exec-{DATE}.json").read_text(encoding="utf-8"))
            index_html = (kb_root / "_kb-roadmaps" / "index.html").read_text(encoding="utf-8")

            self.assertEqual(detail_json["summary"]["correlated"], 1)
            self.assertEqual(exec_json["summary"]["total"], 2)
            self.assertIn(f"product/roadmap-{DATE}.html", index_html)
            self.assertIn(f"exec/roadmap-exec-{DATE}.html", index_html)
        finally:
            shutil.rmtree(tmpdir)


if __name__ == "__main__":
    unittest.main()
