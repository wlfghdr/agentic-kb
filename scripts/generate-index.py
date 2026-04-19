#!/usr/bin/env python3
"""Generate a root index.html for an agentic-kb layer.

Scans the repository for HTML artifacts (reports, presentations, specs,
journey maps, mocks, etc.) and produces a self-contained index.html with
Dynatrace/Strato design tokens, dark/light toggle, and GitHub-Pages-ready
relative links.

Usage:
    python generate-index.py [REPO_ROOT] [--title TITLE] [--description DESC]

If REPO_ROOT is omitted, uses the current directory.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import NamedTuple


class Artifact(NamedTuple):
    path: str          # relative to repo root
    title: str         # extracted from <title> or filename
    date: str          # YYYY-MM-DD
    category: str      # grouping label
    contributor: str   # for team KBs, empty for personal


# ── Discovery ──────────────────────────────────────────────────────────

SKIP_DIRS = {'.git', 'node_modules', '.kb-scripts', '.kb-config', '.kb-log',
             '_kb-references/templates', 'templates'}
SKIP_FILES = {'index.html'}

DATE_RE = re.compile(r'(\d{4}-\d{2}-\d{2})')
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.IGNORECASE | re.DOTALL)


def should_skip(rel: str) -> bool:
    parts = Path(rel).parts
    for d in SKIP_DIRS:
        d_parts = Path(d).parts
        for i in range(len(parts)):
            if parts[i:i+len(d_parts)] == d_parts:
                return True
    return Path(rel).name in SKIP_FILES


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

    if 'report' in rel_lower:
        return 'Reports', contributor
    if 'strategy' in rel_lower or 'pitch' in rel_lower or 'vision' in rel_lower:
        return 'Strategy & Vision', contributor
    if 'journey' in rel_lower:
        return 'Journey Maps', contributor
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


def discover_artifacts(repo_root: Path) -> list[Artifact]:
    artifacts = []
    for fp in sorted(repo_root.rglob('*.html')):
        rel = str(fp.relative_to(repo_root))
        if should_skip(rel):
            continue
        title = extract_title(fp) or fp.stem.replace('-', ' ').replace('_', ' ').title()
        date = extract_date(fp, repo_root)
        cat, contrib = categorize(rel)
        artifacts.append(Artifact(path=rel, title=title, date=date,
                                  category=cat, contributor=contrib))
    # Sort newest first
    artifacts.sort(key=lambda a: a.date, reverse=True)
    return artifacts


# ── HTML Generation ────────────────────────────────────────────────────

def generate_html(artifacts: list[Artifact], title: str, description: str,
                  now: str) -> str:
    # Group by category
    by_cat: dict[str, list[Artifact]] = {}
    for a in artifacts:
        by_cat.setdefault(a.category, []).append(a)

    # Category order
    cat_order = ['Reports', 'Strategy & Vision', 'Presentations', 'Journey Maps',
                 'Findings', 'Research', 'Prototypes & Mocks', 'Outputs', 'Other']

    sections = []
    for cat in cat_order:
        items = by_cat.get(cat)
        if not items:
            continue
        rows = []
        for a in items:
            esc_title = html.escape(a.title)
            esc_path = html.escape(a.path)
            contrib_badge = ''
            if a.contributor:
                esc_c = html.escape(a.contributor)
                contrib_badge = f'<span class="badge">{esc_c}</span> '
            rows.append(
                f'        <li>'
                f'<a href="{esc_path}">{esc_title}</a>'
                f' <span class="meta">{contrib_badge}{a.date}</span>'
                f'</li>'
            )
        sections.append(
            f'    <h2>{html.escape(cat)}'
            f' <span class="count">{len(items)}</span></h2>\n'
            f'    <ul class="artifact-list">\n'
            + '\n'.join(rows) + '\n'
            f'    </ul>'
        )

    body_sections = '\n\n'.join(sections) if sections else (
        '    <p class="empty">No HTML artifacts found yet. '
        'Generate one with <code>/kb present</code>, <code>/kb report</code>, '
        'or <code>/kb end-day</code>.</p>'
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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root, [data-theme="dark"] {{
  --bg:           #0b0d13;
  --bg-elevated:  #10131c;
  --bg-card:      #151a26;
  --bg-hover:     #1b2133;
  --border:       #1e2436;
  --border-strong:#2a3248;
  --text:         #eaecf2;
  --text-sec:     #8a90a8;
  --text-dim:     #555d76;
  --accent:       #1496FF;
  --accent-hover: #42aaff;
  --accent-bg:    rgba(20,150,255,0.08);
  --green:        #B4DC00;
  --purple:       #6F2DA8;
  --purple-bg:    rgba(111,45,168,0.10);
  --shadow:       0 2px 12px rgba(0,0,0,0.3);
  --logo-fill:    #FFFFFF;
}}

[data-theme="light"] {{
  --bg:           #f4f5f8;
  --bg-elevated:  #ffffff;
  --bg-card:      #ffffff;
  --bg-hover:     #f0f1f6;
  --border:       #d8dce6;
  --border-strong:#c0c6d4;
  --text:         #141824;
  --text-sec:     #4d5570;
  --text-dim:     #7d849c;
  --accent:       #1474cc;
  --accent-hover: #0f62b4;
  --accent-bg:    rgba(20,116,204,0.06);
  --green:        #73BE28;
  --purple:       #6F2DA8;
  --purple-bg:    rgba(111,45,168,0.05);
  --shadow:       0 2px 12px rgba(0,0,0,0.04);
  --logo-fill:    #1A1A1A;
}}

html, body {{
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
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
.meta {{
  font-size: 0.78rem; color: var(--text-dim);
  white-space: nowrap; display: flex; align-items: center; gap: 0.4rem;
}}
.badge {{
  font-size: 0.68rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.04em;
  background: var(--purple-bg); color: var(--purple);
  padding: 0.1rem 0.45rem; border-radius: 4px;
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
</style>
</head>
<body>
<button class="theme-toggle" type="button" aria-label="Toggle theme"
  onclick="var h=document.documentElement,t=h.getAttribute('data-theme');h.setAttribute('data-theme',t==='dark'?'light':'dark');this.textContent=t==='dark'?'\\u2600':'\\u263E'">\\u263E</button>
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

  <div class="stats">
    <div class="stat"><div class="stat-value">{len(artifacts)}</div><div class="stat-label">Total</div></div>
    <div class="stat"><div class="stat-value">{len(set(a.category for a in artifacts))}</div><div class="stat-label">Categories</div></div>
    <div class="stat"><div class="stat-value">{len(set(a.contributor for a in artifacts if a.contributor))}</div><div class="stat-label">Contributors</div></div>
    <div class="stat"><div class="stat-value">{artifacts[0].date if artifacts else "—"}</div><div class="stat-label">Latest</div></div>
  </div>

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
    out = generate_html(artifacts, title, args.description, now)

    outpath = repo_root / args.output
    outpath.write_text(out, encoding='utf-8')
    print(f'Generated {outpath} — {len(artifacts)} artifacts indexed')


if __name__ == '__main__':
    main()
