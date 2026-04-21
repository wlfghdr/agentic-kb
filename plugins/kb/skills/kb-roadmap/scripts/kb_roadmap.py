#!/usr/bin/env python3
"""kb-roadmap pilot: minimal working renderer.

Reads `.kb-config/layers.yaml` roadmap: block, enumerates items from configured
trackers, performs tier-1 correlation (ticket-key match), and emits the
triple artifact (MD + HTML + JSON) into <output-dir>/<scope>/roadmap-<DATE>.{md,html,json}.

This is a pilot skeleton. It implements:
- config loading + validation (scope + tracker discovery)
- `ticket-export-markdown` adapter (reads a tree of md files, extracts key + status)
- `github-issues` adapter (optional; uses `gh` CLI if on PATH, else skipped with a warning)
- tier-1 correlation (direct key match only)
- triple-artifact emission with neutral templates

Advanced features (tiers 2-4, deep-investigation, mismatch findings, tune, /discuss)
are declared by the skill but left for the full implementation.

Usage:
  python3 kb_roadmap.py <kb-root> [--scope SCOPE] [--date YYYY-MM-DD] [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    print("kb-roadmap requires PyYAML. Install: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


@dataclass
class Item:
    id: str
    title: str
    status: str
    phase: str
    tracker: str
    url: str = ""
    labels: list[str] = field(default_factory=list)
    issue_type: str = ""         # KeyTheme / Milestone / ValuePack / ValueIncrement / Story / Issue / ...
    parent: str = ""             # id of structural parent (VI → VP, VP → KT, GH issue → VI)
    parent_title: str = ""
    milestone: str = ""          # id of associated delivery milestone (may differ from parent)
    milestone_title: str = ""
    lane: str = ""               # id of top-level swimlane ancestor (VP / Milestone / KT)
    lane_title: str = ""
    target: str = ""             # human-readable target window ("2026 CQ2", "Jun 2026", ...)
    target_quarter: str = ""     # normalized "YYYY-Qn" when derivable
    target_source: str = ""      # how target was derived: self | gh-milestone | parent-bfs | inherited
    gh_milestone: str = ""       # GitHub milestone title (when tracker = github-issues)
    gh_milestone_due: str = ""   # GitHub milestone due-on date (ISO, when set)
    state: str = "open"          # open | closed (normalized from tracker state / phase)
    closed_at: str = ""          # ISO timestamp when closed (best-effort)
    created_at: str = ""         # ISO timestamp when created (best-effort)
    owner: str = ""
    raw: dict = field(default_factory=dict)


def _resolve_config_path(kb_root: Path) -> Path:
    candidates = [
        kb_root / ".kb-config" / "layers.yaml",
        kb_root / ".kb-config.yaml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    print(
        "kb-roadmap: missing .kb-config/layers.yaml "
        "(legacy fallback: .kb-config.yaml)",
        file=sys.stderr,
    )
    sys.exit(1)


def _resolve_artifacts_path(kb_root: Path) -> Path | None:
    candidates = [
        kb_root / ".kb-config" / "artifacts.yaml",
        kb_root / ".kb-artifacts.yaml",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def load_config(kb_root: Path) -> dict:
    cfg = _resolve_config_path(kb_root)
    return yaml.safe_load(cfg.read_text(encoding="utf-8"))


def map_phase(status: str, phases: dict) -> str:
    for phase, statuses in phases.items():
        for s in statuses:
            if status.strip().lower() == s.strip().lower():
                return phase
    return "idea"


# ---- adapters ----

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_QUARTER_RE = re.compile(r"(20\d{2})\s*(?:CQ|Q|FQ)?\s*([1-4])", re.IGNORECASE)
_MONTH_RE = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(20\d{2})\b")
_MONTH_TO_Q = {"Jan": 1, "Feb": 1, "Mar": 1, "Apr": 2, "May": 2, "Jun": 2,
               "Jul": 3, "Aug": 3, "Sep": 3, "Oct": 4, "Nov": 4, "Dec": 4}


def _derive_target(front: dict, body_head: str) -> tuple[str, str]:
    """Return (human-readable target, normalized 'YYYY-Qn'). Best-effort."""
    cf = front.get("customFields") or {}
    sprint_raw = cf.get("Sprint") or cf.get("sprint") or ""
    fix_versions = cf.get("Fix Version/s") or front.get("fixVersions") or ""
    due = cf.get("Due Date") or front.get("duedate") or ""
    candidates = []
    for v in (sprint_raw, fix_versions, due):
        if isinstance(v, list):
            candidates.extend(str(x) for x in v)
        elif v:
            candidates.append(str(v))
    candidates.append(body_head[:500])
    for cand in candidates:
        qm = _QUARTER_RE.search(cand)
        if qm:
            human = cand if len(cand) < 40 else f"{qm.group(1)} Q{qm.group(2)}"
            return human, f"{qm.group(1)}-Q{qm.group(2)}"
        mm = _MONTH_RE.search(cand)
        if mm:
            month_key = mm.group(1)[:3].title()
            q = _MONTH_TO_Q.get(month_key, 0)
            if q:
                return f"{month_key} {mm.group(2)}", f"{mm.group(2)}-Q{q}"
    return "", ""


_PARENT_SECTION_RE = re.compile(
    r"^##\s+Parent\s*\n+\s*[-*]\s+\*\*([A-Z]{2,}-\d+)\*\*",
    re.MULTILINE,
)
_MILESTONE_LABEL_RE = re.compile(r"^milestone[_:-]([A-Z]{2,}-\d+)$", re.IGNORECASE)


def _derive_parent(front: dict, body: str) -> tuple[str, str]:
    """Return (structural-parent-id, milestone-id). Structural parent comes from
    the '## Parent' section of the body when present; otherwise falls back to
    the first label of the form `<role>_<KEY>`. Milestone id comes from a
    `milestone_<KEY>` label independently of the structural parent.
    """
    structural = ""
    if body:
        pm = _PARENT_SECTION_RE.search(body)
        if pm:
            structural = pm.group(1)
    milestone = ""
    label_parent = ""
    for lbl in front.get("labels") or []:
        s = str(lbl)
        mm = _MILESTONE_LABEL_RE.match(s)
        if mm:
            milestone = milestone or mm.group(1)
            continue
        if not label_parent:
            lm = re.match(r"(?:keytheme|parent|epic|valuepack|vp)[_:-]([A-Z]{2,}-\d+)", s, re.IGNORECASE)
            if lm:
                label_parent = lm.group(1)
    if not structural:
        structural = label_parent or milestone
    return structural, milestone


def _parse_md_ticket(md_path: Path, tracker_name: str) -> Item | None:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    front: dict = {}
    body = text
    fm = _FRONTMATTER_RE.match(text)
    if fm:
        try:
            front = yaml.safe_load(fm.group(1)) or {}
        except Exception:
            front = {}
        body = text[fm.end():]
    key = str(front.get("key", "")).strip()
    if not key:
        km = re.search(r"\b([A-Z]{2,}-\d+)\b", text[:500])
        if not km:
            return None
        key = km.group(1)
    title = str(front.get("summary") or "").strip()
    if not title:
        tm = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
        title = tm.group(1).strip() if tm else key
        # strip a leading "KEY: " prefix
        title = re.sub(rf"^{re.escape(key)}:\s*", "", title)
    status = str(front.get("status") or "").strip()
    if not status:
        sm = re.search(r"^\s*[-*]\s+\*\*Status\*\*:\s*(.+?)\s*$", body, re.MULTILINE)
        status = sm.group(1).strip() if sm else ""
    labels = front.get("labels") or []
    if isinstance(labels, str):
        labels = [s.strip() for s in labels.split(",")]
    labels = [str(x).strip() for x in labels if x]
    issue_type = str(front.get("issueType") or front.get("type") or "").strip()
    owner = str(front.get("assignee") or "").strip()
    parent_id, milestone_id = _derive_parent(front, body)
    target_human, target_q = _derive_target(front, body[:800])
    # Best-effort state + timestamps
    created_at = str(front.get("created") or front.get("createdAt") or "")
    resolved_at = str(front.get("resolutiondate") or front.get("resolved") or front.get("closedAt") or "")
    status_lc = status.lower()
    closed_status_terms = ("done", "closed", "resolved", "shipped", "released", "archived", "cancelled", "canceled", "wont do", "won't do")
    state = "closed" if any(t in status_lc for t in closed_status_terms) else "open"
    return Item(
        id=key, title=title, status=status, phase="",
        tracker=tracker_name, labels=labels,
        issue_type=issue_type, parent=parent_id, milestone=milestone_id,
        target=target_human, target_quarter=target_q,
        target_source="self" if target_q else "",
        state=state, closed_at=resolved_at, created_at=created_at,
        owner=owner,
        raw={"path": str(md_path), "body": text},
    )


def adapter_ticket_export_markdown(tracker_cfg: dict, kb_root: Path) -> list[Item]:
    cfg = tracker_cfg.get("config", {}) if "config" in tracker_cfg else tracker_cfg
    raw_path = cfg.get("path") or tracker_cfg.get("path")
    if not raw_path:
        return []
    path = (kb_root / raw_path).resolve()
    if not path.exists():
        print(f"kb-roadmap: ticket-export-markdown path missing: {path}", file=sys.stderr)
        return []
    tracker_name = tracker_cfg.get("name", "ticket-export-markdown")
    items: list[Item] = []
    primary_keys: set[str] = set()
    referenced_keys: set[str] = set()
    for md in path.rglob("*.md"):
        it = _parse_md_ticket(md, tracker_name)
        if not it:
            continue
        items.append(it)
        primary_keys.add(it.id)
        # Collect referenced keys from the body (skip the item's own key).
        for m in re.finditer(r"\b([A-Z]{2,}-\d+)\b", it.raw.get("body", "")):
            if m.group(1) != it.id:
                referenced_keys.add(m.group(1))

    # 1-edge dependency expansion: pull in items from broader search-roots whose
    # keys are referenced by primary items but don't live under the narrowed path.
    dep_cfg = cfg.get("dependency-expand", {}) or tracker_cfg.get("dependency-expand", {}) or {}
    if dep_cfg.get("enabled") and dep_cfg.get("depth", 1) >= 1:
        search_roots = dep_cfg.get("search-roots", [])
        missing = referenced_keys - primary_keys
        if missing and search_roots:
            found = 0
            for root in search_roots:
                root_path = (kb_root / root).resolve()
                if not root_path.exists():
                    continue
                for md in root_path.rglob("*.md"):
                    # Quick filename check to avoid parsing every file.
                    stem_key_m = re.search(r"([A-Z]{2,}-\d+)", md.stem)
                    if stem_key_m and stem_key_m.group(1) in missing:
                        it = _parse_md_ticket(md, f"{tracker_name} (dep)")
                        if it and it.id in missing:
                            it.raw["dependency-edge"] = 1
                            items.append(it)
                            missing.discard(it.id)
                            found += 1
                    if not missing:
                        break
                if not missing:
                    break
            if found:
                print(f"kb-roadmap: dependency-expand pulled in {found} 1-edge "
                      f"ticket(s) from {path.name} references", file=sys.stderr)

    # Bodies are kept in raw for the cross-tracker linking pass in
    # collect_items; they are stripped just before JSON serialization.
    return items


def _iso_to_quarter(iso: str) -> str:
    """Return 'YYYY-Qn' for an ISO date/time string, or ''."""
    if not iso:
        return ""
    m = re.match(r"(\d{4})-(\d{2})", iso)
    if not m:
        return ""
    y, mo = m.group(1), int(m.group(2))
    q = (mo - 1) // 3 + 1
    return f"{y}-Q{q}"


def adapter_github_issues(tracker_cfg: dict, kb_root: Path) -> list[Item]:
    import shutil, subprocess
    if not shutil.which("gh"):
        print("kb-roadmap: gh CLI not on PATH; github-issues adapter skipped",
              file=sys.stderr)
        return []
    cfg = tracker_cfg.get("config", {}) or {}
    repo = cfg.get("repo") or tracker_cfg.get("repo")
    if not repo:
        return []
    # Pull both open and closed issues so closed / finished items can be
    # included in the roadmap (the HTML filter can hide them by default).
    state_arg = cfg.get("state", "all")
    limit = str(cfg.get("limit", 500))
    json_fields = "number,title,state,labels,url,milestone,body,closedAt,createdAt,updatedAt,assignees"
    try:
        out = subprocess.check_output(
            ["gh", "issue", "list", "-R", repo, "--state", state_arg,
             "--limit", limit, "--json", json_fields],
            text=True, timeout=60,
        )
    except subprocess.CalledProcessError as e:
        print(f"kb-roadmap: gh issue list failed: {e}", file=sys.stderr)
        return []
    data = json.loads(out)
    items: list[Item] = []
    for issue in data:
        state_raw = str(issue.get("state", "OPEN")).lower()
        state = "closed" if state_raw in ("closed", "done") else "open"
        ms = issue.get("milestone") or {}
        ms_title = ms.get("title", "") if isinstance(ms, dict) else ""
        ms_due = ms.get("dueOn", "") if isinstance(ms, dict) else ""
        # Try to derive target_quarter from the GH milestone (title first,
        # then dueOn date).
        target = ""
        target_quarter = ""
        target_source = ""
        if ms_title:
            qm = _QUARTER_RE.search(ms_title)
            if qm:
                target = ms_title
                target_quarter = f"{qm.group(1)}-Q{qm.group(2)}"
                target_source = "gh-milestone-title"
            else:
                mm = _MONTH_RE.search(ms_title)
                if mm:
                    month_key = mm.group(1)[:3].title()
                    q = _MONTH_TO_Q.get(month_key, 0)
                    if q:
                        target = f"{month_key} {mm.group(2)}"
                        target_quarter = f"{mm.group(2)}-Q{q}"
                        target_source = "gh-milestone-title"
        if not target_quarter and ms_due:
            target_quarter = _iso_to_quarter(ms_due)
            if target_quarter:
                target = ms_title or ms_due[:10]
                target_source = "gh-milestone-due"
        items.append(Item(
            id=f"#{issue['number']}",
            title=issue["title"],
            status=issue["state"],
            phase="",
            tracker=tracker_cfg.get("name", "github-issues"),
            url=issue.get("url", ""),
            labels=[l["name"] for l in issue.get("labels", [])],
            state=state,
            closed_at=issue.get("closedAt", "") or "",
            created_at=issue.get("createdAt", "") or "",
            gh_milestone=ms_title,
            gh_milestone_due=ms_due,
            target=target,
            target_quarter=target_quarter,
            target_source=target_source,
            raw={"number": issue["number"], "body": issue.get("body", "") or ""},
        ))
    return items


ADAPTERS = {
    "ticket-export-markdown": adapter_ticket_export_markdown,
    "github-issues": adapter_github_issues,
}


def collect_items(scope_cfg: dict, roadmap_cfg: dict, kb_root: Path) -> list[Item]:
    trackers_by_name = {t["name"]: t for t in roadmap_cfg.get("issue-trackers", [])}
    items: list[Item] = []
    for tref in scope_cfg.get("trackers", []):
        tname = tref["tracker"] if isinstance(tref, dict) else tref
        tcfg = trackers_by_name.get(tname, {"name": tname})
        adapter_name = tcfg.get("adapter")
        adapter = ADAPTERS.get(adapter_name)
        if not adapter:
            print(f"kb-roadmap: unknown adapter {adapter_name!r} for tracker {tname}",
                  file=sys.stderr)
            continue
        items.extend(adapter(tcfg, kb_root))
    phases = roadmap_cfg.get("phases", {})
    for it in items:
        it.phase = map_phase(it.status, phases)
    # Resolve parent titles (and propagate target from parent if child has none).
    by_id = {it.id: it for it in items}
    # --- Cross-tracker parent linking ------------------------------------
    # Some trackers (GitHub issues) reference parent Jira items from the Jira
    # side only (e.g. the Jira VI's body mentions `Workstream A (#27) — DONE`).
    # Build a reverse map from GitHub issue numbers to the Jira item that
    # references them, and assign the structural parent on the GitHub side.
    gh_by_num: dict[str, Item] = {}
    for it in items:
        if re.fullmatch(r"#\d+", it.id):
            gh_by_num[it.id] = it
    gh_ref_re = re.compile(r"\(#(\d+)\)")
    if gh_by_num:
        for it in items:
            # Only consider tickets that could plausibly parent GitHub issues:
            # skip the tickets themselves (github tracker), and ignore comment
            # sections to avoid noise. We scan the body up to the "## Comments"
            # heading when present.
            if not re.fullmatch(r"[A-Z]{2,}-\d+", it.id):
                continue
            body = it.raw.get("body", "") or ""
            # Truncate at comments section if present.
            cidx = body.find("\n## Comments")
            scan = body[:cidx] if cidx >= 0 else body
            for m in gh_ref_re.finditer(scan):
                gh_id = f"#{m.group(1)}"
                child = gh_by_num.get(gh_id)
                if not child:
                    continue
                # Only set if not already assigned to another Jira parent.
                if not child.parent or child.parent.startswith("#"):
                    child.parent = it.id

    # --- Label-based parent mapping (adopter-configured fallback) ---------
    # Each tracker in the scope may declare `parent-mappings:` as an ordered
    # list of rules:
    #   - when: {labels-any: [...], labels-all: [...], title-matches: "..."}
    #     parent: <parent-id>
    # The first rule that matches wins. Rules are only applied to items that
    # still have no Jira parent after the body-reference pass.
    trackers_by_name = {t["name"]: t for t in roadmap_cfg.get("issue-trackers", [])}
    for tref in scope_cfg.get("trackers", []):
        tname = tref["tracker"] if isinstance(tref, dict) else tref
        tcfg = trackers_by_name.get(tname, {})
        rules = (tcfg.get("config", {}) or tcfg).get("parent-mappings", []) or []
        if not rules:
            continue
        for it in items:
            if it.tracker != tname:
                continue
            if it.parent and re.fullmatch(r"[A-Z]{2,}-\d+", it.parent):
                continue
            for rule in rules:
                cond = rule.get("when", {}) or {}
                labels_any = [s.lower() for s in cond.get("labels-any", [])]
                labels_all = [s.lower() for s in cond.get("labels-all", [])]
                title_re = cond.get("title-matches")
                item_labels = [s.lower() for s in (it.labels or [])]
                if labels_any and not any(l in item_labels for l in labels_any):
                    continue
                if labels_all and not all(l in item_labels for l in labels_all):
                    continue
                if title_re and not re.search(title_re, it.title or "", re.IGNORECASE):
                    continue
                it.parent = rule.get("parent", "")
                break
    # Resolve parent titles + walk up to compute lane (top-level ancestor
    # Milestone / Value Pack / Key Theme) + propagate target.
    lane_types = {"Milestone", "Value Pack", "ValuePack", "Key Theme", "KeyTheme"}
    for it in items:
        if it.parent and it.parent in by_id:
            it.parent_title = by_id[it.parent].title
        if it.milestone and it.milestone in by_id:
            it.milestone_title = by_id[it.milestone].title
        # Walk parent chain to find a lane-worthy ancestor.
        cur = it
        seen = {cur.id}
        lane_it = None
        while cur.parent and cur.parent in by_id and cur.parent not in seen:
            seen.add(cur.parent)
            cur = by_id[cur.parent]
            if cur.issue_type in lane_types:
                lane_it = cur
                break
        # If the item itself is lane-worthy, it is its own lane.
        if it.issue_type in lane_types and lane_it is None:
            lane_it = it
        if lane_it is not None:
            it.lane = lane_it.id
            it.lane_title = lane_it.title
        # Fall back: use milestone if nothing else resolved.
        if not it.lane and it.milestone and it.milestone in by_id:
            it.lane = it.milestone
            it.lane_title = by_id[it.milestone].title
    # Propagate earliest child target quarter up to lane-worthy items that
    # have no target of their own (VPs typically lack a Sprint field).
    children_by_parent: dict[str, list[Item]] = {}
    for it in items:
        if it.parent:
            children_by_parent.setdefault(it.parent, []).append(it)
    for it in items:
        if it.issue_type in lane_types and not it.target_quarter:
            # Aggregate over direct + transitive children via BFS.
            queue = list(children_by_parent.get(it.id, []))
            seen_c: set[str] = set()
            qs: list[str] = []
            while queue:
                c = queue.pop()
                if c.id in seen_c:
                    continue
                seen_c.add(c.id)
                if c.target_quarter:
                    qs.append(c.target_quarter)
                queue.extend(children_by_parent.get(c.id, []))
            if qs:
                q_min = min(qs)
                q_max = max(qs)
                it.target_quarter = q_min
                it.target_source = it.target_source or "parent-bfs"
                # Human-readable spans "Q2 2026 – Q3 2026" when range.
                if q_min != q_max:
                    it.target = it.target or f"{q_min} – {q_max}"
                else:
                    it.target = it.target or q_min.replace("-", " ")
    # Propagate parent target to children that still lack one.
    for it in items:
        if not it.target_quarter and it.parent and it.parent in by_id:
            p = by_id[it.parent]
            if p.target_quarter:
                it.target_quarter = p.target_quarter
                it.target = it.target or p.target
                it.target_source = it.target_source or "inherited-parent"
    return items


# ---- tier-1 correlation ----

def correlate_tier1(items: list[Item]) -> dict[str, list[Item]]:
    """Group items by id. Items sharing an id across trackers are correlated."""
    groups: dict[str, list[Item]] = {}
    for it in items:
        groups.setdefault(it.id, []).append(it)
    return groups


# ---- rendering ----

MD_TEMPLATE = """# Roadmap — {scope} — {date}

