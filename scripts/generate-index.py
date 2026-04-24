#!/usr/bin/env python3
"""Generate a root index.html for an agentic-kb layer.

Scans the repository for HTML artifacts (reports, presentations, specs,
journey maps, mocks, etc.) and produces a self-contained index.html with
dark/light toggle and GitHub-Pages-ready relative links.

Styling is read from .kb-config/artifacts.yaml when present (source=template
or source=website derive tokens from the reference). Falls back to a neutral
theme if no config exists.

Usage:
    python generate-index.py [REPO_ROOT] [--title TITLE] [--description DESC]

If REPO_ROOT is omitted, uses the current directory.
Designed to be copied into .kb-scripts/ of any KB layer.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import NamedTuple

try:
    import yaml  # PyYAML — optional
except ImportError:
    yaml = None  # type: ignore[assignment]


class Artifact(NamedTuple):
    path: str          # relative to repo root
    title: str         # extracted from <title> or filename
    date: str          # YYYY-MM-DD
    category: str      # grouping label
    contributor: str   # for team KBs, empty for personal
    family: str        # dedup key — normalized stem, dir-scoped
    summary: str       # short "what is this" blurb — meta description or first heading/paragraph


# ── Index config defaults ──────────────────────────────────────────────

DEFAULT_INDEX_CONFIG = {
    'stale_after_days': 14,
    'pinned_categories': ['Journey Maps', 'Roadmap & Status'],
    'dedup_versioned': True,
    'drop_referenced_subpages': True,
    'category_order': 'recency',   # or 'fixed'
}


# ── Theme tokens ───────────────────────────────────────────────────────

# Neutral default theme — vendor-neutral tokens suitable as a baseline.
# Consumers can override via `.kb-config/artifacts.yaml` (styling.source: template).
DEFAULT_THEME = {
    'dark': {
        'bg':           '#0b0d13',
        'bg_elevated':  '#10131c',
        'bg_card':      '#151a26',
        'bg_hover':     '#1b2133',
        'border':       '#1e2436',
        'border_strong':'#2a3248',
        'text':         '#eaecf2',
        'text_sec':     '#8a90a8',
        'text_dim':     '#555d76',
        'accent':       '#1496FF',                        # blue accent
        'accent_hover': '#42aaff',
        'accent_bg':    'rgba(20,150,255,0.10)',
        'badge_bg':     'rgba(111,45,168,0.16)',          # purple badge bg
        'badge_fg':     '#a78bfa',                        # purple light
        'shadow':       '0 2px 12px rgba(0,0,0,0.3)',
    },
    'light': {
        'bg':           '#f4f5f8',
        'bg_elevated':  '#ffffff',
        'bg_card':      '#ffffff',
        'bg_hover':     '#f0f1f6',
        'border':       '#d8dce6',
        'border_strong':'#c0c6d4',
        'text':         '#141824',
        'text_sec':     '#4d5570',
        'text_dim':     '#8a90a8',
        'accent':       '#1284EA',                        # blue accent (deep)
        'accent_hover': '#1496FF',
        'accent_bg':    'rgba(20,150,255,0.08)',
        'badge_bg':     'rgba(111,45,168,0.10)',
        'badge_fg':     '#591F91',                        # purple deep
        'shadow':       '0 2px 12px rgba(0,0,0,0.06)',
    },
}


def load_theme(repo_root: Path) -> dict:
    """Load theme tokens from .kb-config/artifacts.yaml or return defaults."""
    config_path = repo_root / '.kb-config' / 'artifacts.yaml'
    if not config_path.exists() or yaml is None:
        return DEFAULT_THEME

    try:
        with open(config_path) as f:
            cfg = yaml.safe_load(f) or {}
    except Exception:
        return DEFAULT_THEME

    styling = cfg.get('styling', {})
    source = styling.get('source', 'builtin')

    if source == 'template':
        # Try to extract CSS variables from the reference template file
        ref_file = styling.get('reference-file', '')
        if ref_file:
            ref_path = repo_root / ref_file
            if ref_path.exists():
                return extract_theme_from_template(ref_path) or DEFAULT_THEME

    # For 'builtin' or 'website' (website would need runtime fetch — use builtin)
    return DEFAULT_THEME


def load_index_config(repo_root: Path) -> dict:
    """Load index config from .kb-config/artifacts.yaml `index:` section."""
    cfg = dict(DEFAULT_INDEX_CONFIG)
    config_path = repo_root / '.kb-config' / 'artifacts.yaml'
    if not config_path.exists() or yaml is None:
        return cfg
    try:
        with open(config_path) as f:
            raw = yaml.safe_load(f) or {}
    except Exception:
        return cfg
    idx = raw.get('index', {}) or {}
    if 'stale-after-days' in idx:
        cfg['stale_after_days'] = int(idx['stale-after-days'])
    if 'pinned-categories' in idx:
        cfg['pinned_categories'] = list(idx['pinned-categories'] or [])
    if 'dedup-versioned' in idx:
        cfg['dedup_versioned'] = bool(idx['dedup-versioned'])
    if 'drop-referenced-subpages' in idx:
        cfg['drop_referenced_subpages'] = bool(idx['drop-referenced-subpages'])
    if 'category-order' in idx:
        cfg['category_order'] = str(idx['category-order'])
    return cfg


def extract_theme_from_template(template_path: Path) -> dict | None:
    """Extract CSS variable values from a template's :root and [data-theme] blocks."""
    try:
        text = template_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return None

    # Map CSS variable names to our token names
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

    # Find dark theme block (in :root or [data-theme="dark"])
    dark_tokens = dict(DEFAULT_THEME['dark'])
    light_tokens = dict(DEFAULT_THEME['light'])

    # Simple approach: extract all var declarations
    for m in var_re.finditer(text):
        var_name, var_value = m.group(1), m.group(2).strip()
        token = var_map.get(var_name)
        if token and 'var(' not in var_value:  # skip references
            # Determine if this is in a dark or light context
            # by checking what's before this match
            preceding = text[:m.start()]
            if '[data-theme="light"]' in preceding[max(0, len(preceding)-500):]:
                light_tokens[token] = var_value
            else:
                dark_tokens[token] = var_value

    return {'dark': dark_tokens, 'light': light_tokens}


