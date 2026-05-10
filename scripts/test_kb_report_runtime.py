#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROADMAP_SCRIPT = REPO / "plugins" / "kb" / "skills" / "kb-roadmap" / "scripts" / "kb_roadmap.py"
REPORT_SCRIPT = REPO / "plugins" / "kb" / "skills" / "kb-management" / "scripts" / "generate_report.py"


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected to find {needle!r}")


def write_ticket(path: Path, key: str, title: str, status: str, owner: str, target: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
key: {key}
summary: {title}
status: {status}
issueType: Story
assignee: {owner}
customFields:
  Sprint: {target}
labels:
  - demo
---

# {key}: {title}
""",
        encoding="utf-8",
    )


def write_decision(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """---
status: proposed
owner: product-lead
---

# D-2026-05-09 sequencing choice

Choose whether activation work stays in Q2.
""",
        encoding="utf-8",
    )


def write_journey(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        """# 1.1 — Activation Journey

#### Readiness
<span class=\"status-chip feasible\">Green</span> — Demo-ready.

### Step 1: Activate · `J1.1-S1` · `[WEB UI]`
The user activates the workspace.
""",
        encoding="utf-8",
    )


def write_finding(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# platform finding\n\nActivation is now critical-path.\n", encoding="utf-8")


def main() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="agentic-kb-report-runtime-test-"))
    try:
        kb_root = tempdir / "kb"
        (kb_root / ".kb-config").mkdir(parents=True, exist_ok=True)
        (kb_root / ".kb-config" / "layers.yaml").write_text(
            """layers:
  personal:
    workstreams:
      - name: platform
roadmap:
  default-scope: platform
  output-dir: _kb-roadmaps
  scopes:
    platform:
      kind: detail
      label: Platform
      description: Platform delivery scope.
      owner: product-lead
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
    committed: [Committed]
    in-delivery: [In Progress]
    shipped: [Done]
    archived: []
""",
            encoding="utf-8",
        )
        write_ticket(kb_root / "plan" / "PLAT-101.md", "PLAT-101", "Activation work", "Committed", "eng-lead", "2026 CQ2")
        write_ticket(kb_root / "delivery" / "PLAT-101.md", "PLAT-101", "Activation work", "In Progress", "eng-lead", "2026 CQ2")
        write_decision(kb_root / "_kb-decisions" / "D-2026-05-09-sequencing-choice.md")
        write_journey(kb_root / "_kb-journeys" / "1.1-activation.md")
        write_finding(kb_root / "findings" / "2026-05-09-platform-activation.md")

        subprocess.run(["python3", str(ROADMAP_SCRIPT), str(kb_root), "--scope", "platform", "--date", "2026-05-08"], check=True, cwd=REPO)

        write_ticket(kb_root / "plan" / "PLAT-101.md", "PLAT-101", "Activation work", "In Progress", "eng-lead", "2026 CQ3")
        write_ticket(kb_root / "delivery" / "PLAT-102.md", "PLAT-102", "Invite fallback", "Done", "eng-lead", "2026 CQ2")

        subprocess.run(["python3", str(ROADMAP_SCRIPT), str(kb_root), "--scope", "platform", "--date", "2026-05-10"], check=True, cwd=REPO)

        for report_type in ("delivery", "roadmap-change", "status"):
            subprocess.run(["python3", str(REPORT_SCRIPT), str(kb_root), report_type, "platform", "--date", "2026-05-10"], check=True, cwd=REPO)

        delivery_md = (kb_root / "_kb-references" / "reports" / "sources" / "platform" / "delivery-platform-2026-05-10.md").read_text(encoding="utf-8")
        roadmap_change_md = (kb_root / "_kb-references" / "reports" / "sources" / "platform" / "roadmap-change-platform-2026-05-10.md").read_text(encoding="utf-8")
        status_md = (kb_root / "_kb-references" / "reports" / "sources" / "platform" / "status-platform-2026-05-10.md").read_text(encoding="utf-8")
        delivery_html = (kb_root / "_kb-references" / "reports" / "delivery-platform-2026-05-10.html").read_text(encoding="utf-8")

        assert_contains(delivery_md, "**Report type**: delivery")
        assert_contains(delivery_md, "PLAT-101 Activation work")
        assert_contains(delivery_md, "_kb-roadmaps/platform/roadmap-2026-05-10.json")
        assert_contains(roadmap_change_md, "**Report type**: roadmap-change")
        assert_contains(roadmap_change_md, "phase-change")
        assert_contains(roadmap_change_md, "milestone-change")
        assert_contains(status_md, "**Report type**: status")
        assert_contains(status_md, "delivery-platform-2026-05-10")
        assert_contains(delivery_html, "delivery")
        assert_contains(delivery_html, "Activation work")

        print("kb-report runtime integration test: OK")
        return 0
    finally:
        shutil.rmtree(tempdir)


if __name__ == "__main__":
    raise SystemExit(main())