> Generated by kb-roadmap (pilot). Source of truth: tracker items + delivery repos declared in `.kb-config/layers.yaml`.

## A. Plan baseline

Items pulled from configured plan trackers.

| id | title | phase | status | tracker |
|----|-------|-------|--------|---------|
{plan_rows}

## B. Delivery baseline

_Pilot: full delivery baseline (git commits, PRs, tags) not yet implemented. See `references/artifact-contract.md`._

## C. Correlation matrix (tier 1 — direct key match)

| id | appearances | trackers |
|----|-------------|----------|
{corr_rows}

## D. Delta

- **Single-tracker items**: {single_count} — may indicate gaps or items outside this scope.
- **Multi-tracker items**: {multi_count} — correlated across plan and delivery.

## E. Mismatch findings

_Pilot: tier-2-through-4 mismatch classification not yet implemented._

## F. Forward plan

_Author-added section. Use `/kb roadmap refine {scope}` to append._

## G. Decisions

_Author-added section. Link `_kb-decisions/D-*.md` as they arise._

---

Generated {generated_at}.
"""


def render_md(scope: str, date: str, items: list[Item], groups: dict[str, list[Item]]) -> str:
    plan_rows = "\n".join(
        f"| `{it.id}` | {it.title[:80]} | {it.phase} | {it.status} | {it.tracker} |"
        for it in sorted(items, key=lambda x: (x.phase, x.id))
    ) or "| _no items_ |  |  |  |  |"
    corr_rows = "\n".join(
        f"| `{gid}` | {len(grp)} | {', '.join(sorted({i.tracker for i in grp}))} |"
        for gid, grp in sorted(groups.items()) if len(grp) >= 1
    ) or "| _no correlations_ |  |  |"
    multi = sum(1 for g in groups.values() if len(g) > 1)
    single = sum(1 for g in groups.values() if len(g) == 1)
    return MD_TEMPLATE.format(
        scope=scope, date=date,
        plan_rows=plan_rows, corr_rows=corr_rows,
        single_count=single, multi_count=multi,
        generated_at=dt.datetime.now().isoformat(timespec="minutes"),
    )


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="auto">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Roadmap — {scope} — {date}</title>
<style>
:root {{
  --bg:#0e141b; --surface:#16202a; --surface2:#1d2a36; --surface3:#243444;
  --border:#2d3d4d; --text:#eef4f8; --text-dim:#9aaebd; --text-muted:#6b7c8c;
  --accent-1:#66e3a4; --accent-2:#28b8c7; --accent-3:#6f8cff;
  --warn:#ffb84d; --risk:#ff6b6b;
  --phase-idea:#6b7c8c; --phase-defined:#28b8c7; --phase-committed:#6f8cff;
  --phase-in-delivery:#ffb84d; --phase-shipped:#66e3a4; --phase-archived:#4a5968;
}}
[data-theme="light"] {{
  --bg:#f5f7fa; --surface:#fff; --surface2:#f0f3f7; --surface3:#e5eaf1;
  --border:#d7dde5; --text:#111821; --text-dim:#4a5968; --text-muted:#7a8898;
  --accent-1:#2aa870; --accent-2:#108ea0; --accent-3:#3c5bd6;
  --warn:#c47d00; --risk:#c4362c;
  --phase-idea:#7a8898; --phase-defined:#108ea0; --phase-committed:#3c5bd6;
  --phase-in-delivery:#c47d00; --phase-shipped:#2aa870; --phase-archived:#a4adba;
}}
@media (prefers-color-scheme: light) {{ [data-theme="auto"] {{
  --bg:#f5f7fa; --surface:#fff; --surface2:#f0f3f7; --surface3:#e5eaf1;
  --border:#d7dde5; --text:#111821; --text-dim:#4a5968; --text-muted:#7a8898;
  --accent-1:#2aa870; --accent-2:#108ea0; --accent-3:#3c5bd6;
  --warn:#c47d00; --risk:#c4362c;
  --phase-idea:#7a8898; --phase-defined:#108ea0; --phase-committed:#3c5bd6;
  --phase-in-delivery:#c47d00; --phase-shipped:#2aa870; --phase-archived:#a4adba;
}} }}
{tokens_css}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter,-apple-system,system-ui,sans-serif; background:var(--bg); color:var(--text); line-height:1.55; }}
a {{ color:var(--accent-2); text-decoration:none; }} a:hover {{ text-decoration:underline; }}

.toc {{ position:sticky; top:0; z-index:10; background:var(--surface); border-bottom:1px solid var(--border); padding:10px 24px; font-size:0.85rem; }}
.toc a {{ color:var(--text-dim); margin-right:16px; }}
.toc a:hover {{ color:var(--accent-2); }}
.theme-toggle {{ float:right; background:none; border:1px solid var(--border); color:var(--text-dim); border-radius:999px; padding:2px 10px; cursor:pointer; }}

.hero {{ text-align:center; padding:48px 24px 40px; border-bottom:1px solid var(--border); background:linear-gradient(180deg, var(--surface) 0%, var(--bg) 100%); }}
.hero .badge {{ display:inline-block; padding:4px 14px; border-radius:999px; background:var(--surface2); color:var(--text-dim); font-size:0.78rem; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:14px; }}
.hero h1 {{ margin:0 0 8px; font-size:2rem; letter-spacing:-0.02em; }}
.hero .subtitle {{ color:var(--text-dim); font-size:1rem; margin:0 0 6px; }}
.hero .meta {{ color:var(--text-muted); font-size:0.82rem; margin-top:4px; }}
.brand-logo {{ height:32px; margin-bottom:12px; }}
.brand-logo-dark {{ display:none; }}
[data-theme="dark"] .brand-logo-light, [data-theme="auto"] .brand-logo-light {{ display:inline; }}
[data-theme="dark"] .brand-logo-dark {{ display:inline; }}
[data-theme="dark"] [data-theme-pair="light"] .brand-logo-light {{ display:none; }}

main {{ max-width:1180px; margin:0 auto; padding:24px; }}
section {{ margin:40px 0; }}
h2 {{ margin:0 0 8px; font-size:1.4rem; letter-spacing:-0.01em; }}
h2 .sec-num {{ display:inline-block; width:34px; color:var(--text-muted); font-size:0.9rem; font-weight:500; }}
.lead {{ color:var(--text-dim); margin:0 0 20px; max-width:800px; }}

.chip-strip {{ display:flex; gap:10px; flex-wrap:wrap; margin:18px 0; justify-content:center; }}
.chip {{ padding:6px 14px; border-radius:999px; background:var(--surface2); font-size:0.82rem; color:var(--text-dim); border:1px solid var(--border); }}
.chip strong {{ color:var(--text); margin-right:6px; font-size:0.9rem; }}
.chip.chip-accent {{ background:var(--surface3); }}

/* ── Timeline ── */
.timeline {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:20px 24px; margin:16px 0; overflow-x:auto; }}
.timeline-axis {{ display:grid; grid-template-columns:280px 1fr; margin-bottom:6px; }}
.timeline-axis-inner {{ display:grid; grid-template-columns:repeat({num_quarters}, 1fr); font-size:0.72rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.06em; }}
.timeline-axis-inner span {{ text-align:center; padding:4px 0; border-left:1px solid var(--border); }}
.timeline-axis-inner span:first-child {{ border-left:none; }}
.timeline-axis-inner span.today {{ color:var(--accent-2); font-weight:600; }}
.timeline-row {{ display:grid; grid-template-columns:280px 1fr; align-items:center; margin-bottom:4px; }}
.timeline-label {{ padding-right:14px; font-size:0.78rem; color:var(--text); font-weight:500; display:flex; align-items:center; gap:6px; overflow:hidden; }}
.timeline-label .tree-toggle {{ width:10px; display:inline-block; color:var(--text-muted); font-size:0.7rem; transition:transform 0.15s; flex-shrink:0; }}
.timeline-label .tree-toggle-empty {{ color:var(--border); }}
.tree-branch > summary .timeline-label .tree-toggle {{ transform:rotate(0deg); }}
.tree-branch[open] > summary .timeline-label .tree-toggle {{ transform:rotate(90deg); }}
.timeline-label .tree-title {{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1 1 auto; min-width:0; }}
.timeline-label .tree-type {{ font-size:0.62rem; padding:1px 6px; border-radius:3px; background:var(--surface3); color:var(--text-dim); text-transform:uppercase; letter-spacing:0.04em; }}
.timeline-label small {{ display:inline-flex; align-items:center; gap:6px; color:var(--text-muted); font-weight:400; font-size:0.68rem; flex-shrink:0; }}
.tree-branch {{ margin:0; }}
.tree-branch > summary {{ list-style:none; cursor:pointer; }}
.tree-branch > summary::-webkit-details-marker {{ display:none; }}
.tree-branch > summary::marker {{ content:""; }}
.tree-branch > summary:hover .timeline-label .tree-title {{ color:var(--accent-2); }}
.tree-children {{ border-left:1px dashed var(--border); margin-left:8px; padding-left:0; }}
.timeline-track {{ position:relative; height:24px; background:var(--surface2); border:1px solid var(--border); border-radius:5px; overflow:hidden; }}
.timeline-track .today-line {{ position:absolute; top:0; bottom:0; width:2px; background:var(--accent-2); opacity:0.6; z-index:2; }}
.timeline-bar {{ position:absolute; top:2px; bottom:2px; border-radius:3px; display:flex; align-items:center; padding:0 8px; font-size:0.7rem; font-weight:600; color:#fff; white-space:nowrap; overflow:hidden; cursor:default; }}
.tree-row[data-depth="0"] .timeline-track {{ height:28px; }}
.tree-row[data-depth="0"] .timeline-bar {{ top:3px; bottom:3px; font-size:0.74rem; }}
.tree-row[data-depth="0"] .timeline-label {{ font-size:0.84rem; font-weight:600; }}
.tree-row[data-depth="1"] .timeline-label {{ font-size:0.78rem; font-weight:500; }}
.tree-row[data-depth="2"] .timeline-label {{ font-size:0.74rem; font-weight:400; color:var(--text-dim); }}
.tree-row[data-depth="3"] .timeline-label {{ font-size:0.72rem; font-weight:400; color:var(--text-muted); }}
.tree-row[data-depth="3"] .timeline-track,
.tree-row[data-depth="4"] .timeline-track {{ height:18px; }}
.tree-row[data-depth="3"] .timeline-bar,
.tree-row[data-depth="4"] .timeline-bar {{ top:1px; bottom:1px; font-size:0.64rem; padding:0 6px; }}
.timeline-bar.phase-idea {{ background:linear-gradient(90deg, var(--phase-idea), #8695a5); }}
.timeline-bar.phase-defined {{ background:linear-gradient(90deg, var(--phase-defined), #5eead4); }}
.timeline-bar.phase-committed {{ background:linear-gradient(90deg, var(--phase-committed), #a78bfa); }}
.timeline-bar.phase-in-delivery {{ background:linear-gradient(90deg, var(--phase-in-delivery), #fcd34d); color:#1f1300; }}
.timeline-bar.phase-shipped {{ background:linear-gradient(90deg, var(--phase-shipped), #86efac); color:#072415; }}
.timeline-bar.phase-archived {{ background:linear-gradient(90deg, var(--phase-archived), var(--text-muted)); }}
.timeline-bar .count {{ opacity:0.8; margin-left:6px; font-weight:500; }}
.timeline-controls {{ display:flex; gap:8px; margin:8px 0; font-size:0.75rem; }}
.timeline-controls button {{ background:var(--surface2); border:1px solid var(--border); color:var(--text-dim); border-radius:6px; padding:4px 10px; cursor:pointer; font-size:0.74rem; }}
.timeline-controls button:hover {{ color:var(--accent-2); border-color:var(--accent-2); }}

/* ── Kanban ── */
.kanban {{ display:grid; grid-template-columns:repeat({num_phases}, minmax(220px, 1fr)); gap:14px; margin:16px 0; overflow-x:auto; }}
.kanban-col {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; min-height:200px; display:flex; flex-direction:column; }}
.kanban-col-header {{ padding:12px 14px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; }}
.kanban-col-header .name {{ font-size:0.82rem; font-weight:600; letter-spacing:0.02em; text-transform:uppercase; }}
.kanban-col-header .count {{ font-size:0.74rem; color:var(--text-muted); background:var(--surface2); padding:2px 9px; border-radius:999px; }}
.kanban-col[data-phase="idea"] .name {{ color:var(--phase-idea); }}
.kanban-col[data-phase="defined"] .name {{ color:var(--phase-defined); }}
.kanban-col[data-phase="committed"] .name {{ color:var(--phase-committed); }}
.kanban-col[data-phase="in-delivery"] .name {{ color:var(--phase-in-delivery); }}
.kanban-col[data-phase="shipped"] .name {{ color:var(--phase-shipped); }}
.kanban-col[data-phase="archived"] .name {{ color:var(--phase-archived); }}
.kanban-cards {{ padding:10px; display:flex; flex-direction:column; gap:8px; flex:1; }}
.kanban-card {{ background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:10px 12px; font-size:0.82rem; }}
.kanban-card .id {{ font-family:'SF Mono',Menlo,Consolas,monospace; font-size:0.72rem; color:var(--text-muted); }}
.kanban-card .title {{ color:var(--text); margin:2px 0 6px; line-height:1.35; }}
.kanban-card .meta {{ display:flex; gap:6px; flex-wrap:wrap; font-size:0.68rem; color:var(--text-muted); }}
.kanban-card .meta .pill {{ padding:1px 7px; border-radius:999px; background:var(--surface3); }}
.kanban-card .meta .pill-type {{ background:var(--surface3); color:var(--text-dim); }}
.kanban-card .meta .pill-target {{ background:var(--accent-2); color:#fff; opacity:0.85; }}
.kanban-empty {{ color:var(--text-muted); font-size:0.78rem; text-align:center; padding:20px 0; }}

/* ── Tables ── */
.details {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; margin:10px 0; overflow:hidden; }}
.details summary {{ padding:12px 18px; cursor:pointer; font-weight:500; font-size:0.92rem; list-style:none; }}
.details summary::marker {{ display:none; }}
.details summary::before {{ content:"▸"; margin-right:10px; color:var(--text-muted); display:inline-block; transition:transform 0.15s; }}
.details[open] summary::before {{ transform:rotate(90deg); }}
.details .content {{ padding:0 18px 14px; overflow-x:auto; }}
table {{ width:100%; border-collapse:collapse; font-size:0.84rem; }}
th, td {{ padding:8px 10px; text-align:left; border-bottom:1px solid var(--border); vertical-align:top; }}
th {{ background:var(--surface2); color:var(--text-dim); font-weight:600; font-size:0.76rem; text-transform:uppercase; letter-spacing:0.04em; }}
tr:last-child td {{ border-bottom:0; }}
code {{ font-family:'SF Mono',Menlo,Consolas,monospace; background:var(--surface2); padding:1px 6px; border-radius:4px; font-size:0.78rem; }}

.callout {{ background:var(--surface); border:1px solid var(--border); border-left:3px solid var(--accent-2); border-radius:8px; padding:14px 18px; margin:14px 0; font-size:0.9rem; color:var(--text-dim); }}

footer {{ text-align:center; color:var(--text-muted); font-size:0.76rem; padding:28px 20px; border-top:1px solid var(--border); margin-top:60px; }}

/* ── Filter state on timeline rows ── */
.tl-hide-closed .tree-row[data-state="closed"] {{ display:none; }}
.tl-hide-open .tree-row[data-state="open"] {{ display:none; }}
.tl-hide-closed .tree-branch:has(> summary .tree-row[data-state="closed"]) {{ display:none; }}
.tl-hide-open .tree-branch:has(> summary .tree-row[data-state="open"]) {{ display:none; }}
.timeline-filter {{ display:inline-flex; gap:6px; align-items:center; color:var(--text-dim); font-size:0.74rem; user-select:none; margin-left:auto; }}
.timeline-filter input {{ accent-color:var(--accent-2); }}

/* ── Landing-zone quarter cards ── */
.landing-zones {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:14px; margin:12px 0; }}
.lz-card {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:14px 16px; }}
.lz-card.lz-today {{ border-color:var(--accent-2); box-shadow:0 0 0 1px var(--accent-2) inset; }}
.lz-card.lz-empty {{ opacity:0.55; }}
.lz-card h3 {{ margin:0 0 6px; font-size:0.9rem; display:flex; justify-content:space-between; align-items:baseline; }}
.lz-card h4 {{ margin:10px 0 4px; font-size:0.7rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--text-muted); font-weight:600; }}
.lz-card .lz-count {{ font-size:0.7rem; color:var(--text-muted); font-weight:400; }}
.lz-card ul {{ margin:0; padding:0; list-style:none; }}
.lz-card li {{ padding:3px 0; font-size:0.78rem; color:var(--text-dim); border-top:1px dashed var(--border); }}
.lz-card li:first-child {{ border-top:none; }}
.lz-card .pill {{ display:inline-block; font-size:0.66rem; padding:1px 6px; border-radius:4px; background:var(--surface2); color:var(--text-dim); margin-left:4px; }}
.lz-card .pill-done {{ background:color-mix(in srgb, var(--phase-shipped) 25%, var(--surface2)); color:var(--phase-shipped); }}

/* ── Velocity ── */
.velocity-grid {{ display:grid; grid-template-columns:repeat(auto-fill, minmax(150px, 1fr)); gap:10px; margin:12px 0; }}
.vel-card {{ background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:14px; text-align:center; }}
.vel-card .vel-num {{ font-size:1.6rem; font-weight:700; color:var(--text); }}
.vel-card .vel-lbl {{ font-size:0.72rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.05em; margin-top:2px; }}
.vel-card-accent {{ border-color:var(--accent-2); }}
.vel-card-accent .vel-num {{ color:var(--accent-2); }}

/* ── Findings ── */
.finding {{ border:1px solid var(--border); border-radius:10px; background:var(--surface); margin:8px 0; }}
.finding summary {{ padding:10px 14px; font-weight:600; cursor:pointer; display:flex; gap:10px; align-items:center; }}
.finding .finding-list {{ margin:0; padding:8px 14px 14px 34px; font-size:0.82rem; color:var(--text-dim); }}
.finding .finding-list li {{ padding:3px 0; }}
.sev-badge {{ font-size:0.66rem; padding:2px 8px; border-radius:999px; text-transform:uppercase; letter-spacing:0.05em; font-weight:700; }}
.sev-high {{ background:color-mix(in srgb, var(--phase-in-delivery) 30%, var(--surface2)); color:var(--phase-in-delivery); }}
.sev-medium {{ background:color-mix(in srgb, var(--phase-committed) 30%, var(--surface2)); color:var(--phase-committed); }}
.finding-high {{ border-left:3px solid var(--phase-in-delivery); }}
.finding-medium {{ border-left:3px solid var(--phase-committed); }}

@media (max-width: 880px) {{
  .kanban {{ grid-template-columns:repeat(2, minmax(180px, 1fr)); }}
  .timeline-axis, .timeline-row {{ grid-template-columns:180px 1fr; }}
}}
</style>
</head>
<body>

<nav class="toc">
<a href="#overview">Overview</a>
<a href="#timeline">Timeline</a>
<a href="#landing-zones">Landing zones</a>
<a href="#velocity">Velocity</a>
<a href="#findings">Findings</a>
<a href="#kanban">Status board</a>
<a href="#correlation">Correlation</a>
<a href="#plan">Plan table</a>
<a href="#forward">Forward</a>
<a href="#decisions">Decisions</a>
<button class="theme-toggle" data-action="toggle-theme">☾</button>
</nav>

<header class="hero">
{logo_img}
<div class="badge">Generated roadmap · {generator}</div>
<h1>Roadmap — {scope_label}</h1>
<p class="subtitle">{scope_description}</p>
<div class="meta">{date} · scope <code>{scope}</code></div>
<div class="chip-strip">
  <span class="chip chip-accent"><strong>{plan_count}</strong>items</span>
  <span class="chip"><strong>{open_count}</strong>open</span>
  <span class="chip"><strong>{closed_count}</strong>closed</span>
  <span class="chip"><strong>{in_delivery_count}</strong>in delivery</span>
  <span class="chip"><strong>{shipped_count}</strong>shipped</span>
  <span class="chip"><strong>{gh_ms_count}</strong>GH milestones</span>
</div>
</header>

<main>

<section id="overview">
  <h2><span class="sec-num">01</span>Overview</h2>
    <p class="lead">{scope_description} This roadmap was generated from configured trackers in <code>.kb-config/layers.yaml</code>. Timeline bars reflect target quarters parsed from ticket metadata; the status board reflects current phase mapping from native tracker statuses.</p>
</section>

<section id="timeline">
  <h2><span class="sec-num">02</span>Timeline</h2>
  <p class="lead">Hierarchical tree grouped by <code>KeyTheme → ValuePack → ValueIncrement → GitHub workstream → GitHub issue</code>. Each row's bar spans the target-quarter range of the item plus all descendants; color reflects the dominant phase (for containers, aggregated from children). Click any row to expand or collapse its subtree. The vertical line marks today.</p>
  <div class="timeline-controls">
    <button data-action="tree-expand-all">Expand all</button>
    <button data-action="tree-collapse-all">Collapse all</button>
    <button data-action="tree-expand-to-depth" data-depth="1">Lanes only</button>
    <button data-action="tree-expand-to-depth" data-depth="2">Lanes + VIs</button>
    <label class="timeline-filter"><input type="checkbox" data-filter="show-closed" checked> show closed / shipped</label>
    <label class="timeline-filter"><input type="checkbox" data-filter="show-open" checked> show open</label>
  </div>
  <div class="timeline">
    <div class="timeline-axis"><div></div><div class="timeline-axis-inner">{axis_quarters_html}</div></div>
    {timeline_rows_html}
  </div>
  {timeline_legend_html}
</section>

<section id="landing-zones">
  <h2><span class="sec-num">03</span>Landing zones by quarter</h2>
  <p class="lead">Drill-down per quarter. Shows GitHub milestones (native delivery landing zones) plus Jira value-increments scheduled for each quarter, with open/closed counts. Use this to spot an over-loaded quarter or a milestone that should shift.</p>
  {landing_zones_html}
</section>

<section id="velocity">
  <h2><span class="sec-num">04</span>Velocity & forecast</h2>
  <p class="lead">Rough burn-rate based on GitHub <code>closedAt</code> timestamps. The forecast is a guesstimate: <code>open ÷ weekly velocity</code>. Treat it as a directional signal, not a commitment.</p>
  {velocity_html}
</section>

<section id="findings">
  <h2><span class="sec-num">05</span>Findings · critical path · discrepancies</h2>
  <p class="lead">Heuristic checks across the resolved hierarchy. Items flagged here usually need a conversation before the next planning cycle.</p>
  {findings_html}
</section>

<section id="kanban">
  <h2><span class="sec-num">06</span>Status board</h2>
  <p class="lead">Items grouped by phase. <strong>Containers</strong> (Key Theme, Value Pack, Milestone) are excluded — the board shows deliverables only. Phases derive from tracker statuses via the <code>roadmap.phases</code> mapping.</p>
  <div class="kanban">
{kanban_cols_html}
  </div>
</section>

<section id="correlation">
  <h2><span class="sec-num">07</span>Correlation matrix (tier 1)</h2>
  <p class="lead">Items that share an identifier across trackers. Single-tracker items appear in the plan table below.</p>
  <details class="details" open><summary>Correlations · {multi_count} multi-tracker</summary><div class="content">
    <table><thead><tr><th>id</th><th>appearances</th><th>trackers</th></tr></thead>
      <tbody>{corr_rows_html}</tbody>
    </table>
  </div></details>
</section>

<section id="plan">
  <h2><span class="sec-num">08</span>Plan table</h2>
  <p class="lead">All items, sorted by phase then milestone. Click to expand.</p>
  <details class="details"><summary>All items · {plan_count} rows</summary><div class="content">
    <table><thead><tr><th>id</th><th>title</th><th>type</th><th>phase</th><th>status</th><th>target</th><th>lane / milestone</th><th>tracker</th></tr></thead>
      <tbody>{plan_rows_html}</tbody>
    </table>
  </div></details>
</section>

<section id="forward">
  <h2><span class="sec-num">09</span>Forward plan</h2>
  <div class="callout">Use <code>/kb roadmap refine {scope}</code> to append a dated forward-plan block, or <code>/kb roadmap audit</code> to run the 15-rule consistency check.</div>
</section>

<section id="decisions">
  <h2><span class="sec-num">10</span>Decisions</h2>
  <div class="callout">Linked <code>_kb-decisions/D-*.md</code> entries surface here after <code>/kb decide resolve</code>. Pilot: none resolved against this scope yet.</div>
</section>

</main>

<footer>
Generated {generated_at} · kb-roadmap · scope <code>{scope}</code> · agentic-kb
</footer>

<script>
(function(){{var r=document.documentElement;var s=localStorage.getItem('kb-rm-theme');if(s)r.setAttribute('data-theme',s);
document.querySelectorAll('[data-action="toggle-theme"]').forEach(function(b){{b.addEventListener('click',function(){{var c=r.getAttribute('data-theme')||'auto';var n=c==='dark'?'light':c==='light'?'auto':'dark';r.setAttribute('data-theme',n);localStorage.setItem('kb-rm-theme',n);}});}});
// Timeline tree controls
function allBranches(){{return document.querySelectorAll('.tree-branch');}}
document.querySelectorAll('[data-action="tree-expand-all"]').forEach(function(b){{b.addEventListener('click',function(){{allBranches().forEach(function(d){{d.open=true;}});}});}});
document.querySelectorAll('[data-action="tree-collapse-all"]').forEach(function(b){{b.addEventListener('click',function(){{allBranches().forEach(function(d){{d.open=false;}});}});}});
document.querySelectorAll('[data-action="tree-expand-to-depth"]').forEach(function(b){{b.addEventListener('click',function(){{var target=parseInt(b.getAttribute('data-depth'),10);allBranches().forEach(function(d){{var row=d.querySelector(':scope > summary .tree-row');var depth=row?parseInt(row.getAttribute('data-depth'),10):0;d.open=(depth<target);}});}});}});
// Show/hide closed+open rows via class on the timeline container
function applyFilters(){{var tl=document.querySelector('.timeline');if(!tl)return;var showClosed=document.querySelector('[data-filter="show-closed"]');var showOpen=document.querySelector('[data-filter="show-open"]');tl.classList.toggle('tl-hide-closed', showClosed && !showClosed.checked);tl.classList.toggle('tl-hide-open', showOpen && !showOpen.checked);}}
document.querySelectorAll('[data-filter]').forEach(function(cb){{cb.addEventListener('change',applyFilters);}});applyFilters();
}})();
</script>
</body></html>
"""