# ── Discovery ──────────────────────────────────────────────────────────

SKIP_DIRS = {'.git', 'node_modules', '.kb-scripts', '.kb-config', '.kb-log',
             '_kb-references/templates', 'templates'}
# Only skipped when at the repo root (the generated output). Sub-directory
# index.html files are hubs/entry points and MUST be indexed so that
# drop_referenced_subpages can see their outgoing links.
SKIP_FILES_ROOT = {'index.html'}

DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2})')
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)

# Warn about filenames that can trip on static hosts (e.g. GitHub Pages
# sometimes returns 404 for multi-dot paths). Report them instead of
# silently indexing broken links.
_DOTTY_STEM_RE = re.compile(r'\.[^.]')


def should_skip(rel: str) -> bool:
    parts = Path(rel).parts
    for d in SKIP_DIRS:
        d_parts = Path(d).parts
        for i in range(len(parts)):
            if parts[i:i+len(d_parts)] == d_parts:
                return True
    # Skip index.html only when it IS the root output file.
    return len(parts) == 1 and parts[0] in SKIP_FILES_ROOT


def extract_title(filepath: Path) -> str | None:
    try:
        text = filepath.read_text(encoding='utf-8', errors='ignore')[:4096]
        m = TITLE_RE.search(text)
        if m:
            t = m.group(1).strip()
            # Strip common suffixes
            for sep in (' — ', ' | ', ' - '):
                if sep in t:
                    t = t.split(sep)[0].strip()
            return t
    except Exception:
        pass
    return None


_META_DESC_RE = re.compile(
    r'''<meta\s+[^>]*name\s*=\s*["'](?:description|og:description)["']'''
    r'''[^>]*content\s*=\s*["']([^"']+)["']''',
    re.IGNORECASE,
)
_META_DESC_RE_ALT = re.compile(
    r'''<meta\s+[^>]*content\s*=\s*["']([^"']+)["']'''
    r'''[^>]*name\s*=\s*["'](?:description|og:description)["']''',
    re.IGNORECASE,
)
_HEADING_RE = re.compile(r'<h[1-3][^>]*>(.*?)</h[1-3]>', re.IGNORECASE | re.DOTALL)
_PARA_RE = re.compile(r'<p[^>]*>(.*?)</p>', re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r'<[^>]+>')
_WS_RE = re.compile(r'\s+')


def _clean_text(s: str) -> str:
    s = _TAG_RE.sub(' ', s)
    s = html.unescape(s)
    return _WS_RE.sub(' ', s).strip()


def _shorten(s: str, max_chars: int = 110) -> str:
    s = s.strip()
    if len(s) <= max_chars:
        return s
    cut = s[:max_chars].rsplit(' ', 1)[0]
    return cut.rstrip(' ,;:.-') + '…'


def extract_summary(filepath: Path, title: str) -> str:
    """Return a short "what's in this file" blurb.

    Preference order: <meta name="description">, first <h1|h2|h3> that isn't
    the page title, first <p>. Returns empty string if nothing usable is found.
    """
    try:
        text = filepath.read_text(encoding='utf-8', errors='ignore')[:16384]
    except Exception:
        return ''
    # 1. meta description
    for rx in (_META_DESC_RE, _META_DESC_RE_ALT):
        m = rx.search(text)
        if m:
            s = _clean_text(m.group(1))
            if s:
                return _shorten(s)
    # 2. first heading that differs from title
    title_norm = title.strip().lower()
    for m in _HEADING_RE.finditer(text):
        s = _clean_text(m.group(1))
        if s and s.lower() != title_norm:
            return _shorten(s)
    # 3. first paragraph with enough substance
    for m in _PARA_RE.finditer(text):
        s = _clean_text(m.group(1))
        if len(s) >= 15:
            return _shorten(s)
    return ''


