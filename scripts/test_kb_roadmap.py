#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "plugins" / "kb" / "skills" / "kb-roadmap" / "scripts" / "kb_roadmap.py"


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"expected to find {needle!r}")


def write_ticket(path: Path, key: str, title: str, status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"""---
key: {key}
summary: {title}
status: {status}
issueType: Story
labels:
  - demo
---

# {key}: {title}
""",
        encoding="utf-8",
    )


def main() -> int:
    tempdir = Path(tempfile.mkdtemp(prefix="agentic-kb-roadmap-test-"))
    try:
        kb_root = tempdir / "kb"
        (kb_root / ".kb-config").mkdir(parents=True, exist_ok=True)
        write_ticket(kb_root / "plan" / "ABC-101.md", "ABC-101", "Planned item", "In Progress")
        write_ticket(kb_root / "delivery" / "ABC-101.md", "ABC-101", "Delivered item", "Done")

        (kb_root / ".kb-config" / "layers.yaml").write_text(
            """layers:
  personal:
    workstreams:
      - name: product
roadmap:
  default-scope: product
  output-dir: _kb-roadmaps
  scopes:
    product:
      kind: detail
      label: Product
      description: Product detail scope.
    exec:
      kind: roll-up
      label: Exec
      description: Exec roll-up scope.
      aggregates: [product]
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
    committed: []
    in-delivery: [In Progress]
    shipped: [Done]
    archived: []
""",
            encoding="utf-8",
        )

        subprocess.run(
            ["python3", str(SCRIPT), str(kb_root), "--scope", "product", "--date", "2026-05-08"],
            check=True,
            cwd=REPO,
        )
        subprocess.run(
            ["python3", str(SCRIPT), str(kb_root), "--scope", "exec", "--date", "2026-05-08"],
            check=True,
            cwd=REPO,
        )

        detail_json = json.loads(
            (kb_root / "_kb-roadmaps" / "product" / "roadmap-2026-05-08.json").read_text(encoding="utf-8")
        )
        exec_json = json.loads(
            (kb_root / "_kb-roadmaps" / "exec" / "roadmap-exec-2026-05-08.json").read_text(encoding="utf-8")
        )
        index_html = (kb_root / "_kb-roadmaps" / "index.html").read_text(encoding="utf-8")

        if detail_json["summary"]["correlated"] != 1:
            raise AssertionError(f"expected 1 correlated item, got {detail_json['summary']['correlated']}")
        if exec_json["summary"]["total"] != 2:
            raise AssertionError(f"expected roll-up total 2, got {exec_json['summary']['total']}")
        assert_contains(index_html, "product/roadmap-2026-05-08.html")
        assert_contains(index_html, "exec/roadmap-exec-2026-05-08.html")

        print("kb-roadmap regression test: OK")
        return 0
    finally:
        shutil.rmtree(tempdir)


if __name__ == "__main__":
    raise SystemExit(main())