# ---- HTML helpers ----

PHASE_ORDER = ["idea", "defined", "committed", "in-delivery", "shipped", "archived"]
PHASE_LABELS = {"idea": "Idea", "defined": "Defined", "committed": "Committed",
                "in-delivery": "In delivery", "shipped": "Shipped", "archived": "Archived"}


def _build_quarter_axis(scope_cfg: dict, roadmap_cfg: dict, items: list[Item]) -> list[str]:
    """Return list of quarter labels (e.g. ['2026 Q1', '2026 Q2', ...])."""
    tl_cfg = scope_cfg.get("timeline") or roadmap_cfg.get("timeline") or {}
    start = tl_cfg.get("start")
    end = tl_cfg.get("end")
    quarters: list[tuple[int, int]] = []
    seen = set()
    for it in items:
        if it.target_quarter:
            m = re.match(r"(\d{4})-Q([1-4])", it.target_quarter)
            if m:
                key = (int(m.group(1)), int(m.group(2)))
                seen.add(key)
    if start and end:
        sy, sq = _parse_q(start)
        ey, eq = _parse_q(end)
    elif seen:
        sy, sq = min(seen)
        ey, eq = max(seen)
    else:
        today = dt.date.today()
        sy, sq = today.year, (today.month - 1) // 3 + 1
        ey, eq = sy + 1, sq
    # widen to include today ±1 quarter for context
    today = dt.date.today()
    ty, tq = today.year, (today.month - 1) // 3 + 1
    if (ty, tq) < (sy, sq):
        sy, sq = ty, tq
    if (ty, tq) > (ey, eq):
        ey, eq = ty, tq
    # cap at 8 quarters
    y, q = sy, sq
    while (y, q) <= (ey, eq) and len(quarters) < 8:
        quarters.append((y, q))
        q += 1
        if q > 4:
            q = 1
            y += 1
    return [f"{y} Q{q}" for (y, q) in quarters]


