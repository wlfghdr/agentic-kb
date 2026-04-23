#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("install.py")
SPEC = importlib.util.spec_from_file_location("agentic_kb_install", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
install = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(install)


def write_skill(path: Path, version: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                "name: sample-skill",
                f"version: {version}",
                "---",
                "",
                "# Sample",
                "",
            ]
        ),
        encoding="utf-8",
    )


class InstallDriftDetectionTests(unittest.TestCase):
    def test_existing_copy_reports_up_to_date_when_versions_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src-skill"
            dst = root / "dst-skill"
            write_skill(src, "1.2.3")

            original_is_windows = install.IS_WINDOWS
            install.IS_WINDOWS = True
            try:
                install.link_or_copy(src, dst, force=False)
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    install.link_or_copy(src, dst, force=False)
            finally:
                install.IS_WINDOWS = original_is_windows

            self.assertIn(f"up-to-date (v1.2.3): {dst}", buf.getvalue())

    def test_existing_copy_reports_stale_and_keeps_old_contents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src-skill"
            dst = root / "dst-skill"
            write_skill(src, "1.0.0")

            original_is_windows = install.IS_WINDOWS
            install.IS_WINDOWS = True
            try:
                install.link_or_copy(src, dst, force=False)
                write_skill(src, "1.1.0")
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    install.link_or_copy(src, dst, force=False)
            finally:
                install.IS_WINDOWS = original_is_windows

            self.assertIn(
                f"stale (v1.0.0 -> v1.1.0): {dst} (run with --force to reinstall / update)",
                buf.getvalue(),
            )
            self.assertIn("version: 1.0.0", (dst / "SKILL.md").read_text(encoding="utf-8"))

    def test_unversioned_existing_file_prints_force_tip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "kb.prompt.md"
            dst = root / "installed.prompt.md"
            src.write_text("# Prompt\n", encoding="utf-8")

            original_is_windows = install.IS_WINDOWS
            install.IS_WINDOWS = True
            try:
                install.link_or_copy(src, dst, force=False)
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    install.link_or_copy(src, dst, force=False)
            finally:
                install.IS_WINDOWS = original_is_windows

            self.assertIn(
                f"skip (exists): {dst} (run with --force to reinstall / update)",
                buf.getvalue(),
            )


class MultiHarnessInstallTests(unittest.TestCase):
    """Smoke tests for the codex/gemini/kiro install paths."""

    def _sample_command(self, root: Path) -> tuple[str, Path]:
        src = root / "kb.prompt.md"
        src.write_text(
            "---\n"
            "mode: agent\n"
            'description: KB ops — capture, digest, promote\n'
            "---\n"
            "\n"
            "# /kb — Knowledge Base\n"
            "\n"
            "Route to kb-management.\n",
            encoding="utf-8",
        )
        return ("kb", src)

    def test_codex_writes_md_with_frontmatter_stripped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install.install_codex(root, [self._sample_command(root)], force=False)
            dst = root / "prompts" / "kb.md"
            self.assertTrue(dst.is_file())
            content = dst.read_text(encoding="utf-8")
            self.assertNotIn("---\nmode:", content)
            self.assertIn("# /kb — Knowledge Base", content)

    def test_gemini_generates_toml_wrapper_with_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install.install_gemini(root, [self._sample_command(root)], force=False)
            dst = root / "commands" / "kb.toml"
            self.assertTrue(dst.is_file())
            content = dst.read_text(encoding="utf-8")
            self.assertIn('description = "KB ops', content)
            self.assertIn('prompt = """', content)
            self.assertIn("# /kb — Knowledge Base", content)

    def test_kiro_copies_md_verbatim_into_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            install.install_kiro(root, [self._sample_command(root)], force=False)
            dst = root / "agents" / "kb.md"
            self.assertTrue(dst.exists())
            content = dst.read_text(encoding="utf-8")
            # Kiro keeps frontmatter and body intact — it ignores unknown keys.
            self.assertIn("mode: agent", content)
            self.assertIn("# /kb — Knowledge Base", content)

    def test_detect_targets_discovers_new_harnesses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            import os
            cwd = os.getcwd()
            try:
                os.chdir(tmp)
                for sub in (".codex", ".gemini", ".kiro"):
                    Path(tmp, sub).mkdir()
                hits = set(install.detect_targets())
            finally:
                os.chdir(cwd)
            # codex detect only probes ~/.codex, so it's environment-dependent;
            # gemini + kiro have local probes and MUST be picked up.
            self.assertIn("gemini", hits)
            self.assertIn("kiro", hits)


if __name__ == "__main__":
    unittest.main()
