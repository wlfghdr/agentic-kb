#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parent.parent
ARCHIVE_SCRIPT = REPO / "plugins" / "kb" / "skills" / "kb-management" / "scripts" / "migrate_archives.py"
LAYER_SCRIPT = REPO / "plugins" / "kb" / "skills" / "kb-management" / "scripts" / "migrate_layer_model.py"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n").rstrip() + "\n", encoding="utf-8")


class MigrationScriptTests(unittest.TestCase):
    def test_archive_migrator_reports_and_applies_year_based_moves(self) -> None:
        tmpdir = Path(tempfile.mkdtemp(prefix="agentic-kb-migrate-archives-"))
        kb_root = tmpdir / "alice-kb"
        try:
            write(kb_root / "_kb-inputs" / "digested" / "2026-04" / "proof.md", "proof\n")
            write(kb_root / "_kb-tasks" / "archive" / "2026-04.md", "# Archive\n")
            write(kb_root / "_kb-decisions" / "archive" / "D-2026-04-24-proof.md", "# Decision\n")
            write(kb_root / "_kb-ideas" / "archive" / "I-2026-04-24-proof.md", "# Idea\n")
            write(kb_root / "_kb-references" / "findings" / "2026-04-24-proof.md", "# Finding\n")
            write(kb_root / ".kb-log" / "2026-04-24.log", "09:00:00Z | capture | personal | x | y\n")

            dry_run = subprocess.check_output(
                [sys.executable, str(ARCHIVE_SCRIPT), str(kb_root)],
                cwd=REPO,
                text=True,
            )
            self.assertIn("MOVE _kb-inputs/digested/2026-04/proof.md -> _kb-inputs/digested/2026/04/proof.md", dry_run)
            self.assertTrue((kb_root / "_kb-inputs" / "digested" / "2026-04" / "proof.md").exists())

            subprocess.run(
                [sys.executable, str(ARCHIVE_SCRIPT), str(kb_root), "--apply"],
                cwd=REPO,
                check=True,
            )

            self.assertTrue((kb_root / "_kb-inputs" / "digested" / "2026" / "04" / "proof.md").is_file())
            self.assertTrue((kb_root / "_kb-tasks" / "archive" / "2026" / "04.md").is_file())
            self.assertTrue((kb_root / "_kb-decisions" / "archive" / "2026" / "D-2026-04-24-proof.md").is_file())
            self.assertTrue((kb_root / "_kb-ideas" / "archive" / "2026" / "I-2026-04-24-proof.md").is_file())
            self.assertTrue((kb_root / "_kb-references" / "findings" / "2026" / "2026-04-24-proof.md").is_file())
            self.assertTrue((kb_root / ".kb-log" / "2026" / "2026-04-24.log").is_file())
        finally:
            shutil.rmtree(tmpdir)

    def test_layer_model_migrator_converts_legacy_schema(self) -> None:
        tmpdir = Path(tempfile.mkdtemp(prefix="agentic-kb-migrate-layers-"))
        kb_root = tmpdir / "alice-kb"
        try:
            write(
                kb_root / ".kb-config" / "layers.yaml",
                """
                workspace:
                  root: /tmp/demo
                  user: alice
                  aliases:
                    kb: alice-kb
                    tk: team-observability-kb

                layers:
                  personal:
                    path: .
                    workstreams:
                      - name: platform-signals
                        themes: [observability, reliability]
                  teams:
                    - name: team-observability
                      path: ../team-observability-kb
                      contributor-dir: alice
                  org-unit:
                    name: engineering-org
                    path: ../engineering-org-kb
                  marketplace:
                    enabled: true
                    repo: org/team-skills

                roadmap:
                  default-scope: platform-signals
                """,
            )

            dry_run = subprocess.check_output(
                [sys.executable, str(LAYER_SCRIPT), str(kb_root)],
                cwd=REPO,
                text=True,
            )
            self.assertIn("anchor-layer: personal", dry_run)
            self.assertIn("scope: team", dry_run)
            self.assertIn("default-scope: platform-signals", dry_run)

            subprocess.run(
                [sys.executable, str(LAYER_SCRIPT), str(kb_root), "--apply"],
                cwd=REPO,
                check=True,
            )

            migrated = yaml.safe_load((kb_root / ".kb-config" / "layers.yaml").read_text(encoding="utf-8"))
            self.assertEqual(migrated["workspace"]["anchor-layer"], "personal")
            self.assertIsInstance(migrated["layers"], list)

            personal = migrated["layers"][0]
            team = next(layer for layer in migrated["layers"] if layer["name"] == "team-observability")
            org = next(layer for layer in migrated["layers"] if layer["name"] == "engineering-org")

            self.assertEqual(personal["scope"], "personal")
            self.assertEqual(personal["parent"], "team-observability")
            self.assertIn("roadmap", personal)
            self.assertEqual(team["parent"], "engineering-org")
            self.assertEqual(org["marketplace"]["repo"], "org/team-skills")
        finally:
            shutil.rmtree(tmpdir)


if __name__ == "__main__":
    unittest.main()