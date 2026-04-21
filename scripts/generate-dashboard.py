#!/usr/bin/env python3
"""Generate a KB command-center dashboard.html.

Complements generate-index.py. While index.html lists HTML artifacts,
dashboard.html surfaces live KB state the owner should have in mind:
focus tasks, active ideas, open decisions, pending inputs, recent
findings & reports, workstream freshness, and (opt-in) external
work-items from GitHub and Jira.

Panels are config-driven via .kb-config/artifacts.yaml → `dashboard:`
section. Unknown or disabled panels are silently skipped so the same
script works for personal, team, and org-unit KBs.

Usage:
    python generate-dashboard.py [REPO_ROOT] [--title TITLE] [--output dashboard.html]

Designed to be copied into .kb-scripts/ of any KB layer.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


# ── Theme: reuse the same tokens as generate-index.py ─────────────────

DEFAULT_THEME = {
    'dark': {
        'bg': '#0b0d13', 'bg_elevated': '#10131c', 'bg_card': '#151a26',
        'bg_hover': '#1b2133', 'border': '#1e2436', 'border_strong': '#2a3248',
        'text': '#eaecf2', 'text_sec': '#8a90a8', 'text_dim': '#555d76',
        'accent': '#1496FF', 'accent_hover': '#42aaff',
        'accent_bg': 'rgba(20,150,255,0.10)',
        'badge_bg': 'rgba(111,45,168,0.16)', 'badge_fg': '#a78bfa',
        'shadow': '0 2px 12px rgba(0,0,0,0.3)',
    },
    'light': {
        'bg': '#f4f5f8', 'bg_elevated': '#ffffff', 'bg_card': '#ffffff',
        'bg_hover': '#f0f1f6', 'border': '#d8dce6', 'border_strong': '#c0c6d4',
        'text': '#141824', 'text_sec': '#4d5570', 'text_dim': '#8a90a8',
        'accent': '#1284EA', 'accent_hover': '#1496FF',
        'accent_bg': 'rgba(20,150,255,0.08)',
        'badge_bg': 'rgba(111,45,168,0.10)', 'badge_fg': '#591F91',
        'shadow': '0 2px 12px rgba(0,0,0,0.06)',
    },
}

DEFAULT_DASHBOARD = {
    'enabled': True,
    'panels': [
        'focus-tasks', 'pending-inputs', 'active-ideas', 'open-decisions',
        'recent-findings', 'recent-reports', 'workstreams',
    ],
    'limits': {
        'recent-findings': 5,
        'recent-reports': 3,
        'recent-digests': 3,
        'active-ideas': 8,
        'open-decisions': 8,
        'workstreams': 10,
        'github': 10,
        'jira': 10,
    },
    'external': {
        'github': {'enabled': False, 'query': 'assignee:@me is:open', 'repos': []},
        'jira': {'enabled': False, 'source': 'path', 'path': '',
                 'assignee': '', 'status_exclude': []},
    },
}


def _load_yaml(path: Path) -> dict:
    if not path.exists() or yaml is None:
        return {}
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def load_config(repo_root: Path) -> tuple[dict, dict]:
    """Return (theme, dashboard_cfg). Looks in both .kb-config/artifacts.yaml
    and legacy .kb-artifacts.yaml at the repo root."""
    cfg = {}
    for candidate in (repo_root / '.kb-config' / 'artifacts.yaml',
                      repo_root / '.kb-artifacts.yaml'):
        loaded = _load_yaml(candidate)
        if loaded:
            cfg = loaded
            break

    # Theme
    theme = DEFAULT_THEME
    styling = cfg.get('styling', {}) or {}
    if styling.get('source') == 'template':
        ref_file = styling.get('reference-file')
        if ref_file:
            ref_path = repo_root / ref_file
            if ref_path.exists():
                extracted = _extract_theme_from_template(ref_path)
                if extracted:
                    theme = extracted

    # Dashboard
    dash = _merge_dashboard(DEFAULT_DASHBOARD, cfg.get('dashboard', {}) or {})
    # Merge top-level `brand:` section into dashboard cfg for convenience.
    brand = cfg.get('brand', {}) or {}
    if brand:
        dash.setdefault('brand', {}).update(brand)
    return theme, dash


# ── Brand logos ────────────────────────────────────────────────────────

# Inline SVG logos, keyed by name. 'hexagon' is the vendor-neutral default.
# Adopters opt in via `.kb-config/artifacts.yaml` → `brand: {logo: <name>}`.
BRAND_LOGOS = {
    'hexagon': (
        '<svg width="28" height="28" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M50 5L90 27.5V72.5L50 95L10 72.5V27.5L50 5Z" fill="var(--accent)" opacity="0.15"/>'
        '<path d="M50 15L80 32.5V67.5L50 85L20 67.5V32.5L50 15Z" stroke="var(--accent)" stroke-width="2" fill="none"/>'
        '<circle cx="50" cy="50" r="8" fill="var(--accent)"/>'
        '</svg>'
    ),
    'none': '',
}


def render_brand_logo(repo_root: Path, dash: dict) -> str:
    """Return the inline SVG/HTML for the dashboard brand logo.

    Config keys (all under `brand:`):
      - logo: one of the named logos ('hexagon' default, 'none')
      - logo-file: optional path to a .svg file (relative to repo root); overrides `logo`
    """
    brand = (dash.get('brand') or {}) if dash else {}
    logo_file = brand.get('logo-file')
    if logo_file:
        candidate = Path(logo_file)
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        if candidate.exists():
            try:
                svg = candidate.read_text(encoding='utf-8', errors='ignore').strip()
                # Strip XML prolog if any.
                svg = re.sub(r'^<\?xml[^>]*\?>\s*', '', svg)
                return svg
            except Exception:
                pass
    name = (brand.get('logo') or 'hexagon').lower()
    return BRAND_LOGOS.get(name, BRAND_LOGOS['hexagon'])


def _merge_dashboard(base: dict, override: dict) -> dict:
    out = {k: (dict(v) if isinstance(v, dict) else list(v) if isinstance(v, list) else v)
           for k, v in base.items()}
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge_dashboard(out[k], v)
        else:
            out[k] = v
    return out


def _extract_theme_from_template(template_path: Path) -> dict | None:
    """Extract CSS variable values from a reference template."""
    try:
        text = template_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return None
    var_map = {
        '--bg': 'bg',
        '--bg-elevated': 'bg_elevated',
        '--bg-card': 'bg_card',
        '--bg-card-hover': 'bg_hover', '--bg-hover': 'bg_hover',
        '--border': 'border',
        '--border-strong': 'border_strong',
        '--text': 'text', '--fg': 'text',
        '--text-secondary': 'text_sec', '--fg-muted': 'text_sec',
        '--text-tertiary': 'text_dim', '--fg-dim': 'text_dim',
        '--accent': 'accent',
        '--accent-hover': 'accent_hover',
        '--accent-bg': 'accent_bg',
        '--badge-bg': 'badge_bg',
        '--badge-fg': 'badge_fg',
        '--shadow': 'shadow',
    }
    var_re = re.compile(r'(--[\w-]+)\s*:\s*([^;]+);')
    dark = dict(DEFAULT_THEME['dark'])
    light = dict(DEFAULT_THEME['light'])
    for m in var_re.finditer(text):
        name, value = m.group(1), m.group(2).strip()
        token = var_map.get(name)
        if not token or 'var(' in value:
            continue
        preceding = text[:m.start()]
        if '[data-theme="light"]' in preceding[max(0, len(preceding)-500):]:
            light[token] = value
        else:
            dark[token] = value
    return {'dark': dark, 'light': light}


# ── Panel data model ───────────────────────────────────────────────────

@dataclass
class Row:
    title: str
    href: str = ''          # relative link or empty
    meta: str = ''          # right-aligned small text (date, status, etc.)
    badges: list[str] = field(default_factory=list)
    sub: str = ''           # optional second line


@dataclass
class Panel:
    key: str
    title: str
    rows: list[Row] = field(default_factory=list)
    empty: str = 'Nothing here yet.'
    note: str = ''          # small grey text under heading
    count: int | None = None    # overrides len(rows) in header badge


# ── Panel collectors ───────────────────────────────────────────────────

TASK_ITEM_RE = re.compile(r'^\s*(?:\d+\.|[-*])\s+(.*)$')


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''


def _strip_md(s: str) -> str:
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
    s = re.sub(r'`(.+?)`', r'\1', s)
    s = re.sub(r'\[(.+?)\]\([^)]+\)', r'\1', s)
    return s.strip()


def _parse_list_items(md: str, limit: int) -> list[str]:
    items = []
    for line in md.splitlines():
        if line.startswith('#') or line.startswith('>'):
            continue
        m = TASK_ITEM_RE.match(line)
        if m:
            items.append(_strip_md(m.group(1)))
        if len(items) >= limit:
            break
    return items


def panel_focus_tasks(repo_root: Path, dash: dict) -> Panel | None:
    fp = repo_root / '_kb-tasks' / 'focus.md'
    if not fp.exists():
        return None
    items = _parse_list_items(_read_text(fp), limit=10)
    panel = Panel(key='focus-tasks', title='Focus', note='Max 6 — what you\'re on right now',
                  empty='No focus items — add with `/kb task`.')
    for item in items:
        panel.rows.append(Row(title=item, href='_kb-tasks/focus.md'))
    return panel


def panel_backlog_count(repo_root: Path, dash: dict) -> Panel | None:
    fp = repo_root / '_kb-tasks' / 'backlog.md'
    if not fp.exists():
        return None
    items = _parse_list_items(_read_text(fp), limit=5)
    total = len([l for l in _read_text(fp).splitlines() if TASK_ITEM_RE.match(l)])
    panel = Panel(key='backlog', title='Backlog',
                  note=f'{total} item{"s" if total != 1 else ""} total — showing top 5',
                  empty='Backlog clean.')
    panel.count = total
    for item in items:
        panel.rows.append(Row(title=item, href='_kb-tasks/backlog.md'))
    return panel


def panel_pending_inputs(repo_root: Path, dash: dict) -> Panel | None:
    inputs_dir = repo_root / '_kb-inputs'
    if not inputs_dir.is_dir():
        return None
    # Non-digested top-level files
    items = []
    for fp in sorted(inputs_dir.iterdir()):
        if fp.is_file() and fp.suffix.lower() in ('.md', '.txt') and fp.name.lower() != 'readme.md':
            items.append(fp)
    panel = Panel(key='pending-inputs', title='Pending Inputs',
                  note='Un-digested captures in `_kb-inputs/` — run `/kb review`',
                  empty='Inbox empty.')
    for fp in items[:10]:
        rel = str(fp.relative_to(repo_root))
        title = fp.stem.replace('-', ' ').replace('_', ' ')
        mtime = datetime.fromtimestamp(fp.stat().st_mtime).strftime('%Y-%m-%d')
        panel.rows.append(Row(title=title, href=rel, meta=mtime))
    panel.count = len(items)
    return panel


IDEA_STATUS_RE = re.compile(r'^\*\*Status\*\*\s*:\s*(.+?)\s*$', re.MULTILINE)
IDEA_TITLE_RE = re.compile(r'^#\s+(?:Idea:\s*)?(.+?)\s*$', re.MULTILINE)


def _parse_meta_field(text: str, field_name: str) -> str:
    m = re.search(rf'^\*\*{re.escape(field_name)}\*\*\s*:\s*(.+?)\s*$',
                  text, re.MULTILINE)
    return m.group(1).strip() if m else ''


def panel_active_ideas(repo_root: Path, dash: dict) -> Panel | None:
    ideas_dir = repo_root / '_kb-ideas'
    if not ideas_dir.is_dir():
        return None
    limit = int(dash.get('limits', {}).get('active-ideas', 8))
    panel = Panel(key='active-ideas', title='Active Ideas',
                  note='Non-archived ideas — `/kb develop` to sparring-partner them',
                  empty='No active ideas.')
    files = []
    for fp in sorted(ideas_dir.glob('I-*.md')):
        text = _read_text(fp)
        status = _parse_meta_field(text, 'Status').lower()
        if status in ('shipped', 'archived', 'dropped'):
            continue
        m = IDEA_TITLE_RE.search(text)
        title = m.group(1).strip() if m else fp.stem
        files.append((fp, title, status or 'seed'))
    files.sort(key=lambda x: x[0].stat().st_mtime, reverse=True)
    for fp, title, status in files[:limit]:
        rel = str(fp.relative_to(repo_root))
        panel.rows.append(Row(title=title, href=rel,
                              badges=[status] if status else []))
    panel.count = len(files)
    return panel


def panel_open_decisions(repo_root: Path, dash: dict) -> Panel | None:
    dec_dir = repo_root / '_kb-decisions'
    if not dec_dir.is_dir():
        return None
    limit = int(dash.get('limits', {}).get('open-decisions', 8))
    panel = Panel(key='open-decisions', title='Open Decisions',
                  note='Undecided items — `/kb decide resolve D-id` to close',
                  empty='No open decisions.')
    files = []
    for fp in sorted(dec_dir.glob('D-*.md')):
        text = _read_text(fp)
        status = _parse_meta_field(text, 'Status').lower()
        if status in ('resolved', 'decided', 'closed', 'superseded'):
            continue
        m = re.search(r'^#\s+(?:Decision:\s*)?(.+?)\s*$', text, re.MULTILINE)
        title = m.group(1).strip() if m else fp.stem
        files.append((fp, title, status or 'open'))
    files.sort(key=lambda x: x[0].stat().st_mtime, reverse=True)
    for fp, title, status in files[:limit]:
        rel = str(fp.relative_to(repo_root))
        panel.rows.append(Row(title=title, href=rel, badges=[status] if status else []))
    panel.count = len(files)
    return panel


FINDING_FILENAME_RE = re.compile(r'(\d{4}-\d{2}-\d{2})-(.+?)\.md$')


def _recent_md_files(directory: Path, limit: int) -> list[tuple[Path, str, str]]:
    """Return [(path, date, title), ...] newest first."""
    out = []
    if not directory.is_dir():
        return out
    for fp in directory.glob('*.md'):
        m = FINDING_FILENAME_RE.search(fp.name)
        date = m.group(1) if m else datetime.fromtimestamp(fp.stat().st_mtime).strftime('%Y-%m-%d')
        # title from first heading
        text = _read_text(fp)
        tm = re.search(r'^#\s+(.+?)\s*$', text, re.MULTILINE)
        title = tm.group(1).strip() if tm else fp.stem
        title = re.sub(r'^(Finding|Topic|Digest):\s*', '', title, flags=re.IGNORECASE)
        out.append((fp, date, title))
    out.sort(key=lambda x: x[1], reverse=True)
    return out[:limit]


def panel_recent_findings(repo_root: Path, dash: dict) -> Panel | None:
    limit = int(dash.get('limits', {}).get('recent-findings', 5))
    findings_dir = repo_root / '_kb-references' / 'findings'
    items = _recent_md_files(findings_dir, limit)
    if not items:
        return None
    panel = Panel(key='recent-findings', title='Recent Findings',
                  note=f'Latest {limit} from `_kb-references/findings/`',
                  empty='No findings yet.')
    for fp, date, title in items:
        panel.rows.append(Row(title=title, href=str(fp.relative_to(repo_root)), meta=date))
    return panel


def panel_recent_digests(repo_root: Path, dash: dict) -> Panel | None:
    limit = int(dash.get('limits', {}).get('recent-digests', 3))
    sd_dir = repo_root / '_kb-references' / 'strategy-digests'
    candidates: list[tuple[Path, str, str]] = []
    if sd_dir.is_dir():
        candidates.extend(_recent_md_files(sd_dir, limit))
    # Also digest-named findings
    findings_dir = repo_root / '_kb-references' / 'findings'
    if findings_dir.is_dir():
        for fp in findings_dir.glob('*digest*.md'):
            m = FINDING_FILENAME_RE.search(fp.name)
            date = m.group(1) if m else ''
            tm = re.search(r'^#\s+(.+?)\s*$', _read_text(fp), re.MULTILINE)
            title = (tm.group(1).strip() if tm else fp.stem)
            candidates.append((fp, date, title))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[1], reverse=True)
    panel = Panel(key='recent-digests', title='Recent Digests',
                  note='Strategy + workstream digests',
                  empty='No digests yet.')
    for fp, date, title in candidates[:limit]:
        panel.rows.append(Row(title=title, href=str(fp.relative_to(repo_root)), meta=date))
    return panel


def panel_recent_reports(repo_root: Path, dash: dict) -> Panel | None:
    limit = int(dash.get('limits', {}).get('recent-reports', 3))
    reports_dir = repo_root / '_kb-references' / 'reports'
    if not reports_dir.is_dir():
        return None
    htmls = []
    date_re = re.compile(r'(\d{4}-\d{2}-\d{2})')
    for fp in reports_dir.glob('*.html'):
        m = date_re.search(fp.name)
        date = m.group(1) if m else datetime.fromtimestamp(fp.stat().st_mtime).strftime('%Y-%m-%d')
        title_m = re.search(r'<title[^>]*>(.*?)</title>', _read_text(fp), re.IGNORECASE | re.DOTALL)
        title = (title_m.group(1).strip() if title_m else fp.stem)
        for sep in (' — ', ' | ', ' - '):
            if sep in title:
                title = title.split(sep)[0].strip()
        htmls.append((fp, date, title))
    htmls.sort(key=lambda x: x[1], reverse=True)
    if not htmls:
        return None
    panel = Panel(key='recent-reports', title='Recent Reports',
                  note=f'Latest {limit} generated reports',
                  empty='No reports yet.')
    for fp, date, title in htmls[:limit]:
        panel.rows.append(Row(title=title, href=str(fp.relative_to(repo_root)), meta=date))
    return panel


def panel_workstreams(repo_root: Path, dash: dict) -> Panel | None:
    # Spec: _kb-workstreams/ at repo root. Some deployments also keep
    # Jira-synced digests under _kb-references/workstreams/ — include both.
    candidates = [repo_root / '_kb-workstreams',
                  repo_root / '_kb-references' / 'workstreams']
    dirs = [d for d in candidates if d.is_dir()]
    if not dirs:
        return None
    limit = int(dash.get('limits', {}).get('workstreams', 10))
    rows = []
    seen_names = set()
    files = []
    for d in dirs:
        for fp in d.glob('*.md'):
            if fp.stem in seen_names:
                continue
            seen_names.add(fp.stem)
            files.append(fp)
    for fp in sorted(files):
        mtime = datetime.fromtimestamp(fp.stat().st_mtime)
        date = mtime.strftime('%Y-%m-%d')
        # stale if > 21 days
        stale = (datetime.now() - mtime) > timedelta(days=21)
        title = fp.stem.replace('-', ' ').title()
        rows.append((fp, date, title, stale))
    rows.sort(key=lambda x: x[1], reverse=True)
    if not rows:
        return None
    panel = Panel(key='workstreams', title='Workstreams',
                  note='Last-updated per workstream file',
                  empty='No workstreams tracked.')
    for fp, date, title, stale in rows[:limit]:
        badges = ['stale'] if stale else []
        panel.rows.append(Row(title=title, href=str(fp.relative_to(repo_root)),
                              meta=date, badges=badges))
    return panel


# ── External: GitHub ───────────────────────────────────────────────────

def panel_github(repo_root: Path, dash: dict) -> Panel | None:
    gh_cfg = (dash.get('external', {}) or {}).get('github', {}) or {}
    if not gh_cfg.get('enabled'):
        return None
    limit = int(dash.get('limits', {}).get('github', 10))
    query = gh_cfg.get('query', 'assignee:@me is:open is:issue')
    repos = gh_cfg.get('repos', []) or []

    # `gh search issues` expects each qualifier as a separate positional
    # argument, not a single quoted string. Tokenize via shlex.
    try:
        query_tokens = shlex.split(query)
    except ValueError:
        query_tokens = query.split()
    cmd = ['gh', 'search', 'issues', *query_tokens,
           '--limit', str(limit),
           '--json', 'title,url,repository,updatedAt,state,isPullRequest']
    if repos:
        for r in repos:
            cmd.extend(['--repo', r])
    try:
        out = subprocess.check_output(cmd, cwd=repo_root,
                                       stderr=subprocess.PIPE, text=True)
        items = json.loads(out)
    except subprocess.CalledProcessError as e:
        panel = Panel(key='github', title='GitHub',
                      empty=f'gh search failed: {(e.stderr or "").strip()[:200] or "unknown error"}')
        panel.note = f'Query: `{query}`'
        return panel
    except (FileNotFoundError, json.JSONDecodeError):
        panel = Panel(key='github', title='GitHub',
                      empty='`gh` CLI unavailable or unauthenticated.')
        panel.note = 'Install & authenticate `gh` to enable this panel.'
        return panel

    panel = Panel(key='github', title='GitHub',
                  note=f'Open items matching `{query}`',
                  empty='No matching issues/PRs.')
    for it in items[:limit]:
        repo = it.get('repository', {}).get('nameWithOwner', '') if isinstance(it.get('repository'), dict) else ''
        title = it.get('title', '')
        url = it.get('url', '')
        updated = (it.get('updatedAt') or '')[:10]
        is_pr = it.get('isPullRequest')
        badges = ['pr'] if is_pr else ['issue']
        panel.rows.append(Row(title=title, href=url, meta=updated,
                              badges=badges, sub=repo))
    return panel


# ── External: Jira (via jira-sync-style markdown with YAML frontmatter) ─

def panel_jira(repo_root: Path, dash: dict) -> Panel | None:
    j_cfg = (dash.get('external', {}) or {}).get('jira', {}) or {}
    if not j_cfg.get('enabled'):
        return None
    source = j_cfg.get('source', 'path')
    if source != 'path':
        return None  # other sources not yet implemented
    path_str = j_cfg.get('path', '')
    if not path_str:
        return None
    jpath = Path(path_str)
    if not jpath.is_absolute():
        jpath = (repo_root / jpath).resolve()
    if not jpath.is_dir():
        return None
    limit = int(dash.get('limits', {}).get('jira', 10))
    assignee_filter = (j_cfg.get('assignee') or '').strip().lower()
    status_exclude = [s.lower() for s in (j_cfg.get('status_exclude') or [])]

    items = []
    for fp in jpath.rglob('*.md'):
        text = _read_text(fp)
        if not text.startswith('---'):
            continue
        # crude frontmatter parse
        try:
            _, fm, _ = text.split('---', 2)
        except ValueError:
            continue
        if yaml is None:
            continue
        try:
            meta = yaml.safe_load(fm) or {}
        except Exception:
            continue
        if not isinstance(meta, dict):
            continue
        status = str(meta.get('status', '')).lower()
        if status in status_exclude:
            continue
        assignee = str(meta.get('assignee', '')).lower()
        if assignee_filter and assignee_filter not in assignee:
            continue
        key = str(meta.get('key', fp.stem))
        summary = str(meta.get('summary', ''))
        updated = str(meta.get('updated', ''))[:10]
        items.append((updated, key, summary, meta.get('status', ''), meta.get('issueType', '')))
    items.sort(reverse=True)
    if not items:
        return None
    panel = Panel(key='jira', title='Jira',
                  note=f'Filtered from `{path_str}`' + (
                      f' · assignee contains "{assignee_filter}"' if assignee_filter else ''),
                  empty='No matching Jira items.')
    for updated, key, summary, status, itype in items[:limit]:
        badges = []
        if status:
            badges.append(str(status).lower())
        if itype:
            badges.append(str(itype).lower())
        panel.rows.append(Row(title=f'{key} · {summary}', meta=updated, badges=badges))
    panel.count = len(items)
    return panel


PANEL_BUILDERS = {
    'focus-tasks': panel_focus_tasks,
    'backlog': panel_backlog_count,
    'pending-inputs': panel_pending_inputs,
    'active-ideas': panel_active_ideas,
    'open-decisions': panel_open_decisions,
    'recent-findings': panel_recent_findings,
    'recent-digests': panel_recent_digests,
    'recent-reports': panel_recent_reports,
    'workstreams': panel_workstreams,
    'github': panel_github,
    'jira': panel_jira,
}


# ── HTML generation ────────────────────────────────────────────────────

def _render_row(row: Row) -> str:
    title_html = html.escape(row.title)
    if row.href:
        target = ' target="_blank" rel="noopener"' if row.href.startswith(('http://', 'https://')) else ''
        title_html = f'<a href="{html.escape(row.href)}"{target}>{title_html}</a>'
    badges_inner = ''.join(f'<span class="badge">{html.escape(b)}</span>' for b in row.badges)
    badges_html = f'<div class="row-badges">{badges_inner}</div>' if badges_inner else ''
    meta = html.escape(row.meta)
    sub = f'<div class="row-sub">{html.escape(row.sub)}</div>' if row.sub else ''
    return (
        '      <li class="row">\n'
        f'        <div class="row-main"><span class="row-title">{title_html}</span>{sub}{badges_html}</div>\n'
        f'        <div class="row-meta"><span class="row-date">{meta}</span></div>\n'
        '      </li>'
    )


def _render_panel(p: Panel) -> str:
    count = p.count if p.count is not None else len(p.rows)
    count_html = f' <span class="count">{count}</span>' if count else ''
    note = f'<p class="panel-note">{html.escape(p.note)}</p>' if p.note else ''
    if not p.rows:
        body = f'    <p class="panel-empty">{html.escape(p.empty)}</p>'
    else:
        rows = '\n'.join(_render_row(r) for r in p.rows)
        body = f'    <ul class="rows">\n{rows}\n    </ul>'
    return (
        '  <section class="panel">\n'
        f'    <h2>{html.escape(p.title)}{count_html}</h2>\n'
        f'    {note}\n'
        f'{body}\n'
        '  </section>'
    )


def generate_html(panels: list[Panel], title: str, description: str,
                  now: str, theme: dict, total_open: int,
                  brand_svg: str = '') -> str:
    dark = theme['dark']
    light = theme['light']
    panels_html = '\n\n'.join(_render_panel(p) for p in panels)
    if not brand_svg:
        brand_svg = BRAND_LOGOS['hexagon']
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Dashboard</title>
<meta name="generator" content="agentic-kb/generate-dashboard">
<meta name="generated" content="{now}">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root, [data-theme="dark"] {{
  --bg:{dark['bg']}; --bg-elevated:{dark['bg_elevated']}; --bg-card:{dark['bg_card']};
  --bg-hover:{dark['bg_hover']}; --border:{dark['border']}; --border-strong:{dark['border_strong']};
  --text:{dark['text']}; --text-sec:{dark['text_sec']}; --text-dim:{dark['text_dim']};
  --accent:{dark['accent']}; --accent-hover:{dark['accent_hover']}; --accent-bg:{dark['accent_bg']};
  --badge-bg:{dark['badge_bg']}; --badge-fg:{dark['badge_fg']}; --shadow:{dark['shadow']};
}}
[data-theme="light"] {{
  --bg:{light['bg']}; --bg-elevated:{light['bg_elevated']}; --bg-card:{light['bg_card']};
  --bg-hover:{light['bg_hover']}; --border:{light['border']}; --border-strong:{light['border_strong']};
  --text:{light['text']}; --text-sec:{light['text_sec']}; --text-dim:{light['text_dim']};
  --accent:{light['accent']}; --accent-hover:{light['accent_hover']}; --accent-bg:{light['accent_bg']};
  --badge-bg:{light['badge_bg']}; --badge-fg:{light['badge_fg']}; --shadow:{light['shadow']};
}}

html, body {{
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
               'Segoe UI', sans-serif;
  background: var(--bg); color: var(--text);
  line-height: 1.55; -webkit-font-smoothing: antialiased;
}}
main {{ max-width: 1100px; margin: 0 auto; padding: 2.5rem 1.5rem 5rem; }}

.header {{ display: flex; align-items: center; gap: 1rem; margin-bottom: 0.25rem; }}
h1 {{ font-size: 1.75rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.2; }}
.lead {{ font-size: 1rem; color: var(--text-sec); margin-top: 0.15rem; }}
.watermark {{ font-size: 0.72rem; color: var(--text-dim);
  letter-spacing: 0.06em; font-variant: all-small-caps; margin: 0.2rem 0 1.8rem; }}

.theme-toggle {{
  position: fixed; top: 1rem; right: 1rem;
  width: 36px; height: 36px; border-radius: 8px;
  border: 1px solid var(--border-strong);
  background: var(--bg-elevated); color: var(--text);
  cursor: pointer; font-size: 1rem; display: grid; place-items: center;
  box-shadow: var(--shadow); transition: border-color 0.15s;
}}
.theme-toggle:hover {{ border-color: var(--accent); }}

.top-nav {{
  display: flex; gap: 0.6rem; margin-bottom: 1.6rem; flex-wrap: wrap;
}}
.top-nav a {{
  font-size: 0.82rem; color: var(--accent); text-decoration: none;
  padding: 0.3rem 0.7rem; border: 1px solid var(--border);
  background: var(--bg-card); border-radius: 999px;
}}
.top-nav a:hover {{ border-color: var(--accent); background: var(--accent-bg); }}

.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 1rem;
}}
.panel {{
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 12px; padding: 1rem 1.15rem 1.1rem;
  box-shadow: var(--shadow);
}}
.panel h2 {{
  font-size: 0.98rem; font-weight: 600;
  display: flex; align-items: center; gap: 0.5rem;
  margin-bottom: 0.15rem;
}}
.panel .count {{
  font-size: 0.7rem; font-weight: 500;
  background: var(--accent-bg); color: var(--accent);
  padding: 0.1rem 0.45rem; border-radius: 10px;
}}
.panel-note {{
  font-size: 0.75rem; color: var(--text-dim);
  margin: 0 0 0.65rem; line-height: 1.4;
}}
.panel-empty {{
  font-size: 0.85rem; color: var(--text-sec);
  padding: 0.4rem 0;
}}
.rows {{ list-style: none; padding: 0; margin: 0; }}
.row {{
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 0.7rem; padding: 0.45rem 0;
  border-bottom: 1px dashed var(--border);
  font-size: 0.88rem;
}}
.row:last-child {{ border-bottom: none; }}
.row-main {{
  flex: 1 1 auto; min-width: 0;
  overflow-wrap: break-word; word-break: break-word;
}}
.row-title {{
  color: var(--text); line-height: 1.4;
  display: block;
}}
.row-title a {{ color: var(--accent); text-decoration: none; }}
.row-title a:hover {{ text-decoration: underline; }}
.row-sub {{ font-size: 0.72rem; color: var(--text-dim); margin-top: 0.1rem; }}
.row-badges {{
  display: flex; flex-wrap: wrap; gap: 0.3rem;
  margin-top: 0.2rem;
}}
.row-meta {{
  display: flex; align-items: center; gap: 0.35rem;
  flex: 0 0 auto; white-space: nowrap;
  font-size: 0.72rem; color: var(--text-dim);
  padding-top: 0.1rem;
}}
.row-date {{ font-variant-numeric: tabular-nums; }}
.badge {{
  font-size: 0.6rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.03em;
  background: var(--badge-bg); color: var(--badge-fg);
  padding: 0.08rem 0.4rem; border-radius: 4px;
  white-space: nowrap;
}}

.legend {{
  margin-top: 2rem; padding: 0.7rem 1rem;
  border: 1px solid var(--border); background: var(--bg-card);
  border-radius: 8px; font-size: 0.78rem; color: var(--text-sec);
  line-height: 1.55;
}}
.legend code {{ background: var(--bg-hover); padding: 0.05rem 0.3rem;
  border-radius: 3px; font-size: 0.9em; }}
</style>
</head>
<body>
<button class="theme-toggle" type="button" aria-label="Toggle theme"
  onclick="var h=document.documentElement,t=h.getAttribute('data-theme');h.setAttribute('data-theme',t==='dark'?'light':'dark');this.textContent=t==='dark'?'\u2600':'\u263E'">\u263E</button>
<main>
  <div class="header">
    {brand_svg}
    <div>
      <h1>{html.escape(title)}</h1>
      <p class="lead">{html.escape(description or "What you should have in mind right now.")}</p>
    </div>
  </div>
  <p class="watermark">command center &middot; {now} &middot; {total_open} open items tracked</p>

  <nav class="top-nav">
    <a href="index.html">&larr; Artifact index</a>
  </nav>

  <div class="grid">
{panels_html}
  </div>

  <p class="legend">
    Auto-generated by <code>generate-dashboard.py</code>. Panels read live KB state on each run.
    Configure via <code>.kb-config/artifacts.yaml</code> → <code>dashboard:</code>.
    External panels (GitHub / Jira) are opt-in and require the underlying tool or data source.
  </p>
</main>
</body>
</html>'''


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate KB command-center dashboard.html')
    parser.add_argument('root', nargs='?', default='.', help='Repository root')
    parser.add_argument('--title', default=None)
    parser.add_argument('--description', default='')
    parser.add_argument('--output', default='dashboard.html')
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    if not repo_root.is_dir():
        sys.exit(f'Not a directory: {repo_root}')

    theme, dash = load_config(repo_root)
    if not dash.get('enabled', True):
        print('Dashboard disabled via config; skipping.')
        return

    title = args.title or f'{repo_root.name} KB'
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    panels: list[Panel] = []
    for key in dash.get('panels', []):
        builder = PANEL_BUILDERS.get(key)
        if not builder:
            print(f'Warning: unknown panel "{key}"', file=sys.stderr)
            continue
        try:
            panel = builder(repo_root, dash)
        except Exception as e:
            print(f'Warning: panel "{key}" failed: {e}', file=sys.stderr)
            panel = None
        if panel is not None:
            panels.append(panel)

    total_open = sum((p.count if p.count is not None else len(p.rows)) for p in panels)
    brand_svg = render_brand_logo(repo_root, dash)
    out_html = generate_html(panels, title, args.description, now, theme, total_open, brand_svg)
    outpath = repo_root / args.output
    outpath.write_text(out_html, encoding='utf-8')

    rendered = ', '.join(f'{p.key}({p.count if p.count is not None else len(p.rows)})' for p in panels)
    print(f'Generated {outpath} — {len(panels)} panels: {rendered}')


if __name__ == '__main__':
    main()