def _parse_q(s: str) -> tuple[int, int]:
    m = re.match(r"(\d{4})[^\d]*Q?([1-4])", s)
    if m:
        return int(m.group(1)), int(m.group(2))
    return dt.date.today().year, (dt.date.today().month - 1) // 3 + 1


def _q_index(q_label: str, axis: list[str]) -> int:
    """Return the 0-based index of q_label in axis, or -1."""
    if q_label in axis:
        return axis.index(q_label)
    # allow '2026-Q2' form too
    m = re.match(r"(\d{4})-Q([1-4])", q_label)
    if m:
        cand = f"{m.group(1)} Q{m.group(2)}"
        if cand in axis:
            return axis.index(cand)
    return -1


def _today_axis_offset(axis: list[str]) -> float:
    """Return fractional index (0..len(axis)) of today on the axis."""
    today = dt.date.today()
    for i, lbl in enumerate(axis):
        m = re.match(r"(\d{4}) Q([1-4])", lbl)
        if not m:
            continue
        y, q = int(m.group(1)), int(m.group(2))
        q_start_month = 3 * (q - 1) + 1
        q_start = dt.date(y, q_start_month, 1)
        q_end_month = q_start_month + 2
        q_end_last = 31 if q_end_month in (3, 5, 7, 8, 10, 12) else (30 if q_end_month != 2 else 28)
        q_end = dt.date(y, q_end_month, q_end_last)
        if q_start <= today <= q_end:
            frac = (today - q_start).days / max(1, (q_end - q_start).days)
            return i + frac
    return -1.0


