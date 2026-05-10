#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "scaffold_acceptance_fixture.py"
DATE = "2026-04-24"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


class AcceptanceFixtureTests(unittest.TestCase):
    def test_scaffolded_workspace_covers_harness_and_layer_contracts(self) -> None:
        tmpdir = Path(tempfile.mkdtemp(prefix="agentic-kb-acceptance-"))
        workspace = tmpdir / "workspace"
        try:
            subprocess.run([sys.executable, str(SCRIPT), str(workspace)], cwd=REPO, check=True)

            for path in (
                workspace / ".claude" / "commands" / "kb.md",
                workspace / ".github" / "prompts" / "kb.prompt.md",
                workspace / ".github" / "instructions" / "kb.instructions.md",
                workspace / ".opencode" / "commands" / "kb.md",
                workspace / ".gemini" / "commands" / "kb.toml",
                workspace / ".kiro" / "skills" / "kb" / "SKILL.md",
                workspace / ".agents" / "skills" / "kb" / "SKILL.md",
            ):
                self.assertTrue(path.exists(), path)

            for path in (
                workspace / ".claude" / "commands" / "kb.md",
                workspace / ".opencode" / "commands" / "kb.md",
                workspace / ".gemini" / "commands" / "kb.toml",
                workspace / ".kiro" / "skills" / "kb" / "SKILL.md",
                workspace / ".agents" / "skills" / "kb" / "SKILL.md",
            ):
                content = read(path)
                self.assertNotIn("Configure Chat", content, path)
                self.assertNotIn("vscode_askQuestions", content, path)

            personal = workspace / "alice-kb"
            team = workspace / "team-observability-kb"
            org = workspace / "engineering-org-kb"
            company = workspace / "company-enablement-kb"
            for path in (
                personal / "index.html",
                personal / "dashboard.html",
                team / "index.html",
                team / "dashboard.html",
                org / "index.html",
                org / "dashboard.html",
                company / "index.html",
                company / "dashboard.html",
                personal / "_kb-references" / "reports" / f"{DATE}-personal-brief-v1-0.html",
                personal / "_kb-references" / "reports" / f"progress-{DATE}-platform-signals-v1-0.html",
                team / "reports" / f"{DATE}-team-review-v1-0.html",
                org / "reports" / f"{DATE}-org-brief-v1-0.html",
                company / "reports" / f"{DATE}-company-brief-v1-0.html",
            ):
                self.assertTrue(path.exists(), path)

            for path in (
                personal / "_kb-notes" / "2026" / "04-24-adoption-sync.md",
                personal / "_kb-references" / "findings" / "2026" / "2026-04-24-proof-strip.md",
                personal / "_kb-inputs" / "digested" / "2026" / "04" / ".gitkeep",
                personal / "_kb-tasks" / "archive" / "2026" / "04.md",
                personal / "_kb-decisions" / "archive" / "2026" / ".gitkeep",
                personal / "_kb-ideas" / "archive" / "2026" / ".gitkeep",
                personal / "_kb-references" / "strategy-digests" / "2026" / ".last-progress-platform-signals",
                team / "_kb-notes" / "2026" / "04-24-review.md",
            ):
                self.assertTrue(path.exists(), path)

            layers = read(personal / ".kb-config" / "layers.yaml")
            self.assertIn("scope: personal", layers)
            self.assertIn("scope: team", layers)
            self.assertIn("scope: org-unit", layers)
            self.assertIn("scope: company", layers)
            self.assertIn("role: consumer", layers)
            self.assertIn("features: [inputs, findings, topics, ideas, decisions, tasks, workstreams, foundation, reports, notes]", layers)
            self.assertIn("connections:", layers)
            self.assertIn("trackers:", layers)
            self.assertIn("marketplace:", layers)

            dashboard = read(personal / "dashboard.html")
            self.assertIn("Focus", dashboard)
            self.assertIn("Active Ideas", dashboard)
            self.assertIn("Open Decisions", dashboard)
            self.assertIn("Topics", dashboard)

            for report in (
                personal / "_kb-references" / "reports" / f"{DATE}-personal-brief-v1-0.html",
                personal / "_kb-references" / "reports" / f"progress-{DATE}-platform-signals-v1-0.html",
                team / "reports" / f"{DATE}-team-review-v1-0.html",
                org / "reports" / f"{DATE}-org-brief-v1-0.html",
                company / "reports" / f"{DATE}-company-brief-v1-0.html",
            ):
                html = read(report)
                self.assertIn('data-theme="dark"', html)
                self.assertIn('[data-theme="light"]', html)
                self.assertIn("Changelog", html)
                self.assertNotIn("fonts.googleapis.com", html)
                self.assertNotIn("@import url(", html)

            self.assertIn("Proof strip matters", read(personal / "index.html"))
            self.assertIn("Note: Adoption sync", read(personal / "index.html"))

            remotes = workspace / "git-remotes"
            clone_dir = tmpdir / "team-clone"
            subprocess.run(["git", "clone", str(remotes / "team-observability-kb.git"), str(clone_dir)], check=True)
            self.assertEqual(git(clone_dir, "branch", "--show-current"), "main")
            self.assertTrue(git(personal, "remote", "get-url", "origin").endswith("alice-kb.git"))
        finally:
            shutil.rmtree(tmpdir)


if __name__ == "__main__":
    unittest.main()