def extract_date(filepath: Path, repo_root: Path) -> str:
    """Get date from filename pattern, then git, then mtime."""
    m = DATE_RE.search(filepath.stem)
    if m:
        return m.group(1)
    # Try git creation date
    try:
        out = subprocess.check_output(
            ['git', 'log', '--diff-filter=A', '--follow', '--format=%aI',
             '--', str(filepath.relative_to(repo_root))],
            cwd=repo_root, stderr=subprocess.DEVNULL, text=True
        ).strip()
        if out:
            return out.splitlines()[-1][:10]
    except Exception:
        pass
    # Fallback to mtime
    return datetime.fromtimestamp(filepath.stat().st_mtime).strftime('%Y-%m-%d')


def categorize(rel_path: str) -> tuple[str, str]:
    """Return (category, contributor) from relative path."""
    parts = Path(rel_path).parts
    contributor = ''

    # Team KB pattern: <contributor>/<rest>
    # Detect by checking if first dir looks like a contributor (not _kb-*)
    if len(parts) > 1 and not parts[0].startswith(('_kb-', '.')):
        contributor = parts[0]
        parts = parts[1:]

    rel_lower = '/'.join(parts).lower()

    if 'roadmap' in rel_lower or 'status' in rel_lower:
        return 'Roadmap & Status', contributor
    if 'journey' in rel_lower:
        return 'Journey Maps', contributor
    if 'report' in rel_lower:
        return 'Reports', contributor
    if 'strategy' in rel_lower or 'pitch' in rel_lower or 'vision' in rel_lower:
        return 'Strategy & Vision', contributor
    if 'finding' in rel_lower:
        return 'Findings', contributor
    if 'slide' in rel_lower or 'presentation' in rel_lower:
        return 'Presentations', contributor
    if 'prototype' in rel_lower or 'mock' in rel_lower or 'website' in rel_lower:
        return 'Prototypes & Mocks', contributor
    if 'research' in rel_lower:
        return 'Research', contributor
    if 'output' in rel_lower:
        return 'Outputs', contributor
    return 'Other', contributor


# Version/date suffix stripping patterns for dedup.
# Each pattern trims a recognized trailing marker so that e.g.
# "product-vision-v3", "product-vision-v4", "product-vision-v5-pitch" all
# collapse to the same family "product-vision" (variant-aware: "-pitch" is
# kept as a distinguishing variant so pitch and non-pitch stay separate).
_VERSION_SUFFIX_RE = re.compile(
    r'(?:[-_](?:v|V)\d+(?:\.\d+)?|[-_]\d{4}-\d{2}-\d{2}(?:-\d{2}-\d{2})?'
    r'|[-_]draft|[-_]final|[-_]wip)$',
    re.IGNORECASE,
)


def family_key(rel_path: str) -> str:
    """Normalized dedup key: directory + stem with version/date suffixes stripped.

    Variants like `-pitch`, `-exec`, `-presentation` are preserved so that
    different kinds of derivative (pitch vs. exec deck) do NOT collapse.
    Pure version bumps (`-v5` → `-v6`) and date stamps DO collapse.
    """
    p = Path(rel_path)
    stem = p.stem
    # Strip repeatedly to handle e.g. "foo-v5-2026-04-15"
    prev = None
    while prev != stem:
        prev = stem
        stem = _VERSION_SUFFIX_RE.sub('', stem)
    # Lowercase for robustness; keep directory to scope dedup to contributor/folder
    return f'{p.parent.as_posix().lower()}::{stem.lower()}'


def discover_artifacts(repo_root: Path) -> list[Artifact]:
    artifacts = []
    for fp in sorted(repo_root.rglob('*.html')):
        rel = str(fp.relative_to(repo_root))
        if should_skip(rel):
            continue
        title = extract_title(fp) or fp.stem.replace('-', ' ').replace('_', ' ').title()
        date = extract_date(fp, repo_root)
        cat, contrib = categorize(rel)
        summary = extract_summary(fp, title)
        artifacts.append(Artifact(path=rel, title=title, date=date,
                                  category=cat, contributor=contrib,
                                  family=family_key(rel), summary=summary))
    # Sort newest first
    artifacts.sort(key=lambda a: a.date, reverse=True)
    return artifacts


# ── Markdown source discovery (issue #21) ──────────────────────────────
#
# Scans the canonical human-authored directories so the public landing
# page actually surfaces the KB's knowledge, not just its HTML artifacts.
# Markdown sources bypass dedup_families / drop_referenced_subpages —
# they are leaf content, not versioned or hub-child HTML.

