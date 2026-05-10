#!/usr/bin/env python3
"""kb-journeys render: markdown journey files -> HTML set + mocks.

Reads journey markdown, emits per-journey HTML plus shared.css and an overview
index, then delegates to extract_mocks.py for standalone mock pages.

The renderer prefers `python-markdown` when installed, but it does not require
it. The built-in fallback keeps raw HTML/mock envelopes intact so extraction and
back-links still work in minimal environments.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


STEP_HEADING_RE = re.compile(
    r"^###\s+Step\s+(?P<num>\d+):\s+(?P<title>.+?)\s+·\s+`(?P<id>J[\d.]+-S\d+)`\s+·\s+`\[(?P<actor>[^\]]+)\]`",
    re.MULTILINE,
)
META_LINE_RE = re.compile(r"^\s*>\s+\*\*(?P<key>[^:]+)\*\*:\s*(?P<value>.+?)\s*$", re.MULTILINE)
TITLE_RE = re.compile(r"^#\s+(?P<tp>\d+(?:\.\d+)*)\s+—\s+(?P<title>.+?)\s*$", re.MULTILINE)
READINESS_RE = re.compile(
    r'<span class="status-chip (?P<key>[a-z0-9-]+)">(?P<label>[^<]+)</span>\s*[—-]\s*(?P<reason>.+)'
)


@dataclass
class JourneyDoc:
    source_path: Path
    output_slug: str
    journey_id: str
    title: str
    tier: str
    phase: str
    subtitle: str
    tier_label: str
    target_duration: str
    last_updated: str
    steps: list[dict]
    flow_md: str
    interfaces_md: str
    readiness_class: str
    readiness_label: str
    readiness_rationale: str


def render_template(template: str, **vars: object) -> str:
    out = template

    def replace_if(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        body = match.group(2)
        return body if vars.get(key) else ""

    out = re.sub(r"\{\{#if\s+(\w+)\}\}([\s\S]*?)\{\{/if\}\}", replace_if, out)

    def replace_each(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        body = match.group(2)
        items = vars.get(key) or []
        rendered: list[str] = []
        for item in items if isinstance(items, list) else []:
            piece = body
            if isinstance(item, dict):
                for item_key, item_value in item.items():
                    piece = piece.replace("{{" + item_key + "}}", str(item_value))
            rendered.append(piece)
        return "".join(rendered)

    out = re.sub(r"\{\{#each\s+(\w+)\}\}([\s\S]*?)\{\{/each\}\}", replace_each, out)

    for key, value in vars.items():
        if isinstance(value, (list, dict)):
            continue
        out = out.replace("{{{" + key + "}}}", str(value))
        out = out.replace("{{" + key + "}}", str(value))

    out = re.sub(r"\{\{[^{}#/]+\}\}", "", out)
    return out


def parse_metadata(md: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for match in META_LINE_RE.finditer(md[:2000]):
        meta[match.group("key").strip().lower()] = match.group("value").strip()
    return meta


def parse_title(md: str, fallback_name: str) -> tuple[str, str, str]:
    match = TITLE_RE.search(md)
    if not match:
        return ("", "", fallback_name)
    tp = match.group("tp")
    title = match.group("title")
    parts = tp.split(".")
    tier = parts[0] if parts else ""
    phase = parts[1] if len(parts) > 1 else ""
    return (tier, phase, title)


def parse_steps(md: str) -> list[dict[str, str]]:
    steps: list[dict[str, str]] = []
    for match in STEP_HEADING_RE.finditer(md):
        steps.append(
            {
                "id": match.group("id"),
                "title": match.group("title"),
                "actor": match.group("actor"),
            }
        )
    return steps


def split_flow(md: str) -> tuple[str, str]:
    parts = re.split(r"^##\s+Flow\s*$", md, maxsplit=1, flags=re.MULTILINE)
    after_flow = parts[1] if len(parts) == 2 else ""
    interfaces_md = ""
    match = re.search(r"^##\s+Interfaces\s*$([\s\S]*?)(?=^##\s+|\Z)", md, re.MULTILINE)
    if match:
        interfaces_md = match.group(1).strip()
    return after_flow.strip(), interfaces_md


def merge_shared_css(base_path: Path, tokens_path: Path | None) -> str:
    base = base_path.read_text(encoding="utf-8")
    if not tokens_path or not tokens_path.exists():
        return base
    adopter = tokens_path.read_text(encoding="utf-8")
    root_block = re.search(r":root\s*\{[^}]*\}", adopter, re.DOTALL)
    light_block = re.search(r'\[data-theme="light"\]\s*\{[^}]*\}', adopter, re.DOTALL)
    dark_auto_block = re.search(
        r"@media\s*\(prefers-color-scheme:\s*light\)\s*\{\s*\[data-theme=\"auto\"\]\s*\{[^}]*\}\s*\}",
        adopter,
        re.DOTALL,
    )
    if root_block:
        base = re.sub(r":root\s*\{[^}]*\}", root_block.group(0), base, count=1, flags=re.DOTALL)
    if light_block:
        base = re.sub(
            r'\[data-theme="light"\]\s*\{[^}]*\}',
            light_block.group(0),
            base,
            count=1,
            flags=re.DOTALL,
        )
    if dark_auto_block:
        base = re.sub(
            r"@media\s*\(prefers-color-scheme:\s*light\)\s*\{\s*\[data-theme=\"auto\"\]\s*\{[^}]*\}\s*\}",
            dark_auto_block.group(0),
            base,
            count=1,
            flags=re.DOTALL,
        )
    return base


def _inline_format(text: str) -> str:
    out = html.escape(text)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    return out


def _render_table(lines: list[str]) -> str:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    if len(rows) >= 2 and all(re.fullmatch(r"[-: ]+", cell) for cell in rows[1]):
        rows.pop(1)
    if not rows:
        return ""
    header, body = rows[0], rows[1:]
    head_html = "".join(f"<th>{_inline_format(cell)}</th>" for cell in header)
    body_html = "".join(
        "<tr>" + "".join(f"<td>{_inline_format(cell)}</td>" for cell in row) + "</tr>"
        for row in body
    )
    return f"<table><thead><tr>{head_html}</tr></thead><tbody>{body_html}</tbody></table>"


def basic_markdown_to_html(md: str) -> str:
    out: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    table_lines: list[str] = []
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            out.append(f"<p>{_inline_format(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            out.append("<ul>" + "".join(f"<li>{_inline_format(item)}</li>" for item in list_items) + "</ul>")
            list_items = []

    def flush_table() -> None:
        nonlocal table_lines
        if table_lines:
            out.append(_render_table(table_lines))
            table_lines = []

    def flush_code() -> None:
        nonlocal code_lines
        if code_lines:
            out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
            code_lines = []

    for raw_line in md.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            flush_table()
            if in_code:
                flush_code()
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped:
            flush_paragraph()
            flush_list()
            flush_table()
            continue

        if stripped.startswith("<!--") or stripped.startswith("<"):
            flush_paragraph()
            flush_list()
            flush_table()
            out.append(line)
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            flush_paragraph()
            flush_list()
            flush_table()
            level = len(heading_match.group(1))
            out.append(f"<h{level}>{_inline_format(heading_match.group(2))}</h{level}>")
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            flush_list()
            table_lines.append(stripped)
            continue

        if stripped.startswith("- "):
            flush_paragraph()
            flush_table()
            list_items.append(stripped[2:].strip())
            continue

        if table_lines:
            flush_table()
        paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    flush_table()
    if in_code:
        flush_code()
    return "\n".join(out)


def prepare_flow_markdown(md: str) -> str:
    def replace_step(match: re.Match[str]) -> str:
        step_num = match.group("num")
        title = html.escape(match.group("title"))
        step_id = html.escape(match.group("id"))
        actor = html.escape(match.group("actor"))
        return (
            f'<h3 id="{step_id}">Step {step_num}: {title} · '
            f'<code class="sid">{step_id}</code> · '
            f'<span class="actor-chip">{actor}</span></h3>'
        )

    return STEP_HEADING_RE.sub(replace_step, md)


def md_to_html(md: str) -> str:
    prepared = prepare_flow_markdown(md)
    if not os.environ.get("KB_JOURNEYS_DISABLE_MARKDOWN"):
        try:
            import markdown  # type: ignore

            return markdown.markdown(prepared, extensions=["fenced_code", "tables", "md_in_html"])
        except ImportError:
            pass
    return basic_markdown_to_html(prepared)


def summarize_readiness(md: str) -> tuple[str, str, str]:
    matches = list(READINESS_RE.finditer(md))
    if not matches:
        return ("partial", "Draft", "Readiness not declared yet.")
    by_priority = {"blocked": 3, "partial": 2, "feasible": 1}
    selected = max(matches, key=lambda m: by_priority.get(m.group("key"), 0))
    return (
        selected.group("key"),
        selected.group("label").strip(),
        html.escape(selected.group("reason").strip()),
    )


def journey_output_slug(source_dir: Path, md_path: Path) -> str:
    rel = md_path.relative_to(source_dir)
    if md_path.name == "README.md":
        return rel.parent.name.replace(".", "-")
    return rel.stem.replace(".", "-")


def discover_journey_files(source_dir: Path) -> list[Path]:
    journey_files = sorted(
        p
        for p in source_dir.glob("*.md")
        if p.stem not in ("overview", "README")
    )
    journey_files.extend(
        sorted(
            p / "README.md"
            for p in source_dir.iterdir()
            if p.is_dir() and (p / "README.md").exists()
        )
    )
    return journey_files


def parse_journey_doc(source_dir: Path, md_path: Path) -> JourneyDoc:
    md = md_path.read_text(encoding="utf-8")
    fallback_name = md_path.parent.name if md_path.name == "README.md" else md_path.stem
    tier, phase, title = parse_title(md, fallback_name)
    meta = parse_metadata(md)
    flow_md, interfaces_md = split_flow(md)
    readiness_class, readiness_label, readiness_rationale = summarize_readiness(md)
    output_slug = journey_output_slug(source_dir, md_path)
    return JourneyDoc(
        source_path=md_path,
        output_slug=output_slug,
        journey_id=f"{tier}.{phase}".strip("."),
        title=title,
        tier=tier,
        phase=phase,
        subtitle=meta.get("sub-journey", ""),
        tier_label=meta.get("tier", f"Tier {tier}" if tier else "Tier"),
        target_duration=meta.get("target duration", ""),
        last_updated=meta.get("last updated", ""),
        steps=parse_steps(md),
        flow_md=flow_md,
        interfaces_md=interfaces_md,
        readiness_class=readiness_class,
        readiness_label=readiness_label,
        readiness_rationale=readiness_rationale,
    )


def render_journey(
    doc: JourneyDoc,
    template: str,
    skill_version: str,
    logo_light: str,
    logo_dark: str,
    nav_entries: list[dict[str, str]],
    include_terminal_anim: bool,
) -> str:
    title_prefix = f"{doc.tier}.{doc.phase}" if doc.phase else doc.tier
    return render_template(
        template,
        skill_version=skill_version,
        generated_at=dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        journey_title=html.escape(f"{title_prefix} — {doc.title}".strip()),
        subtitle=html.escape(doc.subtitle),
        tier_label=html.escape(doc.tier_label),
        target_duration=html.escape(doc.target_duration),
        last_updated=html.escape(doc.last_updated),
        readiness_class=doc.readiness_class,
        readiness_chip=doc.readiness_class,
        readiness_label=html.escape(doc.readiness_label),
        readiness_rationale=doc.readiness_rationale,
        steps=doc.steps,
        rendered_flow_html=md_to_html(doc.flow_md),
        rendered_interfaces_html=md_to_html(doc.interfaces_md),
        nav_entries=nav_entries,
        logo_light=logo_light or "",
        logo_dark=logo_dark or "",
        include_terminal_anim="yes" if include_terminal_anim else "",
    )


def render_overview_html(
    overview_md: str,
    docs: list[JourneyDoc],
    skill_version: str,
) -> str:
    cards = []
    for doc in docs:
        cards.append(
            f'<article class="journey-card">'
            f'<div class="journey-card-meta">Tier {html.escape(doc.tier or "–")}</div>'
            f'<h2><a href="{html.escape(doc.output_slug)}.html">{html.escape(doc.journey_id or doc.output_slug)}</a></h2>'
            f'<p>{html.escape(doc.title)}</p>'
            f'<div class="journey-card-links"><span class="status-chip {html.escape(doc.readiness_class)}">{html.escape(doc.readiness_label)}</span></div>'
            f"</article>"
        )
    overview_body = md_to_html(overview_md) if overview_md.strip() else "<p>No overview.md authored yet.</p>"
    generated_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="auto">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="generator" content="kb-journeys v{html.escape(skill_version)}">
  <title>Journeys — Overview</title>
  <link rel="stylesheet" href="shared.css">
</head>
<body>
  <nav class="nav" aria-label="Journey navigation">
    <a href="index.html" class="nav-home">Overview</a>
    <button class="theme-toggle" aria-label="Toggle theme" data-action="toggle-theme">☾</button>
  </nav>
  <header class="journey-header">
    <h1>Journeys — Overview</h1>
    <div class="subtitle">Cross-journey map and generated entry point.</div>
    <div class="meta">Generated {html.escape(generated_at)} · kb-journeys v{html.escape(skill_version)}</div>
  </header>
  <main class="container">
    <section class="journey-summary">
      <h2>Journeys</h2>
      <div class="journey-card-grid">
        {"".join(cards) if cards else "<p>No journeys found.</p>"}
      </div>
    </section>
    <section class="journey-flow">
      {overview_body}
    </section>
  </main>
  <footer class="journey-footer">
    <span>kb-journeys v{html.escape(skill_version)}</span> ·
    <span>Generated {html.escape(generated_at)}</span>
  </footer>
  <script>
    (function () {{
      var root = document.documentElement;
      var saved = localStorage.getItem('kb-journeys-theme');
      if (saved) root.setAttribute('data-theme', saved);
      document.querySelectorAll('[data-action="toggle-theme"]').forEach(function (btn) {{
        btn.addEventListener('click', function () {{
          var cur = root.getAttribute('data-theme') || 'auto';
          var next = cur === 'dark' ? 'light' : cur === 'light' ? 'auto' : 'dark';
          root.setAttribute('data-theme', next);
          localStorage.setItem('kb-journeys-theme', next);
        }});
      }});
    }})();
  </script>
</body>
</html>
"""


