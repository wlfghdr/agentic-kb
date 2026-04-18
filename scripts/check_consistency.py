#!/usr/bin/env python3
"""
Consistency + version + vendor-neutrality checks for the agentic-kb spec.

Fails CI if:
  - any long-lived spec/concept doc is missing a `## Changelog` section
  - any long-lived doc is missing a `**Version:**` field
  - the root VERSION file is missing or not in X.Y.Z form
  - any spec doc contains a forbidden vendor-specific term
  - any internal markdown link is broken
  - any referenced heading anchor does not exist
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

LONG_LIVED_DIRS: list[Path] = []
OPTIONAL_LONG_LIVED = [REPO / "docs" / "REFERENCE.md", REPO / "docs" / "glossary.md"]

# Files that are allowed to not have a version header — narrative walkthroughs,
# examples, and standalone index files.
EXEMPT_FROM_VERSION = {
    REPO / "docs" / "examples" / "day-in-the-life.md",
    REPO / "docs" / "roadmap.md",
}

# Terms we forbid in the public spec.
#
# By default this list is empty — the spec is vendor-neutral and does not
# know which terms are "your" internal terms to keep out. Maintainers and
# forks who want to enforce a blocklist should drop a newline-separated
# list into `.forbidden-terms.txt` at the repo root (gitignored by default).
# That lets organizations layer their own internal vocabulary on top without
# that vocabulary ever appearing in the public spec itself.
FORBIDDEN_TERMS: list[str] = []


def _load_external_blocklist() -> list[str]:
    path = REPO / ".forbidden-terms.txt"
    if not path.is_file():
        return []
    terms: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        terms.append(line.lower())
    return terms

VERSION_RE = re.compile(r"\*\*Version:\*\*\s*(\d+)\.(\d+)")
CHANGELOG_RE = re.compile(r"^##\s+Changelog\s*$", re.MULTILINE)
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
INLINE_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def iter_long_lived_docs():
    for d in LONG_LIVED_DIRS:
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            yield p
    for p in OPTIONAL_LONG_LIVED:
        if p.is_file():
            yield p


def iter_all_docs():
    for p in REPO.rglob("*.md"):
        if any(part in {".git", "node_modules", "plugins"} for part in p.parts):
            continue
        yield p


def normalize_anchor(text: str) -> str:
    value = text.strip().lower()
    value = re.sub(r"[`*_~\[\](){}.!?,:;\"'\\]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def is_external(target: str) -> bool:
    lower = target.lower()
    return any(
        lower.startswith(p)
        for p in ("http://", "https://", "mailto:", "tel:", "ftp://")
    )


def check_versions_and_changelogs() -> list[str]:
    errors = []
    for doc in iter_long_lived_docs():
        text = doc.read_text(encoding="utf-8")
        rel = doc.relative_to(REPO)
        if doc not in EXEMPT_FROM_VERSION and not VERSION_RE.search(text):
            errors.append(f"MISSING **Version:** field: {rel}")
        if not CHANGELOG_RE.search(text):
            errors.append(f"MISSING '## Changelog' section: {rel}")
    return errors


def check_root_version() -> list[str]:
    v = REPO / "VERSION"
    if not v.is_file():
        return ["MISSING: VERSION file at repo root"]
    content = v.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+", content):
        return [f"VERSION must be X.Y.Z, got: {content!r}"]
    return []


def check_changelog_exists() -> list[str]:
    c = REPO / "CHANGELOG.md"
    if not c.is_file():
        return ["MISSING: CHANGELOG.md at repo root"]
    text = c.read_text(encoding="utf-8")
    if "[Unreleased]" not in text:
        return ["CHANGELOG.md must contain an '[Unreleased]' section header"]
    return []


def check_forbidden_terms() -> list[str]:
    terms = FORBIDDEN_TERMS + _load_external_blocklist()
    if not terms:
        return []
    errors = []
    for doc in iter_all_docs():
        rel = doc.relative_to(REPO)
        text_lower = doc.read_text(encoding="utf-8").lower()
        for term in terms:
            if term in text_lower:
                errors.append(f"FORBIDDEN term '{term}' in: {rel}")
    return errors


def check_internal_links() -> list[str]:
    errors = []
    heading_cache: dict[Path, set[str]] = {}

    def headings_of(p: Path) -> set[str]:
        if p not in heading_cache:
            if not p.is_file():
                heading_cache[p] = set()
            else:
                txt = p.read_text(encoding="utf-8", errors="ignore")
                heading_cache[p] = {
                    normalize_anchor(m.group(1)) for m in HEADING_RE.finditer(txt)
                }
        return heading_cache[p]

    for doc in iter_all_docs():
        rel = doc.relative_to(REPO)
        text = doc.read_text(encoding="utf-8", errors="ignore")
        for match in INLINE_LINK_RE.finditer(text):
            raw = match.group(1).strip()
            if not raw or is_external(raw):
                continue
            if raw.startswith("<") and raw.endswith(">"):
                raw = raw[1:-1].strip()
            # Drop title text after whitespace: [text](path "title")
            if " " in raw:
                raw = raw.split(" ", 1)[0]
            # Skip templated placeholders
            if "{{" in raw or "{" in raw and "}" in raw:
                continue
            path_part, _, anchor = raw.partition("#")
            if path_part == "":
                target = doc
            elif path_part.startswith("/"):
                target = REPO / path_part.lstrip("/")
            else:
                target = (doc.parent / path_part).resolve()
            try:
                target.relative_to(REPO)
            except ValueError:
                errors.append(f"{rel} -> {raw} (escapes repo)")
                continue
            if not target.exists():
                errors.append(f"{rel} -> {raw} (target missing)")
                continue
            if anchor and target.suffix.lower() == ".md":
                if normalize_anchor(anchor) not in headings_of(target):
                    errors.append(f"{rel} -> {raw} (anchor '{anchor}' missing)")
    return errors


def main() -> int:
    all_errors: list[str] = []
    all_errors += check_root_version()
    all_errors += check_changelog_exists()
    all_errors += check_versions_and_changelogs()
    all_errors += check_forbidden_terms()
    all_errors += check_internal_links()

    if all_errors:
        print("Consistency check failed:\n")
        for e in all_errors:
            print(f"  ✗ {e}")
        print(f"\nTotal: {len(all_errors)} error(s).")
        return 1

    print("Consistency check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