_MD_H1_RE = re.compile(r'^\s*#\s+(.+?)\s*$', re.MULTILINE)
# Strips the canonical object-kind prefix (`Finding:`/`Topic:`/`Idea:`) or the
# decision-id prefix (`D-YYYY-MM-DD-slug:`) from the raw heading text.
_MD_TITLE_STRIP_RE = re.compile(
    r'^(?:(?:Finding|Topic|Idea)\s*:\s*|(?:[DI]-\d{4}-\d{2}-\d{2}-[\w-]+)\s*:\s*)',
    re.IGNORECASE,
)
_MD_DATE_FIELD_RE = re.compile(
    r'^\*\*(?:Date|Created)\*\*\s*:\s*(\d{4}-\d{2}-\d{2})', re.MULTILINE
)

# (dir, category, optional-exclude-subdir)
_MD_SOURCES: list[tuple[str, str, str | None]] = [
    ('_kb-references/findings', 'Findings', None),
    ('_kb-references/topics', 'Topics', None),
    ('_kb-ideas', 'Ideas', 'archive'),
    ('_kb-decisions', 'Decisions', 'archive'),
]


def _extract_md_title(text: str, fallback: str) -> str:
    m = _MD_H1_RE.search(text)
    if m:
        raw = m.group(1).strip()
        stripped = _MD_TITLE_STRIP_RE.sub('', raw).strip()
        return stripped or raw
    return fallback.replace('-', ' ').replace('_', ' ').title()


def _extract_md_date(text: str, filename: str) -> str:
    m = DATE_RE.search(filename)
    if m:
        return m.group(1)
    m = _MD_DATE_FIELD_RE.search(text)
    if m:
        return m.group(1)
    return ''


def discover_markdown_sources(repo_root: Path) -> list[Artifact]:
    items: list[Artifact] = []
    for rel_dir, category, exclude_sub in _MD_SOURCES:
        src_dir = repo_root / rel_dir
        if not src_dir.is_dir():
            continue
        for fp in sorted(src_dir.glob('*.md')):
            if exclude_sub and exclude_sub in fp.parts:
                continue
            try:
                text = fp.read_text(encoding='utf-8', errors='ignore')[:4096]
            except Exception:
                continue
            title = _extract_md_title(text, fp.stem)
            date = _extract_md_date(text, fp.name)
            rel = str(fp.relative_to(repo_root))
            items.append(Artifact(path=rel, title=title, date=date,
                                  category=category, contributor='',
                                  family=f'md::{rel}', summary=''))
    items.sort(key=lambda a: (a.date or '0000-00-00'), reverse=True)
    return items


def dedup_families(artifacts: list[Artifact]) -> list[Artifact]:
    """Keep only the newest artifact per (category, family) group."""
    seen: dict[tuple[str, str], Artifact] = {}
    for a in artifacts:  # artifacts already newest-first
        key = (a.category, a.family)
        if key not in seen:
            seen[key] = a
    return sorted(seen.values(), key=lambda a: a.date, reverse=True)


# Matches href="..." / src="..." (single or double quoted).
_HREF_RE = re.compile(r'''(?:href|src)\s*=\s*["']([^"'#?]+?\.html)(?:[?#][^"']*)?["']''',
                      re.IGNORECASE)


def _referenced_paths_from(fp: Path, repo_root: Path) -> set[str]:
    """Return the set of repo-relative artifact paths referenced from this HTML.

    Only same-repo relative `.html` links count; absolute URLs (http(s)://,
    //, mailto:, fragments) are ignored. Paths are resolved relative to the
    referring file's directory and normalized against the repo root.
    """
    try:
        text = fp.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return set()
    refs: set[str] = set()
    base = fp.parent
    for m in _HREF_RE.finditer(text):
        url = m.group(1).strip()
        if not url or url.startswith(('http://', 'https://', '//', 'mailto:',
                                       'tel:', 'data:', 'javascript:')):
            continue
        try:
            target = (base / url).resolve()
            rel = target.relative_to(repo_root)
        except (ValueError, OSError):
            continue
        refs.add(rel.as_posix())
    return refs


