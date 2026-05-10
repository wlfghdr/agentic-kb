#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    import yaml  # type: ignore
except ImportError:
    raise SystemExit("generate_report.py requires PyYAML")

REPO = Path(__file__).resolve().parents[5]
BASE = REPO / "plugins" / "kb" / "skills" / "kb-management"
TEMPLATE_DIR = BASE / "templates"


@dataclass
class JourneySignal:
    path: Path
    title: str
    readiness: str
    step_ids: list[str]


@dataclass
class ReportContext:
    kb_root: Path
    scope: str
    date: str
    report_type: str
    cfg: dict
    roadmap_json: dict | None
    roadmap_json_path: Path | None
    previous_roadmap_json: dict | None
    previous_roadmap_json_path: Path | None
    journeys: list[JourneySignal]
    decisions: list[dict]
    findings: list[Path]
    reports_root: Path
    sources_dir: Path
    html_dir: Path


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def resolve_layers_config(kb_root: Path) -> Path:
    candidate = kb_root / ".kb-config" / "layers.yaml"
    if candidate.exists():
        return candidate
    legacy = kb_root / ".kb-config.yaml"
    if legacy.exists():
        return legacy
    raise SystemExit("missing .kb-config/layers.yaml")


def latest_matching(paths: Iterable[Path]) -> list[Path]:
    return sorted(paths, key=lambda p: p.name)


def find_roadmap_snapshots(kb_root: Path, scope: str) -> list[Path]:
    roadmap_dir = kb_root / "_kb-roadmaps" / scope
    if not roadmap_dir.exists():
        return []
    return latest_matching(roadmap_dir.glob("roadmap*.json"))


def load_roadmap_json(path: Path | None) -> dict | None:
    if not path or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def parse_journeys(kb_root: Path) -> list[JourneySignal]:
    root = kb_root / "_kb-journeys"
    if not root.exists():
        return []
    signals: list[JourneySignal] = []
    for path in sorted(root.glob("*.md")):
        if path.name == "overview.md":
            continue
        text = path.read_text(encoding="utf-8")
        title = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        readiness_matches = re.findall(r"#### Readiness\s*\n(?:.+\n)?([^\n]+)", text)
        readiness = readiness_matches[0].strip() if readiness_matches else "unknown"
        step_ids = re.findall(r"`([^`]+)`", text)
        signals.append(JourneySignal(path=path, title=title.group(1).strip() if title else path.stem, readiness=readiness, step_ids=step_ids))
    return signals