def _group_swimlanes(items: list[Item]) -> list[tuple[str, str, list[Item]]]:
    """Return (lane_id, lane_label, items) — one lane per top-level ancestor
    (Value Pack / Milestone / Key Theme) when resolvable, else a fallback
    'Unscheduled' lane for orphans.
    """
    lanes: dict[str, list[Item]] = {}
    labels: dict[str, str] = {}
    for it in items:
        if it.lane:
            lane_id = it.lane
            lanes.setdefault(lane_id, []).append(it)
            labels.setdefault(lane_id, it.lane_title or lane_id)
        else:
            lanes.setdefault("__unscheduled__", []).append(it)
            labels["__unscheduled__"] = "Unscheduled"

    # Order: lanes that contain a Value Pack / Milestone / Key Theme header
    # item first, ranked by that item's target quarter; __unscheduled__ last.
    def lane_sort_key(kv):
        lane_id, items_ = kv
        if lane_id == "__unscheduled__":
            return (99, "")
        # Use the lane header item's target if it itself is in the lane;
        # otherwise use the earliest child target.
        by_id_local = {i.id: i for i in items_}
        header = by_id_local.get(lane_id)
        if header and header.target_quarter:
            return (0, header.target_quarter)
        target_qs = [i.target_quarter for i in items_ if i.target_quarter]
        return (0, min(target_qs) if target_qs else "~")
    ordered = sorted(lanes.items(), key=lane_sort_key)
    return [(lid, labels[lid], its) for lid, its in ordered]


def _build_item_tree(items: list[Item]) -> tuple[list[Item], dict[str, list[Item]]]:
    """Return (roots, children_by_parent). Roots are items with no parent in the set.
    Order within each level: earliest target_quarter first, then by id."""
    by_id = {it.id: it for it in items}
    children: dict[str, list[Item]] = {}
    roots: list[Item] = []
    for it in items:
        p = it.parent if it.parent in by_id else ""
        if p:
            children.setdefault(p, []).append(it)
        else:
            roots.append(it)

    def sort_key(it: Item) -> tuple:
        # Lane-worthy items first, then by target quarter, then id.
        type_rank = 0 if it.issue_type in ("Key Theme", "KeyTheme") else \
                    1 if it.issue_type in ("Value Pack", "ValuePack") else \
                    2 if it.issue_type == "Milestone" else \
                    3 if it.issue_type == "ValueIncrement" else 4
        return (type_rank, it.target_quarter or "~", it.id)

    roots.sort(key=sort_key)
    for k in children:
        children[k].sort(key=sort_key)
    return roots, children


def _collect_descendant_quarters(it: Item, children: dict[str, list[Item]]) -> list[str]:
    out: list[str] = []
    stack = [it]
    seen: set[str] = set()
    while stack:
        cur = stack.pop()
        if cur.id in seen:
            continue
        seen.add(cur.id)
        if cur.target_quarter:
            out.append(cur.target_quarter)
        stack.extend(children.get(cur.id, []))
    return out


def _dominant_phase(it: Item, children: dict[str, list[Item]]) -> str:
    """Pick the phase that best represents a subtree. Rule: use the item's own
    phase if it has a non-empty phase AND its issue_type is not a container
    (VP/KT/Milestone); otherwise pick the phase most common among descendants.
    """
    container_types = {"Key Theme", "KeyTheme", "Value Pack", "ValuePack", "Milestone"}
    if it.issue_type not in container_types and it.phase:
        return it.phase
    # Aggregate over descendants.
    counter: dict[str, int] = {}
    stack = list(children.get(it.id, []))
    seen: set[str] = set()
    while stack:
        c = stack.pop()
        if c.id in seen:
            continue
        seen.add(c.id)
        if c.phase:
            counter[c.phase] = counter.get(c.phase, 0) + 1
        stack.extend(children.get(c.id, []))
    if counter:
        # Prefer in-delivery > committed > defined > idea > shipped > archived
        for p in ("in-delivery", "committed", "defined", "idea", "shipped", "archived"):
            if p in counter:
                return p
    return it.phase or "idea"