def drop_referenced_subpages(artifacts: list[Artifact],
                              repo_root: Path) -> tuple[list[Artifact], int]:
    """Drop artifacts linked to from a hub artifact in the index.

    Intent: when a hub HTML (e.g. a journey index) already links to its
    sub-pages, the sub-pages should not be listed separately in the root
    index. The hub stays; referenced leaves are removed — even when leaves
    share a navigation bar that cross-links every sibling.

     Standalone mock trees are also treated as subordinate navigation when a
     parent overview exists. For example, `_kb-journeys/html/index.html`
     should surface on the root index, while `_kb-journeys/html/mocks/` stays
     reachable only from the journey set itself.

    Algorithm:
      1. Build each artifact's set of outgoing refs that land on another
         indexed artifact (excluding self).
      2. Collapse cliques — groups whose members all share the same
         outward scope (`refs ∪ {self}`). These are typically pages in
         the same nav bar. Keep one representative per clique, preferring
         a file literally named ``index.html``, else the shortest path.
        3. Drop any artifact under a `mocks/` subtree when the parent
            directory already has an `index.html` overview in the index.
        4. Among surviving artifacts, drop any leaf referenced by a hub
         (≥ 2 outgoing refs) unless the leaf is itself a hub reaching
         pages OUTSIDE the referring hub's scope.
    """
    paths = {a.path for a in artifacts}

    # Treat standalone mock trees as subordinate navigation before clique
    # detection so journey overview pages and their sibling journey pages can
    # still collapse to a single canonical entry point.
    mock_drops: set[str] = set()
    for p in paths:
        rel = Path(p)
        if 'mocks' not in rel.parts:
            continue
        mock_index = rel.parts.index('mocks')
        if mock_index == 0:
            continue
        parent_overview = Path(*rel.parts[:mock_index], 'index.html').as_posix()
        if parent_overview in paths:
            mock_drops.add(p)

    out_refs: dict[str, set[str]] = {}
    for a in artifacts:
        fp = repo_root / a.path
        refs = (_referenced_paths_from(fp, repo_root) & paths) - mock_drops
        refs.discard(a.path)
        out_refs[a.path] = refs

    # ── 1. Collapse cliques ──────────────────────────────────────────
    by_sig: dict[frozenset, list[str]] = {}
    for p, refs in out_refs.items():
        sig = frozenset(refs | {p})
        by_sig.setdefault(sig, []).append(p)

    def _rep_key(p: str) -> tuple[int, int, str]:
        name = p.rsplit('/', 1)[-1]
        return (0 if name == 'index.html' else 1, len(p), p)

    clique_drops: set[str] = set()
    for members in by_sig.values():
        if len(members) < 2:
            continue
        keeper = min(members, key=_rep_key)
        for m in members:
            if m != keeper:
                clique_drops.add(m)

    remaining_paths = paths - clique_drops

    remaining_paths -= mock_drops

    # ── 2. Drop leaves referenced by surviving hubs ──────────────────
    HUB_MIN_REFS = 2
    surv_refs = {p: out_refs[p] & remaining_paths for p in remaining_paths}
    hubs = {p for p, r in surv_refs.items() if len(r) >= HUB_MIN_REFS}

    leaf_drops: set[str] = set()
    for hub in hubs:
        hub_scope = surv_refs[hub] | {hub}
        for ref in surv_refs[hub]:
            if ref in hubs and (surv_refs[ref] - hub_scope):
                continue
            leaf_drops.add(ref)

    to_drop = clique_drops | mock_drops | leaf_drops
    kept = [a for a in artifacts if a.path not in to_drop]
    return kept, len(artifacts) - len(kept)


# ── HTML Generation ────────────────────────────────────────────────────