def run_mock_extractor(
    html_dir: Path,
    mocks_dir: Path,
    mock_template: Path,
    skill_version: str,
) -> None:
    extractor = Path(__file__).with_name("extract_mocks.py")
    subprocess.run(
        [
            sys.executable,
            str(extractor),
            "--html-dir",
            str(html_dir),
            "--mocks-dir",
            str(mocks_dir),
            "--template",
            str(mock_template),
            "--skill-version",
            skill_version,
        ],
        check=True,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    ap.add_argument("--template", required=True, type=Path)
    ap.add_argument("--shared-css", required=True, type=Path)
    ap.add_argument("--tokens", type=Path, default=None)
    ap.add_argument("--logo-light", default="")
    ap.add_argument("--logo-dark", default="")
    ap.add_argument("--mock-template", type=Path, default=None)
    ap.add_argument("--skill-version", default="0.1.1")
    ap.add_argument("--include-terminal-anim", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    source_dir = args.source_dir.resolve()
    out_dir = args.output_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    mocks_dir = out_dir / "mocks"

    css_out = merge_shared_css(args.shared_css, args.tokens)
    template = args.template.read_text(encoding="utf-8")
    mock_template = args.mock_template or (args.template.parent / "mock-standalone.html.hbs")

    journey_docs = [parse_journey_doc(source_dir, path) for path in discover_journey_files(source_dir)]
    nav_entries = [
        {
            "tier_class": f"n{doc.tier}" if doc.tier.isdigit() else "n1",
            "href": f"{doc.output_slug}.html",
            "label": f"{doc.journey_id} {doc.title}".strip(),
        }
        for doc in journey_docs
    ]

    if args.dry_run:
        print(f"kb-journeys render (dry-run): {len(journey_docs)} journey(s)")
        for doc in journey_docs:
            print(f"  would write: {out_dir / (doc.output_slug + '.html')}")
        print(f"  would write: {out_dir / 'index.html'}")
        print(f"  would write: {mocks_dir / 'index.html'}")
        return 0

    (out_dir / "shared.css").write_text(css_out, encoding="utf-8")

    for doc in journey_docs:
        html_out = render_journey(
            doc,
            template,
            args.skill_version,
            args.logo_light,
            args.logo_dark,
            nav_entries,
            args.include_terminal_anim,
        )
        (out_dir / f"{doc.output_slug}.html").write_text(html_out, encoding="utf-8")

    overview_path = source_dir / "overview.md"
    overview_md = overview_path.read_text(encoding="utf-8") if overview_path.exists() else ""
    (out_dir / "index.html").write_text(
        render_overview_html(overview_md, journey_docs, args.skill_version),
        encoding="utf-8",
    )

    run_mock_extractor(out_dir, mocks_dir, mock_template, args.skill_version)

    print(f"kb-journeys render: {len(journey_docs)} journey(s) -> {out_dir}")
    print(f"  overview: {out_dir / 'index.html'}")
    print(f"  mocks: {mocks_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
