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


if __name__ == "__main__":
    unittest.main()