def generate_html(artifacts: list[Artifact], title: str, description: str,
                  now: str, theme: dict, index_cfg: dict,
                  has_dashboard: bool = False) -> str:
    dark = theme['dark']
    light = theme['light']

    dashboard_nav = (
        '  <nav class="top-nav">\n'
        '    <a href="dashboard.html" class="nav-dashboard">'
        '&rarr; Dashboard &mdash; focus, ideas, decisions, tasks</a>\n'
        '  </nav>'
        if has_dashboard else ''
    )

    # ── Staleness ────────────────────────────────────────────────────
    stale_days = int(index_cfg.get('stale_after_days', 14))
    today = datetime.now().date()
    stale_cutoff = today - timedelta(days=stale_days)
    stale_cutoff_str = stale_cutoff.strftime('%Y-%m-%d')

    def is_stale(date_str: str) -> bool:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date() < stale_cutoff
        except ValueError:
            return False

    # ── Group + order categories ─────────────────────────────────────
    by_cat: dict[str, list[Artifact]] = {}
    for a in artifacts:
        by_cat.setdefault(a.category, []).append(a)

    pinned = [c for c in index_cfg.get('pinned_categories', []) if c in by_cat]
    remaining = [c for c in by_cat if c not in pinned]

    if index_cfg.get('category_order', 'recency') == 'recency':
        # Sort remaining by newest artifact date desc
        remaining.sort(
            key=lambda c: max(a.date for a in by_cat[c]),
            reverse=True,
        )
    else:
        # Fixed fallback order
        fixed = ['Reports', 'Strategy & Vision', 'Presentations', 'Journey Maps',
                 'Findings', 'Research', 'Prototypes & Mocks', 'Outputs',
                 'Roadmap & Status', 'Other']
        remaining.sort(key=lambda c: fixed.index(c) if c in fixed else 999)

    cat_order = pinned + remaining

    # ── Build sections ───────────────────────────────────────────────
    sections = []
    for cat in cat_order:
        items = by_cat.get(cat)
        if not items:
            continue
        rows = []
        for a in items:
            esc_title = html.escape(a.title)
            esc_path = html.escape(a.path)
            esc_summary = (html.escape(a.summary) if a.summary
                           else '<span class="muted">—</span>')
            badges = []
            if is_stale(a.date):
                badges.append('<span class="badge-stale">stale</span>')
            if a.contributor:
                badges.append(f'<span class="badge">{html.escape(a.contributor)}</span>')
            badges_html = ''.join(badges)
            rows.append(
                '        <tr>'
                f'<td class="col-title"><a href="{esc_path}">{esc_title}</a></td>'
                f'<td class="col-summary">{esc_summary}</td>'
                f'<td class="col-meta">{badges_html}<span class="date">{a.date}</span></td>'
                '</tr>'
            )
        sections.append(
            f'    <h2>{html.escape(cat)}'
            f' <span class="count">{len(items)}</span></h2>\n'
            '    <table class="artifact-table">\n'
            '      <thead><tr>'
            '<th class="col-title">Artifact</th>'
            '<th class="col-summary">Summary</th>'
            '<th class="col-meta">Meta</th>'
            '</tr></thead>\n'
            '      <tbody>\n'
            + '\n'.join(rows) + '\n'
            '      </tbody>\n'
            '    </table>'
        )

    body_sections = '\n\n'.join(sections) if sections else (
        '    <p class="empty">No HTML artifacts found yet. '
        'Generate one with <code>/kb present</code>, <code>/kb report</code>, '
        'or <code>/kb end-day</code>.</p>'
    )

    pinned_label = ', '.join(pinned) if pinned else 'none'
    legend_html = (
        '  <p class="legend">'
        f'<strong>Ordering:</strong> Pinned categories first ({html.escape(pinned_label)}); '
        'others ordered by newest artifact. '
        '<strong>Dedup:</strong> only the latest version of each artifact family is shown '
        '(older versions remain on disk). '
        f'<strong><span class="badge-stale">stale</span></strong> marks content older than '
        f'{stale_days} days (before <code>{stale_cutoff_str}</code>) — may be outdated.'
        '</p>'
    )

    return f'''<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Artifact Index</title>
<meta name="generator" content="agentic-kb/generate-index">
<meta name="generated" content="{now}">
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root, [data-theme="dark"] {{
  --bg:           {dark['bg']};
  --bg-elevated:  {dark['bg_elevated']};
  --bg-card:      {dark['bg_card']};
  --bg-hover:     {dark['bg_hover']};
  --border:       {dark['border']};
  --border-strong:{dark['border_strong']};
  --text:         {dark['text']};
  --text-sec:     {dark['text_sec']};
  --text-dim:     {dark['text_dim']};
  --accent:       {dark['accent']};
  --accent-hover: {dark['accent_hover']};
  --accent-bg:    {dark['accent_bg']};
  --badge-bg:     {dark['badge_bg']};
  --badge-fg:     {dark['badge_fg']};
  --shadow:       {dark['shadow']};
}}

[data-theme="light"] {{
  --bg:           {light['bg']};
  --bg-elevated:  {light['bg_elevated']};
  --bg-card:      {light['bg_card']};
  --bg-hover:     {light['bg_hover']};
  --border:       {light['border']};
  --border-strong:{light['border_strong']};
  --text:         {light['text']};
  --text-sec:     {light['text_sec']};
  --text-dim:     {light['text_dim']};
  --accent:       {light['accent']};
  --accent-hover: {light['accent_hover']};
  --accent-bg:    {light['accent_bg']};
  --badge-bg:     {light['badge_bg']};
  --badge-fg:     {light['badge_fg']};
  --shadow:       {light['shadow']};
}}

html, body {{
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
               'Segoe UI', sans-serif;
  background: var(--bg); color: var(--text);
  line-height: 1.6; -webkit-font-smoothing: antialiased;
}}

main {{
  max-width: 860px; margin: 0 auto;
  padding: 2.5rem 1.5rem 5rem;
}}

/* Header */
.header {{
  display: flex; align-items: center; gap: 1rem;
  margin-bottom: 0.5rem;
}}
.header svg {{ flex-shrink: 0; }}
h1 {{
  font-size: 1.75rem; font-weight: 700;
  letter-spacing: -0.02em; line-height: 1.2;
}}
.lead {{
  font-size: 1.05rem; color: var(--text-sec);
  margin: 0.25rem 0 0.5rem;
}}
.watermark {{
  font-size: 0.75rem; color: var(--text-dim);
  letter-spacing: 0.06em; font-variant: all-small-caps;
  margin-bottom: 2rem;
}}

/* Theme toggle */
.theme-toggle {{
  position: fixed; top: 1rem; right: 1rem;
  width: 36px; height: 36px; border-radius: 8px;
  border: 1px solid var(--border-strong);
  background: var(--bg-elevated); color: var(--text);
  cursor: pointer; font-size: 1rem; display: grid; place-items: center;
  box-shadow: var(--shadow); transition: border-color 0.15s;
}}
.theme-toggle:hover {{ border-color: var(--accent); }}

/* Sections */
h2 {{
  font-size: 1.15rem; font-weight: 600;
  margin: 2rem 0 0.6rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 0.5rem;
}}
.count {{
  font-size: 0.7rem; font-weight: 500;
  background: var(--accent-bg); color: var(--accent);
  padding: 0.15rem 0.5rem; border-radius: 10px;
}}

/* Artifact list */
.artifact-list {{
  list-style: none; padding: 0; margin: 0;
}}
.artifact-list li {{
  padding: 0.6rem 0.8rem;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: baseline;
  justify-content: space-between; gap: 1rem;
  transition: background 0.1s;
  border-radius: 6px;
}}
.artifact-list li:hover {{
  background: var(--bg-hover);
}}
.artifact-list li:last-child {{ border-bottom: none; }}
.artifact-list a {{
  color: var(--accent); text-decoration: none;
  font-weight: 500; font-size: 0.92rem;
}}
.artifact-list a:hover {{ text-decoration: underline; }}

/* Artifact table */
.artifact-table {{
  width: 100%; border-collapse: collapse;
  font-size: 0.9rem;
}}
.artifact-table th {{
  text-align: left; font-weight: 600;
  font-size: 0.72rem; letter-spacing: 0.06em;
  text-transform: uppercase; color: var(--text-dim);
  padding: 0.4rem 0.8rem 0.5rem;
  border-bottom: 1px solid var(--border-strong);
}}
.artifact-table td {{
  padding: 0.55rem 0.8rem;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}}
.artifact-table tr:last-child td {{ border-bottom: none; }}
.artifact-table tr:hover td {{ background: var(--bg-hover); }}
.artifact-table a {{
  color: var(--accent); text-decoration: none;
  font-weight: 500;
}}
.artifact-table a:hover {{ text-decoration: underline; }}
.col-title {{ width: 34%; }}
.col-summary {{
  width: 50%; color: var(--text-sec);
  font-size: 0.85rem; line-height: 1.45;
}}
.col-summary .muted {{ color: var(--text-dim); }}
.col-meta {{
  width: 16%; white-space: nowrap;
  font-size: 0.78rem; color: var(--text-dim);
  text-align: right;
}}
.col-meta .date {{ margin-left: 0.4rem; }}
@media (max-width: 680px) {{
  .artifact-table, .artifact-table thead, .artifact-table tbody,
  .artifact-table tr, .artifact-table td {{ display: block; width: 100%; }}
  .artifact-table thead {{ display: none; }}
  .artifact-table tr {{
    padding: 0.5rem 0; border-bottom: 1px solid var(--border);
  }}
  .artifact-table td {{ border-bottom: none; padding: 0.15rem 0.2rem; }}
  .col-meta {{ text-align: left; }}
}}
.meta {{
  font-size: 0.78rem; color: var(--text-dim);
  white-space: nowrap; display: flex; align-items: center; gap: 0.4rem;
}}
.badge {{
  font-size: 0.68rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.04em;
  background: var(--badge-bg); color: var(--badge-fg);
  padding: 0.1rem 0.45rem; border-radius: 4px;
}}
.badge-stale {{
  font-size: 0.62rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.04em;
  background: rgba(245,180,0,0.15); color: #d4a000;
  padding: 0.1rem 0.4rem; border-radius: 4px;
  border: 1px solid rgba(245,180,0,0.3);
}}
[data-theme="light"] .badge-stale {{ color: #9a6b00; }}
.legend {{
  font-size: 0.78rem; color: var(--text-sec);
  margin: 0.5rem 0 1.5rem; padding: 0.6rem 0.9rem;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; line-height: 1.55;
}}
.legend code {{
  background: var(--bg-hover); padding: 0.05rem 0.3rem;
  border-radius: 3px; font-size: 0.88em;
}}

.empty {{
  color: var(--text-sec); padding: 2rem 0;
  text-align: center; font-size: 0.95rem;
}}
.empty code {{
  background: var(--bg-card); padding: 0.15rem 0.4rem;
  border-radius: 4px; font-size: 0.85em;
}}

/* Stats bar */
.stats {{
  display: flex; gap: 1.5rem; margin: 1rem 0 1.5rem;
  padding: 0.8rem 1rem; background: var(--bg-card);
  border: 1px solid var(--border); border-radius: 10px;
}}
.stat {{ text-align: center; }}
.stat-value {{
  font-size: 1.5rem; font-weight: 700;
  color: var(--accent); line-height: 1.2;
}}
.stat-label {{
  font-size: 0.7rem; color: var(--text-dim);
  text-transform: uppercase; letter-spacing: 0.06em;
}}
@media (max-width: 600px) {{ .stats {{ flex-wrap: wrap; gap: 1rem; }} }}

/* Top nav (dashboard link) */
.top-nav {{
  display: flex; gap: 0.6rem; margin: 0.75rem 0 1.25rem; flex-wrap: wrap;
}}
.top-nav a {{
  font-size: 0.85rem; color: var(--accent); text-decoration: none;
  padding: 0.4rem 0.85rem; border: 1px solid var(--border);
  background: var(--bg-card); border-radius: 999px;
  font-weight: 500;
}}
.top-nav a:hover {{ border-color: var(--accent); background: var(--accent-bg); }}
.top-nav a.nav-dashboard {{
  border-color: var(--accent); background: var(--accent-bg);
}}
</style>
</head>
<body>
<button class="theme-toggle" type="button" aria-label="Toggle theme"
  onclick="var h=document.documentElement,t=h.getAttribute('data-theme');h.setAttribute('data-theme',t==='dark'?'light':'dark');this.textContent=t==='dark'?'\u2600':'\u263E'">\u263E</button>
<main>
  <div class="header">
    <svg width="28" height="28" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M50 5L90 27.5V72.5L50 95L10 72.5V27.5L50 5Z" fill="var(--accent)" opacity="0.15"/>
      <path d="M50 15L80 32.5V67.5L50 85L20 67.5V32.5L50 15Z" stroke="var(--accent)" stroke-width="2" fill="none"/>
      <circle cx="50" cy="50" r="8" fill="var(--accent)"/>
    </svg>
    <div>
      <h1>{html.escape(title)}</h1>
      <p class="lead">{html.escape(description)}</p>
    </div>
  </div>
  <p class="watermark">latest &middot; {now} &middot; {len(artifacts)} artifact{"s" if len(artifacts) != 1 else ""}</p>

{dashboard_nav}

  <div class="stats">
    <div class="stat"><div class="stat-value">{len(artifacts)}</div><div class="stat-label">Total</div></div>
    <div class="stat"><div class="stat-value">{len(set(a.category for a in artifacts))}</div><div class="stat-label">Categories</div></div>
    <div class="stat"><div class="stat-value">{len(set(a.contributor for a in artifacts if a.contributor))}</div><div class="stat-label">Contributors</div></div>
    <div class="stat"><div class="stat-value">{artifacts[0].date if artifacts else "—"}</div><div class="stat-label">Latest</div></div>
  </div>

{legend_html}

{body_sections}

</main>
</body>
</html>'''