def _render_tree_row(it: Item, children: dict[str, list[Item]], axis: list[str],
                     today_line: str, depth: int, path: str) -> str:
    """Render one timeline row, recursing into children inside a <details>.
    `path` is a unique breadcrumb used for the details' id.
    """
    child_list = children.get(it.id, [])
    has_children = bool(child_list)

    # Compute bar position across self + descendants.
    qs = _collect_descendant_quarters(it, children)
    if qs:
        idxs = [i for i in (_q_index(q, axis) for q in qs) if i >= 0]
    else:
        idxs = []
    if idxs:
        start_i = min(idxs)
        end_i = max(idxs)
    else:
        # No targets in the subtree. Anchor to today if on-axis.
        today_offset = _today_axis_offset(axis)
        ti = int(today_offset) if today_offset >= 0 else 0
        start_i = end_i = ti
    left = (start_i / max(len(axis), 1)) * 100
    width = ((end_i - start_i + 1) / max(len(axis), 1)) * 100

    phase = _dominant_phase(it, children)
    # Count leaf items in subtree (excluding containers).
    container_types = {"Key Theme", "KeyTheme", "Value Pack", "ValuePack", "Milestone"}
    leaf_count = 0
    stack = [it]
    seen_ids: set[str] = set()
    while stack:
        c = stack.pop()
        if c.id in seen_ids:
            continue
        seen_ids.add(c.id)
        if c.issue_type not in container_types:
            leaf_count += 1
        stack.extend(children.get(c.id, []))

    # Label prefix
    type_pill = ""
    if it.issue_type:
        type_pill = f'<span class="tree-type">{html.escape(it.issue_type)}</span>'
    target_str = it.target or (it.target_quarter.replace("-", " ") if it.target_quarter else "")
    bar_text = target_str or PHASE_LABELS.get(phase, phase)
    bar_tail = ""
    if leaf_count > 1:
        bar_tail = f'<span class="count">· {leaf_count}</span>'

    # Indentation + toggle
    toggle = '<span class="tree-toggle">▸</span>' if has_children else '<span class="tree-toggle tree-toggle-empty">·</span>'
    indent_style = f'padding-left:{depth * 14}px'

    # State classifier for filters: "closed" if self closed OR (container) all
    # descendants closed.
    subtree_states: set[str] = set()
    stack = [it]
    seen_s: set[str] = set()
    while stack:
        c = stack.pop()
        if c.id in seen_s: continue
        seen_s.add(c.id)
        if c.issue_type not in container_types:
            subtree_states.add(c.state or "open")
        stack.extend(children.get(c.id, []))
    if not subtree_states:
        row_state = it.state or "open"
    elif subtree_states == {"closed"}:
        row_state = "closed"
    elif "open" in subtree_states:
        row_state = "open"
    else:
        row_state = "open"

    label_html = (
        f'<div class="timeline-label" style="{indent_style}">'
        f'{toggle}<span class="tree-title" title="{html.escape(it.title)}">{html.escape(it.title[:60])}</span>'
        f'<small>{html.escape(it.id)}{" · " + type_pill if type_pill else ""} · {leaf_count} leaf</small>'
        f'</div>'
    )
    track_html = (
        f'<div class="timeline-track">{today_line}'
        f'<div class="timeline-bar phase-{html.escape(phase)}" '
        f'style="left:{left:.2f}%; width:{width:.2f}%" '
        f'title="{html.escape(it.title)} · {html.escape(PHASE_LABELS.get(phase, phase))} · {leaf_count} item(s)">'
        f'{html.escape(bar_text[:30])}{bar_tail}</div>'
        f'</div>'
    )
    row_html = f'<div class="timeline-row tree-row" data-depth="{depth}" data-state="{row_state}">{label_html}{track_html}</div>'

    if not has_children:
        return row_html

    # Render children inside a details block. First-level (depth 0) open by default,
    # lane-worthy containers (VP/KT/Milestone at depth 1) open by default,
    # deeper levels collapsed.
    open_attr = " open" if depth == 0 or it.issue_type in container_types else ""
    child_rows = "\n".join(
        _render_tree_row(c, children, axis, today_line, depth + 1, f"{path}-{i}")
        for i, c in enumerate(child_list)
    )
    return (
        f'<details class="tree-branch"{open_attr} id="tl-{html.escape(path)}">'
        f'<summary>{row_html}</summary>'
        f'<div class="tree-children">{child_rows}</div>'
        f'</details>'
    )


def _render_timeline(items: list[Item], axis: list[str]) -> tuple[str, str]:
    """Return (rows_html, legend_html). Renders a collapsible hierarchical tree:
    KeyTheme → ValuePack → ValueIncrement → GitHub issues → sub-issues, based
    on resolved parent/child relationships. Each level renders one row with a
    bar spanning the target-quarter range of the item plus its descendants.
    """
    if not items or not axis:
        return "<div class='timeline-row'><div class='timeline-label'>–</div><div class='timeline-track'></div></div>", ""
    today_offset = _today_axis_offset(axis)
    today_line = ""
    if today_offset >= 0:
        today_left = (today_offset / len(axis)) * 100
        today_line = f'<div class="today-line" style="left:{today_left:.2f}%"></div>'

    roots, children = _build_item_tree(items)

    # Roots that are lane-worthy (KT/VP/Milestone) are rendered directly.
    # Everything else is bucketed into an 'Unscheduled' synthetic root so the
    # tree view does not hide orphans.
    lane_types = {"Key Theme", "KeyTheme", "Value Pack", "ValuePack", "Milestone"}
    lane_roots = [r for r in roots if r.issue_type in lane_types]
    orphan_roots = [r for r in roots if r.issue_type not in lane_types]

    parts: list[str] = []
    for i, r in enumerate(lane_roots):
        parts.append(_render_tree_row(r, children, axis, today_line, 0, f"r{i}"))

    if orphan_roots:
        # Synthetic 'Unscheduled' container so orphans are collapsible too.
        # Build a pseudo-row.
        qs = []
        leaf_count = len(orphan_roots)
        for o in orphan_roots:
            qs.extend(_collect_descendant_quarters(o, children))
        idxs = [i for i in (_q_index(q, axis) for q in qs) if i >= 0]
        if idxs:
            start_i, end_i = min(idxs), max(idxs)
        else:
            ti = int(today_offset) if today_offset >= 0 else 0
            start_i = end_i = ti
        left = (start_i / max(len(axis), 1)) * 100
        width = ((end_i - start_i + 1) / max(len(axis), 1)) * 100
        syn_label = (
            '<div class="timeline-label" style="padding-left:0px">'
            '<span class="tree-toggle">▸</span>'
            '<span class="tree-title">Unscheduled</span>'
            f'<small>{leaf_count} orphan(s)</small>'
            '</div>'
        )
        syn_track = (
            f'<div class="timeline-track">{today_line}'
            f'<div class="timeline-bar phase-archived" '
            f'style="left:{left:.2f}%; width:{width:.2f}%" '
            f'title="Unscheduled · {leaf_count} orphan(s)">unscheduled<span class="count">· {leaf_count}</span></div>'
            f'</div>'
        )
        syn_row = f'<div class="timeline-row tree-row" data-depth="0">{syn_label}{syn_track}</div>'
        syn_children = "\n".join(
            _render_tree_row(o, children, axis, today_line, 1, f"orph{i}")
            for i, o in enumerate(orphan_roots)
        )
        parts.append(
            f'<details class="tree-branch" id="tl-unscheduled">'
            f'<summary>{syn_row}</summary>'
            f'<div class="tree-children">{syn_children}</div>'
            f'</details>'
        )

    rows_html = "\n".join(parts)
    legend = ('<div class="chip-strip" style="margin-top:8px;justify-content:flex-start">'
              + "".join(f'<span class="chip"><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:var(--phase-{p});margin-right:6px"></span>{PHASE_LABELS[p]}</span>' for p in PHASE_ORDER)
              + '<span class="chip"><strong>tip:</strong> click a row to expand children</span>'
              + "</div>")
    return rows_html, legend



CONTAINER_TYPES = {"Key Theme", "KeyTheme", "Value Pack", "ValuePack", "Milestone"}


def _render_landing_zones(items: list[Item], axis: list[str]) -> str:
    """Per-quarter landing-zone cards. Lists GitHub milestones + Jira VIs
    scheduled for each quarter with open/closed counts. Walks parent chain
    for GH-issue items so an issue inherits the quarter from its VI when no
    GH milestone is set."""
    by_id = {it.id: it for it in items}
    def effective_q(it: Item) -> str:
        # Prefer self target, else walk parents.
        q = it.target_quarter
        seen: set[str] = set()
        cur = it
        while not q and cur.parent and cur.parent in by_id and cur.parent not in seen:
            seen.add(cur.parent)
            cur = by_id[cur.parent]
            q = cur.target_quarter
        return q

    by_q_gh_ms: dict[str, dict[str, dict]] = {}  # q -> ms_title -> {open,closed,due}
    by_q_vis: dict[str, list[Item]] = {}
    by_q_orphan: dict[str, dict[str, int]] = {}  # q -> {open,closed}
    for it in items:
        q = effective_q(it)
        if not q:
            continue
        if it.issue_type == "ValueIncrement":
            by_q_vis.setdefault(q, []).append(it)
        # GitHub issue?
        if re.fullmatch(r"#\d+", it.id):
            if it.gh_milestone:
                bucket = by_q_gh_ms.setdefault(q, {}).setdefault(
                    it.gh_milestone, {"open": 0, "closed": 0, "due": it.gh_milestone_due}
                )
                bucket["closed" if it.state == "closed" else "open"] += 1
            else:
                bucket = by_q_orphan.setdefault(q, {"open": 0, "closed": 0})
                bucket["closed" if it.state == "closed" else "open"] += 1

    if not (by_q_gh_ms or by_q_vis or by_q_orphan):
        return '<div class="callout">No quarter-scheduled items yet.</div>'

    def _axis_to_norm(lbl: str) -> str:
        m = re.match(r"(\d{4})\s*Q([1-4])", lbl)
        return f"{m.group(1)}-Q{m.group(2)}" if m else lbl

    cards: list[str] = []
    today_q_idx = _today_axis_offset(axis)
    for i, q_label in enumerate(axis):
        q = _axis_to_norm(q_label)
        vis = by_q_vis.get(q, [])
        gh_ms = by_q_gh_ms.get(q, {})
        orphan = by_q_orphan.get(q, {"open": 0, "closed": 0})
        total_gh = sum(v["open"] + v["closed"] for v in gh_ms.values()) + orphan["open"] + orphan["closed"]
        is_today = (int(today_q_idx) == i) if today_q_idx >= 0 else False
        if not (vis or gh_ms or orphan["open"] or orphan["closed"]):
            cards.append(f'<div class="lz-card lz-empty{" lz-today" if is_today else ""}"><h3>{html.escape(q_label)}</h3><p>no items scheduled</p></div>')
            continue
        vis_rows = "".join(
            f'<li><code>{html.escape(v.id)}</code> {html.escape(v.title[:60])} '
            f'<span class="pill pill-target">{html.escape(v.state)}</span></li>'
            for v in sorted(vis, key=lambda x: x.id)
        )
        ms_rows = "".join(
            f'<li><strong>{html.escape(m)}</strong> '
            f'<span class="pill">open {c["open"]}</span>'
            f'<span class="pill pill-done">done {c["closed"]}</span>'
            f'{(" · due " + html.escape(c["due"][:10])) if c.get("due") else ""}</li>'
            for m, c in sorted(gh_ms.items(), key=lambda kv: kv[0])
        )
        orphan_row = ""
        if orphan["open"] or orphan["closed"]:
            orphan_row = (f'<li><em>no GitHub milestone</em> '
                          f'<span class="pill">open {orphan["open"]}</span>'
                          f'<span class="pill pill-done">done {orphan["closed"]}</span></li>')
        cards.append(
            f'<div class="lz-card{" lz-today" if is_today else ""}">'
            f'<h3>{html.escape(q_label)}<span class="lz-count">{total_gh + len(vis)} items</span></h3>'
            + (f'<h4>Value increments · {len(vis)}</h4><ul>{vis_rows}</ul>' if vis else '')
            + (f'<h4>GitHub milestones · {len(gh_ms)}</h4><ul>{ms_rows}{orphan_row}</ul>'
               if (gh_ms or orphan["open"] or orphan["closed"]) else '')
            + '</div>'
        )
    return f'<div class="landing-zones">{"".join(cards)}</div>'


