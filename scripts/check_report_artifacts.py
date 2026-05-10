#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = REPO / "plugins" / "kb" / "skills" / "kb-management"

TEMPLATES = {
    "report-status.md": {
        "metadata": [
            "**Report type**: status",
            "**Scope**:",
            "**Date**:",
            "**Audience**:",
            "**Owner**:",
            "**Cadence**:",
            "**Trigger**:",
            "**Approval**:",
        ],
        "sections": [
            "## Executive Summary",
            "## Progress by Workstream",
            "## Decisions and Asks",
            "## Risks and Blockers",
            "## Shared Artifact Links",
            "## Change Log",
        ],
    },
    "report-delivery.md": {
        "metadata": [
            "**Report type**: delivery",
            "**Scope**:",
            "**Date**:",
            "**Audience**:",
            "**Owner**:",
            "**Cadence**:",
            "**Trigger**:",
            "**Approval**:",
        ],
        "sections": [
            "## Delivery Summary",
            "## Commitments vs Reality",
            "## Newly Shipped / Newly At Risk",
            "## Traceability Gaps",
            "## Recommended Follow-through",
            "## Linked Shared Artifacts",
        ],
    },
    "report-roadmap-change.md": {
        "metadata": [
            "**Report type**: roadmap-change",
            "**Scope**:",
            "**Date**:",
            "**Audience**:",
            "**Owner**:",
            "**Cadence**: event-driven",
            "**Trigger**:",
            "**Approval required from**:",
            "**Approval status**:",
        ],
        "sections": [
            "## Change Summary",
            "## Baseline Change Table",
            "## Impact Review",
            "## Required Follow-up",
            "## Evidence and Links",
        ],
    },
}

DOC_EXPECTATIONS = {
    REPO / "docs" / "REFERENCE.md": [
        "_kb-references/reports/sources/<scope>/status-<scope>-YYYY-MM-DD.md",
        "_kb-references/reports/sources/<scope>/delivery-<scope>-YYYY-MM-DD.md",
        "_kb-references/reports/sources/<scope>/roadmap-change-<scope>-YYYY-MM-DD.md",
    ],
    REPO / "docs" / "collaboration.md": [
        "### Ownership and approval boundaries",
        "### Deterministic triggers",
        "### Feedback intake and KB loop",
    ],
    BASE / "references" / "html-artifacts.md": [
        "Canonical source path",
        "**Approval required from**",
    ],
    BASE / "references" / "command-reference.md": [
        "Canonical shared-report contract:",
        "roadmap-change may be opened automatically",
    ],
}


def check_templates() -> list[str]:
    errors: list[str] = []
    template_dir = BASE / "templates"
    for name, rules in TEMPLATES.items():
        path = template_dir / name
        if not path.is_file():
            errors.append(f"missing template: {path.relative_to(REPO)}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in rules["metadata"] + rules["sections"]:
            if needle not in text:
                errors.append(f"{path.relative_to(REPO)} missing {needle!r}")
    return errors


def check_docs() -> list[str]:
    errors: list[str] = []
    for path, needles in DOC_EXPECTATIONS.items():
        if not path.is_file():
            errors.append(f"missing doc: {path.relative_to(REPO)}")
            continue
        text = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{path.relative_to(REPO)} missing {needle!r}")
    return errors


def main() -> int:
    errors = check_templates() + check_docs()
    if errors:
        print("Shared report artifact check failed:\n")
        for error in errors:
            print(f"  ✗ {error}")
        print(f"\nTotal: {len(errors)} error(s).")
        return 1
    print("Shared report artifact check: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