# ── Main ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description='Generate artifact index.html')
    parser.add_argument('root', nargs='?', default='.', help='Repository root')
    parser.add_argument('--title', default=None, help='KB title')
    parser.add_argument('--description', default='', help='One-line description')
    parser.add_argument('--output', default='index.html', help='Output filename')
    args = parser.parse_args()

    repo_root = Path(args.root).resolve()
    if not repo_root.is_dir():
        sys.exit(f'Not a directory: {repo_root}')

    # Auto-detect title from directory name if not provided
    title = args.title or repo_root.name

    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    artifacts = discover_artifacts(repo_root)
    theme = load_theme(repo_root)
    index_cfg = load_index_config(repo_root)
    total_before = len(artifacts)
    if index_cfg.get('dedup_versioned', True):
        artifacts = dedup_families(artifacts)
    dedup_dropped = total_before - len(artifacts)
    subpage_dropped = 0
    if index_cfg.get('drop_referenced_subpages', True):
        artifacts, subpage_dropped = drop_referenced_subpages(artifacts, repo_root)
    # Append markdown sources (findings / topics / ideas / decisions) AFTER
    # dedup + subpage-drop — they are leaf content, not versioned HTML, and
    # must not interact with those filters.
    md_sources = discover_markdown_sources(repo_root)
    artifacts = artifacts + md_sources
    has_dashboard = (repo_root / 'dashboard.html').exists()
    out = generate_html(artifacts, title, args.description, now, theme, index_cfg,
                        has_dashboard=has_dashboard)

    outpath = repo_root / args.output
    outpath.write_text(out, encoding='utf-8')

    # Warn about dotted stems — some static hosts (e.g. GitHub Pages)
    # return 404 for multi-dot paths like "1.1-onboarding.html".
    dotty = [a.path for a in artifacts if _DOTTY_STEM_RE.search(Path(a.path).stem)]
    if dotty:
        print('Warning: filenames contain "." in stem — may 404 on some static '
              'hosts (e.g. GitHub Pages). Prefer hyphens:', file=sys.stderr)
        for p in dotty[:10]:
            print(f'  {p}', file=sys.stderr)
        if len(dotty) > 10:
            print(f'  ... and {len(dotty) - 10} more', file=sys.stderr)

    parts = []
    if dedup_dropped:
        parts.append(f'{dedup_dropped} older versions deduped')
    if subpage_dropped:
        parts.append(f'{subpage_dropped} referenced sub-pages hidden')
    suffix = f' ({"; ".join(parts)})' if parts else ''
    print(f'Generated {outpath} — {len(artifacts)} artifacts indexed{suffix}')


if __name__ == '__main__':
    main()
