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


def write_ticket(path: Path, key: str, title: str, status: str, owner: str, target: str, body: str = "") -> None:
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
{body}
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


def write_journey(path: Path, title: str, readiness: str, step_id: str, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""# {title}

#### Readiness
{readiness}

### Step 1: {body} · `{step_id}` · `[WEB UI]`
{body}
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
        write_ticket(kb_root / "plan" / "PLAT-101.md", "PLAT-101", "Activation work", "Committed", "eng-lead", "2026 CQ2", "journey: J1.1-S1")
        write_ticket(kb_root / "delivery" / "PLAT-101.md", "PLAT-101", "Activation work", "In Progress", "eng-lead", "2026 CQ2", "journey: J1.1-S1")
        write_ticket(kb_root / "plan" / "PLAT-201.md", "PLAT-201", "Billing follow-up", "Committed", "eng-lead", "2026 CQ2")
        write_ticket(kb_root / "delivery" / "PLAT-201.md", "PLAT-201", "Billing follow-up", "Done", "eng-lead", "2026 CQ2")
        write_ticket(kb_root / "plan" / "PLAT-301.md", "PLAT-301", "Merge-safe delivery signal", "Done", "eng-lead", "2026 CQ2", "journey: J1.1-S1")
        write_ticket(kb_root / "delivery" / "PLAT-301.md", "PLAT-301", "Merge-safe delivery signal", "In Progress", "eng-lead", "2026 CQ2")
        write_ticket(kb_root / "plan" / "PLAT-401.md", "PLAT-401", "Delivery-side journey citation", "Committed", "eng-lead", "2026 CQ2")
        write_ticket(kb_root / "delivery" / "PLAT-401.md", "PLAT-401", "Delivery-side journey citation", "In Progress", "eng-lead", "2026 CQ2", "journey: J1.2-S2")
        write_decision(kb_root / "_kb-decisions" / "D-2026-05-09-sequencing-choice.md")
        write_journey(kb_root / "_kb-journeys" / "1.1-activation.md", "1.1 — Activation Journey", '<span class="status-chip feasible">Green</span> — Demo-ready.', "J1.1-S1", "The user activates the workspace.")
        write_journey(kb_root / "_kb-journeys" / "1.2-billing.md", "1.2 — Billing Journey", '<span class="status-chip blocked">Red</span> — Needs fixes.', "J1.2-S2", "The user updates billing details.")
        write_finding(kb_root / "findings" / "2026-05-09-platform-activation.md")

        subprocess.run(["python3", str(ROADMAP_SCRIPT), str(kb_root), "--scope", "platform", "--date", "2026-05-08"], check=True, cwd=REPO)

        write_ticket(kb_root / "plan" / "PLAT-101.md", "PLAT-101", "Activation work", "In Progress", "eng-lead-2", "2026 CQ3", "journey: J1.1-S1")
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
        assert_contains(delivery_md, "PLAT-201 Billing follow-up")
        assert_contains(delivery_md, "PLAT-301 Merge-safe delivery signal")
        assert_contains(delivery_md, "PLAT-401 Delivery-side journey citation")
        assert delivery_md.count("| PLAT-101 Activation work | in-delivery | J1.1-S1 | In Progress | on-track | Mapped from explicit step citation in 1.1-activation.md |") == 1, delivery_md
        assert_contains(delivery_md, "| PLAT-201 Billing follow-up | shipped | n/a | shipped (delivery-export) | shipped | No explicit journey-step mapping found; linkage remains absent |")
        assert_contains(delivery_md, "| PLAT-301 Merge-safe delivery signal | in-delivery | J1.1-S1 | In Progress | on-track | Mapped from explicit step citation in 1.1-activation.md |")
        assert_contains(delivery_md, "| PLAT-401 Delivery-side journey citation | in-delivery | J1.2-S2 | In Progress | on-track | Mapped from explicit step citation in 1.2-billing.md |")
        assert_contains(delivery_md, "2 commitment(s) have no explicit journey-step citation")
        assert_contains(delivery_md, "_kb-roadmaps/platform/roadmap-2026-05-10.json")
        assert_contains(roadmap_change_md, "**Report type**: roadmap-change")
        assert_contains(roadmap_change_md, "**Approval status**: draft")
        assert_contains(roadmap_change_md, "phase-change | PLAT-101 | committed | in-delivery")
        assert_contains(roadmap_change_md, "milestone-change | PLAT-101 | 2026 CQ2 | 2026 CQ3")
        assert_contains(roadmap_change_md, "ownership-change | PLAT-101 | eng-lead | eng-lead-2")
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