def _render_velocity(items: list[Item]) -> str:
    """Rough weekly burn-rate from GitHub closedAt timestamps + forecast."""
    import datetime as _dt
    now = _dt.datetime.now(_dt.timezone.utc)
    gh_items = [it for it in items if re.fullmatch(r"#\d+", it.id)]
    jira_leaf = [it for it in items if it.issue_type not in CONTAINER_TYPES and not re.fullmatch(r"#\d+", it.id)]
    total_gh = len(gh_items)
    closed_gh = sum(1 for it in gh_items if it.state == "closed")
    open_gh = total_gh - closed_gh
    total_jira = len(jira_leaf)
    closed_jira = sum(1 for it in jira_leaf if it.state == "closed")
    open_jira = total_jira - closed_jira

    # Weekly burn: closed GH items in the last 4, 8, 12 weeks (best-effort parse)
    def _parse_iso(s: str):
        if not s:
            return None
        try:
            return _dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None

    buckets = {4: 0, 8: 0, 12: 0}
    for it in gh_items:
        if it.state != "closed":
            continue
        d = _parse_iso(it.closed_at)
        if not d:
            continue
        if d.tzinfo is None:
            d = d.replace(tzinfo=_dt.timezone.utc)
        age_days = (now - d).days
        for w in (4, 8, 12):
            if age_days <= w * 7:
                buckets[w] += 1

    def rate(weeks: int) -> float:
        return buckets[weeks] / weeks if weeks else 0.0

    velocities = {w: rate(w) for w in (4, 8, 12)}
    # Use 8-week as default forecast.
    vel8 = velocities[8]
    eta_weeks = (open_gh / vel8) if vel8 > 0 else None
    eta_str = f"{eta_weeks:.1f} weeks" if eta_weeks is not None else "–"

    rows = []
    # Per-lane breakdown
    by_id = {it.id: it for it in items}
    def lane_of(it: Item) -> str:
        return it.lane or it.parent or ""
    lane_counts: dict[str, dict[str, int]] = {}
    for it in items:
        if it.issue_type in CONTAINER_TYPES:
            continue
        ln = lane_of(it)
        ln_label = by_id.get(ln, Item(id=ln, title=ln or "—", status="", phase="", tracker="")).title[:60] if ln else "(no lane)"
        b = lane_counts.setdefault(ln_label, {"open": 0, "closed": 0})
        b["closed" if it.state == "closed" else "open"] += 1
    lane_rows = "".join(
        f"<tr><td>{html.escape(k)}</td><td>{v['open']}</td><td>{v['closed']}</td>"
        f"<td>{(100 * v['closed'] / max(v['open']+v['closed'],1)):.0f}%</td></tr>"
        for k, v in sorted(lane_counts.items(), key=lambda kv: -(kv[1]['open']+kv[1]['closed']))
    ) or "<tr><td colspan='4'><em>no items</em></td></tr>"

    return (
        '<div class="velocity-grid">'
        f'<div class="vel-card"><div class="vel-num">{total_gh}</div><div class="vel-lbl">GH issues total</div></div>'
        f'<div class="vel-card"><div class="vel-num">{closed_gh}</div><div class="vel-lbl">GH closed</div></div>'
        f'<div class="vel-card"><div class="vel-num">{open_gh}</div><div class="vel-lbl">GH open</div></div>'
        f'<div class="vel-card"><div class="vel-num">{buckets[4]}</div><div class="vel-lbl">closed / 4w</div></div>'
        f'<div class="vel-card"><div class="vel-num">{buckets[8]}</div><div class="vel-lbl">closed / 8w</div></div>'
        f'<div class="vel-card"><div class="vel-num">{buckets[12]}</div><div class="vel-lbl">closed / 12w</div></div>'
        f'<div class="vel-card vel-card-accent"><div class="vel-num">{vel8:.1f}</div><div class="vel-lbl">issues/week (8w avg)</div></div>'
        f'<div class="vel-card vel-card-accent"><div class="vel-num">{eta_str}</div><div class="vel-lbl">ETA for current open backlog</div></div>'
        '</div>'
        f'<p class="lead"><strong>Jira leaves</strong>: {closed_jira} of {total_jira} closed ({(100*closed_jira/max(total_jira,1)):.0f}%). '
        'Jira is intentionally slower-moving than GitHub; treat this as a lagging indicator.</p>'
        '<details class="details"><summary>Per-lane breakdown</summary><div class="content">'
        '<table><thead><tr><th>lane</th><th>open</th><th>closed</th><th>% done</th></tr></thead>'
        f'<tbody>{lane_rows}</tbody></table></div></details>'
    )


def _render_findings(items: list[Item], axis: list[str]) -> str:
    """Heuristic critical-path / discrepancy findings."""
    by_id = {it.id: it for it in items}
    axis_set = set(axis)
    today_idx = _today_axis_offset(axis)
    today_q = ""
    if today_idx >= 0:
        axis_lbl = axis[int(today_idx)]
        m = re.match(r"(\d{4})\s*Q([1-4])", axis_lbl)
        if m:
            today_q = f"{m.group(1)}-Q{m.group(2)}"
    findings: list[tuple[str, str, list[str]]] = []  # (severity, title, rows)

    # 1. Items past target quarter, still open.
    overdue: list[str] = []
    for it in items:
        if it.issue_type in CONTAINER_TYPES:
            continue
        if it.state != "open" or not it.target_quarter or not today_q:
            continue
        if it.target_quarter < today_q:
            overdue.append(f"<code>{html.escape(it.id)}</code> · {html.escape(it.title[:70])} · target {html.escape(it.target_quarter)}"
                          + (f" · GH milestone <em>{html.escape(it.gh_milestone)}</em>" if it.gh_milestone else ""))
    if overdue:
        findings.append(("high", f"Overdue — open items past target quarter ({len(overdue)})", overdue[:12]))

    # 2. Containers where the latest child target exceeds the container's target.
    children: dict[str, list[Item]] = {}
    for it in items:
        if it.parent:
            children.setdefault(it.parent, []).append(it)
    slipping: list[str] = []
    for it in items:
        if it.issue_type not in CONTAINER_TYPES:
            continue
        if not it.target_quarter:
            continue
        desc_qs: list[str] = []
        stack = list(children.get(it.id, []))
        seen: set[str] = set()
        while stack:
            c = stack.pop()
            if c.id in seen: continue
            seen.add(c.id)
            if c.target_quarter:
                desc_qs.append(c.target_quarter)
            stack.extend(children.get(c.id, []))
        if desc_qs:
            latest = max(desc_qs)
            if latest > it.target_quarter:
                slipping.append(
                    f"<code>{html.escape(it.id)}</code> · {html.escape(it.title[:60])} "
                    f"· own target <strong>{html.escape(it.target_quarter)}</strong> "
                    f"vs latest child <strong>{html.escape(latest)}</strong>"
                )
    if slipping:
        findings.append(("high", f"Container slippage — child targets exceed parent target ({len(slipping)})", slipping[:12]))

    # 3. GitHub issues with no milestone AND no Jira parent.
    orphans: list[str] = []
    for it in items:
        if not re.fullmatch(r"#\d+", it.id):
            continue
        if it.gh_milestone:
            continue
        if it.parent and it.parent in by_id:
            continue
        orphans.append(f"<code>{html.escape(it.id)}</code> · {html.escape(it.title[:70])} · labels {', '.join(it.labels[:4])}")
    if orphans:
        findings.append(("medium", f"Unanchored — GH issues without milestone or Jira parent ({len(orphans)})", orphans[:12]))

    # 4. Value Increments without any GitHub issue attached.
    vi_without_gh: list[str] = []
    for it in items:
        if it.issue_type != "ValueIncrement":
            continue
        has_gh = any(re.fullmatch(r"#\d+", c.id) for c in children.get(it.id, []))
        if not has_gh:
            vi_without_gh.append(f"<code>{html.escape(it.id)}</code> · {html.escape(it.title[:70])} · target {html.escape(it.target_quarter or '–')}")
    if vi_without_gh:
        findings.append(("medium", f"No implementation signal — VIs with no linked GH issues ({len(vi_without_gh)})", vi_without_gh))

    # 5. GH milestones with mixed quarters (cross-check).
    ms_quarters: dict[str, set[str]] = {}
    for it in items:
        if not (re.fullmatch(r"#\d+", it.id) and it.gh_milestone):
            continue
        # Walk parent chain for parent target.
        p = by_id.get(it.parent) if it.parent else None
        parent_q = p.target_quarter if p else ""
        if parent_q and it.target_quarter and parent_q != it.target_quarter:
            ms_quarters.setdefault(f"{it.id} / {it.gh_milestone}", set()).update([it.target_quarter, parent_q])
    mismatches: list[str] = []
    for k, qs in ms_quarters.items():
        if len(qs) > 1:
            mismatches.append(f"<code>{html.escape(k)}</code> · quarters: {', '.join(sorted(qs))}")
    if mismatches:
        findings.append(("medium", f"Quarter mismatch — GH milestone vs Jira parent ({len(mismatches)})", mismatches[:12]))

    # 6. Critical path — VIs targeting the current quarter with highest open GH ratio.
    critical: list[str] = []
    if today_q:
        for it in items:
            if it.issue_type != "ValueIncrement" or it.target_quarter != today_q:
                continue
            gh_children = [c for c in children.get(it.id, []) if re.fullmatch(r"#\d+", c.id)]
            if not gh_children:
                continue
            open_n = sum(1 for c in gh_children if c.state == "open")
            total_n = len(gh_children)
            pct_done = (100 * (total_n - open_n) / total_n) if total_n else 0
            critical.append((pct_done, f"<code>{html.escape(it.id)}</code> · {html.escape(it.title[:55])} · "
                                        f"{open_n}/{total_n} GH issues still open · {pct_done:.0f}% done"))
        critical.sort(key=lambda x: x[0])  # least-done first
        critical_rows = [row for _, row in critical[:10]]
    else:
        critical_rows = []
    if critical_rows:
        findings.append(("high", f"Critical path — current-quarter VIs with open scope (least-done first)", critical_rows))

    if not findings:
        return '<div class="callout">No discrepancies detected. Good hygiene.</div>'

    html_parts: list[str] = []
    for sev, title, rows in findings:
        row_html = "".join(f"<li>{r}</li>" for r in rows)
        html_parts.append(
            f'<details class="details finding finding-{sev}" open>'
            f'<summary><span class="sev-badge sev-{sev}">{sev}</span>{html.escape(title)}</summary>'
            f'<div class="content"><ul class="finding-list">{row_html}</ul></div>'
            f'</details>'
        )
    return "\n".join(html_parts)