def parse_decisions(kb_root: Path) -> list[dict]:
    decisions_dir = kb_root / "_kb-decisions"
    if not decisions_dir.exists():
        return []
    out: list[dict] = []
    for path in sorted(decisions_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        status_m = re.search(r"^status:\s*(.+)$", text, re.MULTILINE)
        owner_m = re.search(r"^owner:\s*(.+)$", text, re.MULTILINE)
        title_m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        out.append({
            "path": path,
            "status": status_m.group(1).strip() if status_m else "unknown",
            "owner": owner_m.group(1).strip() if owner_m else "unassigned",
            "title": title_m.group(1).strip() if title_m else path.stem,
        })
    return out


def discover_findings(kb_root: Path, scope: str) -> list[Path]:
    findings_dir = kb_root / "findings"
    if not findings_dir.exists():
        return []
    lowered = scope.lower()
    matches = [p for p in sorted(findings_dir.glob("*.md")) if lowered in p.stem.lower()]
    return matches[-5:]


def build_context(kb_root: Path, scope: str, report_type: str, date: str) -> ReportContext:
    cfg = load_yaml(resolve_layers_config(kb_root))
    snapshots = find_roadmap_snapshots(kb_root, scope)
    current = snapshots[-1] if snapshots else None
    previous = snapshots[-2] if len(snapshots) > 1 else None
    reports_root = kb_root / "_kb-references" / "reports"
    return ReportContext(
        kb_root=kb_root,
        scope=scope,
        date=date,
        report_type=report_type,
        cfg=cfg,
        roadmap_json=load_roadmap_json(current),
        roadmap_json_path=current,
        previous_roadmap_json=load_roadmap_json(previous),
        previous_roadmap_json_path=previous,
        journeys=parse_journeys(kb_root),
        decisions=parse_decisions(kb_root),
        findings=discover_findings(kb_root, scope),
        reports_root=reports_root,
        sources_dir=reports_root / "sources" / scope,
        html_dir=reports_root,
    )


def roadmap_items(ctx: ReportContext) -> list[dict]:
    if not ctx.roadmap_json:
        return []
    return list(ctx.roadmap_json.get("items", []))


def by_id(items: list[dict]) -> dict[str, dict]:
    return {str(item.get("id")): item for item in items}


def summarize_readiness(ctx: ReportContext) -> tuple[int, int]:
    ready = 0
    risky = 0
    for journey in ctx.journeys:
        text = journey.readiness.lower()
        if "green" in text or "ready" in text:
            ready += 1
        if "risk" in text or "blocked" in text or "red" in text:
            risky += 1
    return ready, risky


def source_rel(ctx: ReportContext, path: Path | None) -> str:
    if not path:
        return "not available"
    return path.relative_to(ctx.kb_root).as_posix()


def report_owner(ctx: ReportContext) -> str:
    scope_cfg = ((ctx.cfg.get("roadmap") or {}).get("scopes") or {}).get(ctx.scope, {})
    return scope_cfg.get("owner") or scope_cfg.get("label") or f"{ctx.scope} owner"


def report_audience(ctx: ReportContext, report_type: str) -> str:
    return {
        "status": "leads, product, stakeholders",
        "delivery": "engineering, delivery, product",
        "roadmap-change": "roadmap owner, PM, stakeholders",
    }[report_type]


def fill_status(ctx: ReportContext) -> str:
    items = roadmap_items(ctx)
    open_items = [i for i in items if i.get("state") != "closed" and i.get("issue_type") not in {"Theme", "Initiative", "Milestone"}]
    shipped = [i for i in items if i.get("phase") == "shipped"]
    in_delivery = [i for i in items if i.get("phase") == "in-delivery"]
    decisions_open = [d for d in ctx.decisions if d["status"].lower() != "resolved"]
    ready, risky = summarize_readiness(ctx)
    workstream = ctx.scope
    owner = report_owner(ctx)
    delta = f"{len(in_delivery)} in delivery, {len(shipped)} shipped, {len(decisions_open)} open decisions"
    notes = f"Journey signals: {ready} ready, {risky} risky"
    blockers = [i for i in open_items if i.get("phase") in {"committed", "in-delivery"}][:3]
    blocker_line = "\n".join(
        f"- **{item['id']} {item['title']}** — owner: {item.get('owner') or owner} · next check: {ctx.date}" for item in blockers
    ) or f"- **No active blocker recorded** — owner: {owner} · next check: {ctx.date}"
    decisions_moved = "\n".join(
        f"- {d['title']} ({d['status']})" for d in decisions_open[:3]
    ) or "- No active decision movement recorded"
    decision_asks = "\n".join(
        f"- Review owner for {item['id']} {item['title']}" for item in open_items[:2]
    ) or "- No decision ask queued"
    findings_links = ", ".join(p.relative_to(ctx.kb_root).as_posix() for p in ctx.findings) or "none"
    delivery_link = f"_kb-references/reports/sources/{ctx.scope}/delivery-{ctx.scope}-{ctx.date}.md"
    summary = f"Operating picture for {ctx.scope}: {len(in_delivery)} items are in delivery, {len(shipped)} are shipped, and {len(decisions_open)} decisions still need follow-through."
    template = (TEMPLATE_DIR / "report-status.md").read_text(encoding="utf-8")
    replacements = {
        "{{TITLE}}": f"{ctx.scope.title()} status report {ctx.date}",
        "{{SCOPE}}": ctx.scope,
        "{{DATE}}": ctx.date,
        "{{AUDIENCE}}": report_audience(ctx, "status"),
        "{{OWNER}}": owner,
        "{{CADENCE}}": "weekly",
        "{{EXEC_SUMMARY}}": summary,
        "{{WORKSTREAM_1}}": workstream,
        "{{DELTA_1}}": delta,
        "{{OWNER_1}}": owner,
        "{{NOTES_1}}": notes,
        "{{DECISION_UPDATE}}": decisions_moved.removeprefix("- "),
        "{{DECISION_ASK}}": decision_asks.removeprefix("- "),
        "{{RISK_1}}": blockers[0]["title"] if blockers else "No active blocker recorded",
        "{{RISK_OWNER_1}}": blockers[0].get("owner") or owner if blockers else owner,
        "{{RISK_DATE_1}}": ctx.date,
        "{{ROADMAP_LINK}}": source_rel(ctx, ctx.roadmap_json_path),
        "{{JOURNEY_LINK}}": ", ".join(j.path.relative_to(ctx.kb_root).as_posix() for j in ctx.journeys[:3]) or "not available",
        "{{DELIVERY_REPORT_LINK}}": delivery_link,
        "{{REFERENCE_LINKS}}": findings_links,
    }
    for old, new in replacements.items():
        template = template.replace(old, new)
    if blockers:
        template = template.replace("- **{{RISK_1}}** — owner: {{RISK_OWNER_1}} · next check: {{RISK_DATE_1}}", blocker_line)
    template = template.replace("- {{DECISION_UPDATE}}", decisions_moved)
    template = template.replace("- {{DECISION_ASK}}", decision_asks)
    return template


def fill_delivery(ctx: ReportContext) -> str:
    items = [i for i in roadmap_items(ctx) if i.get("issue_type") not in {"Theme", "Initiative", "Milestone"}]
    commitments = [i for i in items if i.get("phase") in {"committed", "in-delivery", "shipped"}][:5]
    ready, risky = summarize_readiness(ctx)
    summary = f"Delivery reality for {ctx.scope}: {sum(1 for i in commitments if i.get('phase') == 'shipped')} shipped, {sum(1 for i in commitments if i.get('phase') == 'in-delivery')} in delivery, {risky} journey signals need attention."
    rows = []
    for item in commitments:
        journey = next((j for j in ctx.journeys if any(step.startswith("J") for step in j.step_ids)), None)
        rows.append(
            f"| {item['id']} {item['title']} | {item.get('phase','idea')} | {journey.step_ids[0] if journey and journey.step_ids else 'n/a'} | {item.get('status','unknown')} | {'shipped' if item.get('phase') == 'shipped' else 'on-track'} | {journey.readiness if journey else 'No linked journey signal'} |"
        )
    shipped = [f"- {i['id']} {i['title']}" for i in commitments if i.get("phase") == "shipped"] or ["- Nothing newly shipped in the latest roadmap snapshot"]
    at_risk = [f"- {i['id']} {i['title']}" for i in commitments if i.get("phase") in {"committed", "in-delivery"}][:3] or ["- No committed item is currently flagged at risk"]
    gaps = []
    if not ctx.journeys:
        gaps.append("- No journey artifacts were found for this scope")
    if ready == 0:
        gaps.append("- No journey step is currently marked ready")
    if not ctx.decisions:
        gaps.append("- No decision records found to explain trade-offs")
    if not gaps:
        gaps.append("- Scope has roadmap and journey evidence, but linkage is still heuristic rather than explicit")
    template = (TEMPLATE_DIR / "report-delivery.md").read_text(encoding="utf-8")
    replacements = {
        "{{TITLE}}": f"{ctx.scope.title()} delivery report {ctx.date}",
        "{{SCOPE}}": ctx.scope,
        "{{DATE}}": ctx.date,
        "{{AUDIENCE}}": report_audience(ctx, "delivery"),
        "{{OWNER}}": report_owner(ctx),
        "{{CADENCE}}": "weekly",
        "{{DELIVERY_SUMMARY}}": summary,
        "{{ITEM_1}}": commitments[0]["id"] + " " + commitments[0]["title"] if commitments else "No commitment found",
        "{{JOURNEY_STEP_1}}": ctx.journeys[0].step_ids[0] if ctx.journeys and ctx.journeys[0].step_ids else "n/a",
        "{{DELIVERY_SIGNAL_1}}": commitments[0].get("status", "unknown") if commitments else "unknown",
        "{{NOTES_1}}": ctx.journeys[0].readiness if ctx.journeys else "No journey signal",
        "{{TRACEABILITY_GAP_1}}": gaps[0].removeprefix("- "),
        "{{ROADMAP_ACTION}}": source_rel(ctx, ctx.roadmap_json_path),
        "{{JOURNEY_ACTION}}": ", ".join(j.path.relative_to(ctx.kb_root).as_posix() for j in ctx.journeys[:2]) or "add journey artifacts",
        "{{DECISION_ACTION}}": ctx.decisions[0]["path"].relative_to(ctx.kb_root).as_posix() if ctx.decisions else "create a decision if the risk needs human resolution",
        "{{STATUS_REPORT_LINK}}": f"_kb-references/reports/sources/{ctx.scope}/status-{ctx.scope}-{ctx.date}.md",
        "{{ROADMAP_CHANGE_LINK}}": f"_kb-references/reports/sources/{ctx.scope}/roadmap-change-{ctx.scope}-{ctx.date}.md",
        "{{ROADMAP_LINK}}": source_rel(ctx, ctx.roadmap_json_path),
        "{{JOURNEY_LINK}}": ", ".join(j.path.relative_to(ctx.kb_root).as_posix() for j in ctx.journeys[:3]) or "not available",
    }
    for old, new in replacements.items():
        template = template.replace(old, new)
    template = re.sub(r"\| \{\{ITEM_1\}\}.+", "\n".join(rows) if rows else "| none | idea | n/a | unknown | unknown | No data |", template, count=1)
    template = template.replace("- {{SHIPPED_1}}", "\n".join(shipped))
    template = template.replace("- {{AT_RISK_1}}", "\n".join(at_risk))
    template = template.replace("- {{TRACEABILITY_GAP_1}}", "\n".join(gaps))
    return template


def diff_roadmaps(previous: dict | None, current: dict | None) -> list[dict]:
    prev_items = by_id((previous or {}).get("items", []))
    curr_items = by_id((current or {}).get("items", []))
    changes: list[dict] = []
    for item_id, item in curr_items.items():
        before = prev_items.get(item_id)
        if before is None:
            changes.append({"class": "scope-add", "item": item_id, "before": "not present", "after": item.get("phase", "idea"), "reason": "new item entered roadmap scope"})
            continue
        for field, label in (("phase", "phase-change"), ("target", "milestone-change"), ("owner", "ownership-change"), ("lane", "sequence-change")):
            if (before.get(field) or "") != (item.get(field) or ""):
                changes.append({"class": label, "item": item_id, "before": before.get(field) or "unset", "after": item.get(field) or "unset", "reason": f"{field} changed between roadmap snapshots"})
                break
    for item_id, item in prev_items.items():
        if item_id not in curr_items:
            changes.append({"class": "scope-remove", "item": item_id, "before": item.get("phase", "idea"), "after": "not present", "reason": "item left roadmap scope"})
    return changes[:8]


def fill_roadmap_change(ctx: ReportContext) -> str:
    changes = diff_roadmaps(ctx.previous_roadmap_json, ctx.roadmap_json)
    summary = f"Baseline change report for {ctx.scope}: {len(changes)} material roadmap change(s) were detected between {source_rel(ctx, ctx.previous_roadmap_json_path)} and {source_rel(ctx, ctx.roadmap_json_path)}."
    rows = [f"| {c['class']} | {c['item']} | {c['before']} | {c['after']} | {c['reason']} |" for c in changes] or ["| none | scope | no previous snapshot | current baseline only | establish initial baseline |"]
    journey_impact = "\n".join(f"- Review {j.path.relative_to(ctx.kb_root).as_posix()} against the new baseline" for j in ctx.journeys[:2]) or "- No journey artifact found for this scope"
    delivery_impact = f"- Refresh delivery report against {source_rel(ctx, ctx.roadmap_json_path)}"
    stakeholder_impact = f"- Confirm baseline change with {report_owner(ctx)} before downstream status sharing"
    template = (TEMPLATE_DIR / "report-roadmap-change.md").read_text(encoding="utf-8")
    replacements = {
        "{{TITLE}}": f"{ctx.scope.title()} roadmap change report {ctx.date}",
        "{{SCOPE}}": ctx.scope,
        "{{DATE}}": ctx.date,
        "{{AUDIENCE}}": report_audience(ctx, "roadmap-change"),
        "{{OWNER}}": report_owner(ctx),
        "{{APPROVER}}": report_owner(ctx),
        "{{CHANGE_SUMMARY}}": summary,
        "{{ITEM_1}}": changes[0]["item"] if changes else "scope",
        "{{BEFORE_1}}": changes[0]["before"] if changes else "not present",
        "{{AFTER_1}}": changes[0]["after"] if changes else "current baseline only",
        "{{REASON_1}}": changes[0]["reason"] if changes else "establish initial baseline",
        "{{JOURNEY_IMPACT_1}}": journey_impact.removeprefix("- "),
        "{{DELIVERY_IMPACT_1}}": delivery_impact.removeprefix("- "),
        "{{STAKEHOLDER_IMPACT_1}}": stakeholder_impact.removeprefix("- "),
        "{{DECISION_LINK}}": ctx.decisions[0]["path"].relative_to(ctx.kb_root).as_posix() if ctx.decisions else "open a decision if approval is contested",
        "{{STATUS_UPDATE_ACTION}}": f"Refresh status-{ctx.scope}-{ctx.date}.md after approval",
        "{{DELIVERY_UPDATE_ACTION}}": f"Refresh delivery-{ctx.scope}-{ctx.date}.md after approval",
        "{{ROADMAP_LINK}}": f"{source_rel(ctx, ctx.previous_roadmap_json_path)} → {source_rel(ctx, ctx.roadmap_json_path)}",
        "{{JOURNEY_LINK}}": ", ".join(j.path.relative_to(ctx.kb_root).as_posix() for j in ctx.journeys[:3]) or "not available",
        "{{EVIDENCE_LINKS}}": ", ".join(p.relative_to(ctx.kb_root).as_posix() for p in ctx.findings) or "none",
    }
    for old, new in replacements.items():
        template = template.replace(old, new)
    template = re.sub(r"\| re-scope \| .+", "\n".join(rows), template, count=1)
    template = template.replace("- {{JOURNEY_IMPACT_1}}", journey_impact)
    template = template.replace("- {{DELIVERY_IMPACT_1}}", delivery_impact)
    template = template.replace("- {{STAKEHOLDER_IMPACT_1}}", stakeholder_impact)
    return template


def parse_metadata_and_sections(markdown_text: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
    metadata: dict[str, str] = {}
    sections: list[tuple[str, str]] = []
    current_heading: str | None = None
    current_lines: list[str] = []
    for line in markdown_text.splitlines():
        meta = re.match(r"^\*\*(.+?)\*\*:\s*(.*)$", line)
        if meta and current_heading is None:
            metadata[meta.group(1).strip()] = meta.group(2).strip()
            continue
        if line.startswith("## "):
            if current_heading is not None:
                sections.append((current_heading, "\n".join(current_lines).strip()))
            current_heading = line[3:].strip()
            current_lines = []
            continue
        if current_heading is not None:
            current_lines.append(line)
    if current_heading is not None:
        sections.append((current_heading, "\n".join(current_lines).strip()))
    return metadata, sections


def markdown_to_html(text: str) -> str:
    lines = text.splitlines()
    out: list[str] = []
    in_list = False
    in_table = False
    table_rows: list[list[str]] = []

    def flush_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def flush_table() -> None:
        nonlocal in_table, table_rows
        if not in_table:
            return
        header = table_rows[0]
        body = table_rows[2:] if len(table_rows) > 1 and all(set(cell.replace('-', '').strip()) == set() for cell in table_rows[1]) else table_rows[1:]
        out.append("<table><thead><tr>" + "".join(f"<th>{html.escape(cell.strip())}</th>" for cell in header) + "</tr></thead><tbody>")
        for row in body:
            out.append("<tr>" + "".join(f"<td>{html.escape(cell.strip())}</td>" for cell in row) + "</tr>")
        out.append("</tbody></table>")
        in_table = False
        table_rows = []

    for raw in lines:
        line = raw.rstrip()
        if line.startswith("|") and line.endswith("|"):
            flush_list()
            in_table = True
            table_rows.append([cell for cell in line.strip("|").split("|")])
            continue
        flush_table()
        if not line.strip():
            flush_list()
            continue
        if line.startswith("### "):
            flush_list()
            out.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("## "):
            flush_list()
            out.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "):
            flush_list()
            out.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{html.escape(line[2:])}</li>")
        else:
            flush_list()
            out.append(f"<p>{html.escape(line)}</p>")
    flush_table()
    flush_list()
    return "\n".join(out)


def render_html_report(markdown_text: str, ctx: ReportContext) -> str:
    metadata, sections = parse_metadata_and_sections(markdown_text)
    body_html = "\n".join(f"<section><h2>{html.escape(title)}</h2>{markdown_to_html(content)}</section>" for title, content in sections)
    return f"""<!DOCTYPE html>
<html lang=\"en\" data-theme=\"light\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>{html.escape(metadata.get('Scope', ctx.scope))} {html.escape(ctx.report_type)} report</title>
<style>
:root {{ --bg:#ffffff; --surface:#f7f9fc; --border:#d8dee8; --text:#16202a; --muted:#526173; --accent:#2b6cf0; }}
[data-theme=\"dark\"] {{ --bg:#0f1720; --surface:#16222d; --border:#2c3947; --text:#edf2f7; --muted:#a8b5c2; --accent:#8ab4ff; }}
body {{ margin:0; font:16px/1.5 Inter,Arial,sans-serif; background:var(--bg); color:var(--text); }}
header, main {{ max-width:960px; margin:0 auto; padding:24px; }}
header {{ border-bottom:1px solid var(--border); }}
.badge {{ display:inline-block; padding:4px 10px; background:var(--surface); border:1px solid var(--border); border-radius:999px; color:var(--muted); font-size:12px; text-transform:uppercase; }}
.meta {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-top:16px; }}
.card {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:12px; }}
section {{ margin:24px 0; padding:20px; background:var(--surface); border:1px solid var(--border); border-radius:12px; }}
table {{ width:100%; border-collapse:collapse; margin-top:12px; }}
th,td {{ border:1px solid var(--border); padding:8px; text-align:left; vertical-align:top; }}
h1,h2,h3 {{ margin:0 0 12px; }}
p,li {{ color:var(--muted); }}
button {{ position:fixed; top:12px; right:12px; }}
</style>
</head>
<body>
<button onclick=\"document.documentElement.dataset.theme=document.documentElement.dataset.theme==='dark'?'light':'dark'\">toggle theme</button>
<header>
<div class=\"badge\">{html.escape(ctx.report_type)}</div>
<h1>{html.escape(metadata.get('Scope', ctx.scope))} report</h1>
<div class=\"meta\">""" + "".join(f"<div class='card'><strong>{html.escape(k)}</strong><br>{html.escape(v)}</div>" for k, v in metadata.items()) + f"""</div>
</header>
<main>{body_html}</main>
</body>
</html>"""


def generate(ctx: ReportContext) -> tuple[Path, Path]:
    ctx.sources_dir.mkdir(parents=True, exist_ok=True)
    ctx.html_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{ctx.report_type}-{ctx.scope}-{ctx.date}"
    if ctx.report_type == "status":
        markdown_text = fill_status(ctx)
    elif ctx.report_type == "delivery":
        markdown_text = fill_delivery(ctx)
    else:
        markdown_text = fill_roadmap_change(ctx)
    source_path = ctx.sources_dir / f"{stem}.md"
    source_path.write_text(markdown_text + "\n", encoding="utf-8")
    html_path = ctx.html_dir / f"{stem}.html"
    html_path.write_text(render_html_report(markdown_text, ctx), encoding="utf-8")
    return source_path, html_path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("kb_root", type=Path)
    ap.add_argument("report_type", choices=["status", "delivery", "roadmap-change"])
    ap.add_argument("scope")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    args = ap.parse_args()

    ctx = build_context(args.kb_root.resolve(), args.scope, args.report_type, args.date)
    source_path, html_path = generate(ctx)
    print(f"generated {source_path.relative_to(ctx.kb_root)}")
    print(f"generated {html_path.relative_to(ctx.kb_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
