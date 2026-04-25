#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
from pathlib import Path


DATE_IN_NAME_RE = re.compile(r"(20\d{2})-(\d{2})(?:-\d{2})?")
DECISION_RE = re.compile(r"D-(20\d{2})-\d{2}-\d{2}")
IDEA_RE = re.compile(r"I-(20\d{2})-\d{2}-\d{2}")
LOG_RE = re.compile(r"(20\d{2})-\d{2}-\d{2}\.log$")


def _year_from_path(path: Path) -> str:
    name = path.name
    for pattern in (DECISION_RE, IDEA_RE, LOG_RE):
        match = pattern.search(name)
        if match:
            return match.group(1)
    match = DATE_IN_NAME_RE.search(name)
    if match:
        return match.group(1)
    return str(dt.datetime.fromtimestamp(path.stat().st_mtime).year)


def _year_month_from_name(name: str) -> tuple[str, str] | None:
    match = re.fullmatch(r"(20\d{2})-(\d{2})", name)
    if not match:
        return None
    return match.group(1), match.group(2)


def collect_moves(kb_root: Path) -> list[tuple[Path, Path]]:
    moves: list[tuple[Path, Path]] = []

    digested_root = kb_root / "_kb-inputs" / "digested"
    if digested_root.is_dir():
        for child in sorted(digested_root.iterdir()):
            if not child.is_dir():
                continue
            parts = _year_month_from_name(child.name)
            if not parts:
                continue
            year, month = parts
            for file_path in sorted(child.rglob("*")):
                if not file_path.is_file():
                    continue
                rel = file_path.relative_to(child)
                moves.append((file_path, digested_root / year / month / rel))

    tasks_archive = kb_root / "_kb-tasks" / "archive"
    if tasks_archive.is_dir():
        for file_path in sorted(tasks_archive.glob("20??-??.md")):
            parts = _year_month_from_name(file_path.stem)
            if not parts:
                continue
            year, month = parts
            moves.append((file_path, tasks_archive / year / f"{month}.md"))

    for rel_root in (
        Path("_kb-decisions") / "archive",
        Path("_kb-ideas") / "archive",
        Path("_kb-references") / "findings",
        Path("_kb-references") / "strategy-digests",
        Path("_kb-notes"),
    ):
        root = kb_root / rel_root
        if not root.is_dir():
            continue
        for file_path in sorted(root.glob("*.md")):
            moves.append((file_path, root / _year_from_path(file_path) / file_path.name))
        for file_path in sorted(root.glob(".last*")):
            moves.append((file_path, root / _year_from_path(file_path) / file_path.name))

    log_root = kb_root / ".kb-log"
    if log_root.is_dir():
        for file_path in sorted(log_root.glob("20??-??-??.log")):
            moves.append((file_path, log_root / _year_from_path(file_path) / file_path.name))

    return [(src, dst) for src, dst in moves if src != dst and not dst.exists()]


def _git_root(path: Path) -> Path | None:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        return None
    return Path(out) if out else None


def _is_tracked(repo_root: Path, path: Path) -> bool:
    try:
        subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "--error-unmatch", str(path.relative_to(repo_root))],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return False
    return True


def apply_moves(moves: list[tuple[Path, Path]], kb_root: Path) -> None:
    repo_root = _git_root(kb_root)
    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if repo_root and src.exists() and _is_tracked(repo_root, src):
            subprocess.run(
                ["git", "-C", str(repo_root), "mv", str(src.relative_to(repo_root)), str(dst.relative_to(repo_root))],
                check=True,
            )
        else:
            src.rename(dst)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("kb_root", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    kb_root = args.kb_root.resolve()
    moves = collect_moves(kb_root)
    if not moves:
        print("kb-management: archive layout already matches the year-based structure")
        return 0

    print(f"kb-management: archive migration plan for {kb_root}")
    for src, dst in moves:
        print(f"MOVE {src.relative_to(kb_root)} -> {dst.relative_to(kb_root)}")

    if not args.apply:
        print("kb-management: dry-run only; re-run with --apply to move files")
        return 0

    apply_moves(moves, kb_root)
    print(f"kb-management: applied {len(moves)} archive move(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())