def _render_kanban(items: list[Item]) -> str:
    # Exclude container types (Key Theme / Value Pack / Milestone) — the kanban
    # is a deliverables board, not a planning rollup.
    items = [it for it in items if it.issue_type not in CONTAINER_TYPES]
    by_phase: dict[str, list[Item]] = {p: [] for p in PHASE_ORDER}
    for it in items:
        by_phase.setdefault(it.phase or "idea", []).append(it)
    cols: list[str] = []
    for phase in PHASE_ORDER:
        ph_items = sorted(by_phase.get(phase, []),
                          key=lambda x: (x.target_quarter or "~", x.id))
        # Cap per column for readability; the full list is in the plan table.
        visible = ph_items[:12]
        overflow = len(ph_items) - len(visible)
        cards_html = ""
        if not visible:
            cards_html = '<div class="kanban-empty">no items</div>'
        else:
            parts = []
            for it in visible:
                pills = []
                if it.issue_type:
                    pills.append(f'<span class="pill pill-type">{html.escape(it.issue_type)}</span>')
                if it.target:
                    pills.append(f'<span class="pill pill-target">{html.escape(it.target)}</span>')
                elif it.target_quarter:
                    pills.append(f'<span class="pill pill-target">{html.escape(it.target_quarter)}</span>')
                pills_html = "".join(pills)
                parts.append(
                    f'<div class="kanban-card">'
                    f'<div class="id">{html.escape(it.id)}</div>'
                    f'<div class="title">{html.escape(it.title[:120])}</div>'
                    f'<div class="meta">{pills_html}</div>'
                    f'</div>'
                )
            if overflow > 0:
                parts.append(f'<div class="kanban-empty">+{overflow} more in plan table</div>')
            cards_html = "".join(parts)
        cols.append(
            f'<div class="kanban-col" data-phase="{html.escape(phase)}">'
            f'<div class="kanban-col-header"><span class="name">{html.escape(PHASE_LABELS[phase])}</span>'
            f'<span class="count">{len(ph_items)}</span></div>'
            f'<div class="kanban-cards">{cards_html}</div>'
            f'</div>'
        )
    return "\n".join(cols)


def render_html(scope: str, date: str, items: list[Item], groups: dict[str, list[Item]],
                tokens_css: str, logo_light: str, logo_dark: str,
                scope_cfg: dict, roadmap_cfg: dict) -> str:
    def plan_row(it: Item) -> str:
        lane_label = it.lane_title or it.lane or ""
        if it.milestone and it.milestone != it.lane:
            lane_label = f"{lane_label} · {it.milestone}" if lane_label else it.milestone
        return (f"<tr><td><code>{html.escape(it.id)}</code></td>"
                f"<td>{html.escape(it.title[:100])}</td>"
                f"<td>{html.escape(it.issue_type)}</td>"
                f"<td><span class='pill' style='color:var(--phase-{html.escape(it.phase or 'idea')})'>{html.escape(it.phase)}</span></td>"
                f"<td>{html.escape(it.status)}</td>"
                f"<td>{html.escape(it.target)}</td>"
                f"<td>{html.escape(lane_label[:60])}</td>"
                f"<td>{html.escape(it.tracker)}</td></tr>")
    sorted_items = sorted(items, key=lambda x: (PHASE_ORDER.index(x.phase) if x.phase in PHASE_ORDER else 99,
                                                x.lane or "~", x.id))
    plan_rows_html = "\n".join(plan_row(it) for it in sorted_items) or \
                     "<tr><td colspan='8'><em>no items</em></td></tr>"
    corr_rows_html = "\n".join(
        f"<tr><td><code>{html.escape(gid)}</code></td><td>{len(grp)}</td>"
        f"<td>{html.escape(', '.join(sorted({i.tracker for i in grp})))}</td></tr>"
        for gid, grp in sorted(groups.items()) if len(grp) > 1
    ) or "<tr><td colspan='3'><em>no multi-tracker correlations</em></td></tr>"
    multi = sum(1 for g in groups.values() if len(g) > 1)
    single = sum(1 for g in groups.values() if len(g) == 1)
    milestone_count = sum(1 for it in items if it.issue_type in ("Milestone", "Key Theme", "KeyTheme"))
    in_delivery_count = sum(1 for it in items if it.phase == "in-delivery")
    shipped_count = sum(1 for it in items if it.phase == "shipped")
    open_count = sum(1 for it in items if it.state != "closed" and it.issue_type not in CONTAINER_TYPES)
    closed_count = sum(1 for it in items if it.state == "closed" and it.issue_type not in CONTAINER_TYPES)
    gh_ms_titles = {it.gh_milestone for it in items if it.gh_milestone}
    gh_ms_count = len(gh_ms_titles)

    axis = _build_quarter_axis(scope_cfg, roadmap_cfg, items)
    today_offset = _today_axis_offset(axis)
    def _q_span(i: int, q: str) -> str:
        cls = ' class="today"' if int(today_offset) == i else ''
        return f'<span{cls}>{html.escape(q)}</span>'
    axis_quarters_html = "".join(_q_span(i, q) for i, q in enumerate(axis)) or "<span>–</span>"
    timeline_rows_html, timeline_legend_html = _render_timeline(items, axis)
    landing_zones_html = _render_landing_zones(items, axis)
    velocity_html = _render_velocity(items)
    findings_html = _render_findings(items, axis)
    kanban_cols_html = _render_kanban(items)

    logo_img = ""
    if logo_light:
        logo_img = f'<img class="brand-logo brand-logo-light" src="{html.escape(logo_light)}" alt="" height="32">'
        if logo_dark:
            logo_img += f'<img class="brand-logo brand-logo-dark" src="{html.escape(logo_dark)}" alt="" height="32">'

    scope_label = scope_cfg.get("label") or scope.title()
    scope_description = scope_cfg.get("description") or \
        f"Generated roadmap for scope {scope}. {len(items)} items across {milestone_count} milestones."

    return HTML_TEMPLATE.format(
        scope=scope, scope_label=html.escape(scope_label),
        scope_description=html.escape(scope_description),
        date=date,
        plan_count=len(items),
        milestone_count=milestone_count,
        in_delivery_count=in_delivery_count,
        shipped_count=shipped_count,
        open_count=open_count,
        closed_count=closed_count,
        gh_ms_count=gh_ms_count,
        multi_count=multi, single_count=single,
        num_quarters=max(len(axis), 1),
        num_phases=len(PHASE_ORDER),
        axis_quarters_html=axis_quarters_html,
        timeline_rows_html=timeline_rows_html,
        timeline_legend_html=timeline_legend_html,
        landing_zones_html=landing_zones_html,
        velocity_html=velocity_html,
        findings_html=findings_html,
        kanban_cols_html=kanban_cols_html,
        plan_rows_html=plan_rows_html,
        corr_rows_html=corr_rows_html,
        generated_at=dt.datetime.now().isoformat(timespec="minutes"),
        generator="kb-roadmap",
        tokens_css=tokens_css, logo_img=logo_img,
    )



def render_json(scope: str, date: str, items: list[Item], groups: dict[str, list[Item]]) -> str:
    def _item_dict(it: Item) -> dict:
        d = asdict(it)
        # Strip raw.body to keep JSON compact; path stays for traceability.
        if isinstance(d.get("raw"), dict):
            d["raw"] = {k: v for k, v in d["raw"].items() if k != "body"}
        return d
    payload = {
        "scope": scope,
        "date": date,
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "generator": "kb-roadmap",
        "items": [_item_dict(it) for it in items],
        "correlations": [
            {"id": gid, "appearances": len(grp), "trackers": sorted({i.tracker for i in grp})}
            for gid, grp in sorted(groups.items())
        ],
        "summary": {
            "total": len(items),
            "by_phase": {p: sum(1 for i in items if i.phase == p)
                         for p in ["idea", "defined", "committed", "in-delivery", "shipped", "archived"]},
            "correlated": sum(1 for g in groups.values() if len(g) > 1),
            "single_tracker": sum(1 for g in groups.values() if len(g) == 1),
        },
    }
    return json.dumps(payload, indent=2, default=str)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("kb_root", type=Path)
    ap.add_argument("--scope", default=None)
    ap.add_argument("--date", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    kb_root: Path = args.kb_root.resolve()
    cfg = load_config(kb_root)
    roadmap_cfg = cfg.get("roadmap", {})
    if not roadmap_cfg:
        print("kb-roadmap: no roadmap: block in .kb-config/layers.yaml", file=sys.stderr)
        return 1

    scope = args.scope or roadmap_cfg.get("default-scope")
    if not scope:
        print("kb-roadmap: --scope required (no default-scope configured)", file=sys.stderr)
        return 1
    scope_cfg = roadmap_cfg.get("scopes", {}).get(scope)
    if not scope_cfg:
        print(f"kb-roadmap: scope {scope!r} not in roadmap.scopes", file=sys.stderr)
        return 1

    date = args.date or dt.date.today().isoformat()

    items = collect_items(scope_cfg, roadmap_cfg, kb_root)
    groups = correlate_tier1(items)

    # Brand tokens CSS (optional) — spliced into the HTML <style> block verbatim.
    artifacts_cfg = {}
    art_path = _resolve_artifacts_path(kb_root)
    if art_path is not None:
        artifacts_cfg = yaml.safe_load(art_path.read_text(encoding="utf-8")) or {}
    tpl_cfg = artifacts_cfg.get("html-template", {}) or {}
    tokens_path = tpl_cfg.get("tokens")
    tokens_css = ""
    if tokens_path:
        p = (kb_root / tokens_path).resolve()
        if p.exists():
            tokens_css = p.read_text(encoding="utf-8")
    logo_light = tpl_cfg.get("logo", {}).get("light", "")
    logo_dark = tpl_cfg.get("logo", {}).get("dark", "")

    output_dir = (kb_root / roadmap_cfg.get("output-dir", "_kb-roadmaps") / scope).resolve()
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    md = render_md(scope, date, items, groups)
    html_out = render_html(scope, date, items, groups, tokens_css, logo_light, logo_dark,
                           scope_cfg, roadmap_cfg)
    json_out = render_json(scope, date, items, groups)

    if args.dry_run:
        print(f"kb-roadmap (dry-run): {len(items)} items, {sum(1 for g in groups.values() if len(g)>1)} correlated")
        print(f"  would write: {output_dir}/roadmap-{date}.md|.html|.json")
        return 0

    (output_dir / f"roadmap-{date}.md").write_text(md, encoding="utf-8")
    (output_dir / f"roadmap-{date}.html").write_text(html_out, encoding="utf-8")
    (output_dir / f"roadmap-{date}.json").write_text(json_out, encoding="utf-8")
    print(f"kb-roadmap: wrote roadmap-{date}.[md|html|json] to {output_dir}")
    print(f"  items: {len(items)}  correlated: {sum(1 for g in groups.values() if len(g)>1)}  single: {sum(1 for g in groups.values() if len(g)==1)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
