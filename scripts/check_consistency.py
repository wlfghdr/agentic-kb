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
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
IGNORED_PATH_PARTS = {".git", "node_modules", ".venv", "venv", "__pycache__"}

LONG_LIVED_DIRS: list[Path] = []
OPTIONAL_LONG_LIVED = [REPO / "docs" / "REFERENCE.md", REPO / "docs" / "glossary.md"]

# Files that are allowed to not have a version header.
EXEMPT_FROM_VERSION = {
    REPO / "docs" / "roadmap.md",
}

# Files whose version headers intentionally track a local document contract
# instead of the aggregate framework VERSION. Narrative examples that teach
# current behavior should not be added here unless they are deliberately
# release-pinned and the pin is named in the file.
VERSION_MINOR_DRIFT_ALLOWLIST = {
    REPO / "AGENTS.md",
    REPO / "CLAUDE.md",
    REPO / "docs" / "glossary.md",
    REPO / "docs" / "operating-model.md",
    REPO / "docs" / "role-handbook.md",
    REPO / "docs" / "uninstall.md",
    REPO / "plugins" / "kb" / "skills" / "kb-setup" / "references" / "adoption-stages.md",
    REPO / "plugins" / "kb" / "skills" / "kb-setup" / "references" / "github-governance-profile.md",
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

VERSION_RE = re.compile(r"\*\*Version:\*\*\s*(\d+)\.(\d+)(?:\.(\d+))?")
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
        if any(part in IGNORED_PATH_PARTS for part in p.parts):
            continue
        yield p


def parse_version(value: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", value.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def normalize_anchor(text: str) -> str:
    value = text.strip().lower()
    value = re.sub(r"[`*_~\[\](){}.!?,:;\"'\\]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def github_anchor(text: str) -> str:
    value = text.strip().lower()
    value = re.sub(r"\s", "-", value)
    value = re.sub(r"[`*_~\[\](){}.!?,:;\"'\\&]", "", value)
    return value.strip("-")


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

    root_version_path = REPO / "VERSION"
    if not root_version_path.is_file():
        return errors
    root_version = parse_version(root_version_path.read_text(encoding="utf-8"))
    if root_version is None:
        return errors
    root_minor = root_version[:2]

    for doc in iter_all_docs():
        if doc in VERSION_MINOR_DRIFT_ALLOWLIST:
            continue
        text = doc.read_text(encoding="utf-8", errors="ignore")
        match = VERSION_RE.search(text)
        if not match:
            continue
        doc_minor = (int(match.group(1)), int(match.group(2)))
        if doc_minor < root_minor:
            rel = doc.relative_to(REPO)
            doc_version = ".".join(part for part in match.groups() if part is not None)
            errors.append(
                f"VERSION header drift in {rel}: expected at least "
                f"{root_minor[0]}.{root_minor[1]}.x, got {doc_version}. "
                "Add a narrow allowlist entry only for intentionally pinned "
                "or independently versioned docs."
            )
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


def check_manifest_versions() -> list[str]:
    version_file = REPO / "VERSION"
    if not version_file.is_file():
        return []
    expected = version_file.read_text(encoding="utf-8").strip()
    checks = [
        (REPO / "plugin.json", ("version",)),
        (REPO / ".claude-plugin" / "marketplace.json", ("metadata", "version")),
        (REPO / "plugins" / "kb" / "plugin.json", ("version",)),
    ]
    errors: list[str] = []
    for path, key_path in checks:
        rel = path.relative_to(REPO)
        if not path.is_file():
            errors.append(f"MISSING manifest for version check: {rel}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"INVALID JSON for version check: {rel}: {exc}")
            continue
        value = data
        for key in key_path:
            if not isinstance(value, dict) or key not in value:
                errors.append(f"MISSING version field {'.'.join(key_path)} in: {rel}")
                value = None
                break
            value = value[key]
        if value is not None and value != expected:
            errors.append(f"VERSION drift in {rel}: expected {expected}, got {value}")

    marketplace = REPO / ".claude-plugin" / "marketplace.json"
    if marketplace.is_file():
        try:
            data = json.loads(marketplace.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
        for plugin in data.get("plugins", []) or []:
            if not isinstance(plugin, dict):
                continue
            if plugin.get("version") != expected:
                errors.append(
                    f"VERSION drift in .claude-plugin/marketplace.json plugin {plugin.get('name', '?')}: "
                    f"expected {expected}, got {plugin.get('version')!r}"
                )
    return errors


def check_forbidden_terms() -> list[str]:
    terms = FORBIDDEN_TERMS + _load_external_blocklist()
    if not terms:
        return []
    errors = []
    # Scan all text files that could leak vendor-specific language.
    exts = {".md", ".py", ".yaml", ".yml", ".html", ".json", ".sh", ".txt"}
    for p in REPO.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in exts:
            continue
        if any(part in IGNORED_PATH_PARTS for part in p.parts):
            continue
        rel = p.relative_to(REPO)
        # Skip the blocklist file itself and CI config.
        if rel.name == ".forbidden-terms.txt":
            continue
        text_lower = p.read_text(encoding="utf-8", errors="ignore").lower()
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
                    anchor
                    for m in HEADING_RE.finditer(txt)
                    for anchor in (normalize_anchor(m.group(1)), github_anchor(m.group(1)))
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
                if anchor not in headings_of(target) and normalize_anchor(anchor) not in headings_of(target):
                    errors.append(f"{rel} -> {raw} (anchor '{anchor}' missing)")
    return errors


def check_command_list_drift() -> list[str]:
    """Verify the /kb subcommand list does not drift between the dispatcher
    (`plugins/kb/commands/kb.md`) and the canonical command reference
    (`plugins/kb/skills/kb-management/references/command-reference.md`).

    Single source of truth: command-reference.md. The dispatcher's routing
    precedence list of explicit subcommands MUST be a subset of the verbs
    declared as subcommand rows in command-reference.md.
    """
    errors: list[str] = []
    dispatcher = REPO / "plugins" / "kb" / "commands" / "kb.md"
    reference = REPO / "plugins" / "kb" / "skills" / "kb-management" / "references" / "command-reference.md"
    if not dispatcher.is_file() or not reference.is_file():
        return errors

    # Extract from the dispatcher: the routing-precedence item 2 lists
    # explicit subcommands as a backtick-quoted comma-separated list inside
    # parentheses, e.g. (`review`, `promote`, `publish`, ...).
    dispatcher_text = dispatcher.read_text(encoding="utf-8")
    routing_match = re.search(
        r"Explicit subcommand[^\n]*\(([^)]+)\)",
        dispatcher_text,
    )
    if not routing_match:
        errors.append(
            "command-list drift: could not find the explicit-subcommand list "
            "in plugins/kb/commands/kb.md routing precedence"
        )
        return errors
    dispatcher_verbs = set(re.findall(r"`([a-z][a-z0-9-]*)`", routing_match.group(1)))

    # Extract from command-reference.md: every table row whose first cell
    # is a `/kb <verb>` or `/kb <verb> <subverb>` backtick-quoted command.
    reference_text = reference.read_text(encoding="utf-8")
    reference_verbs: set[str] = set()
    for m in re.finditer(r"^\|\s*`/kb\s+([a-z][a-z0-9-]*)", reference_text, re.MULTILINE):
        reference_verbs.add(m.group(1))
    # Also accept aliases declared in plain prose, e.g. "`/kb todo` and
    # `/kb tasks` are accepted aliases of `/kb task`."
    for m in re.finditer(r"`/kb\s+([a-z][a-z0-9-]*)`\s+(?:and|or)\s+`/kb\s+([a-z][a-z0-9-]*)`\s+(?:are\s+accepted\s+aliases|is\s+an?\s+alias)", reference_text):
        reference_verbs.add(m.group(1))
        reference_verbs.add(m.group(2))

    missing = sorted(dispatcher_verbs - reference_verbs)
    if missing:
        errors.append(
            "command-list drift: the dispatcher (plugins/kb/commands/kb.md) "
            f"routes verbs that are not documented in command-reference.md: {missing}. "
            "Either add them to command-reference.md or remove them from the dispatcher."
        )
    return errors


def main() -> int:
    all_errors: list[str] = []
    all_errors += check_root_version()
    all_errors += check_changelog_exists()
    all_errors += check_manifest_versions()
    all_errors += check_versions_and_changelogs()
    all_errors += check_forbidden_terms()
    all_errors += check_internal_links()
    all_errors += check_command_list_drift()

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
