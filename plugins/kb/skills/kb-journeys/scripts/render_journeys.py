#!/usr/bin/env python3
"""kb-journeys render: markdown journey files -> HTML set + mocks.

Generic — no vendor strings. Reads journey markdown, emits per-journey HTML
plus shared.css (with adopter's brand tokens merged) and an overview index.
Then delegates to extract_mocks.py for standalone-mock pages.

Minimal pilot: preserves structure, renders metadata block + step summary +
flow sections. Adopters wanting richer rendering replace this script with
their own renderer binding to the same contract.

Usage:
  python3 render_journeys.py \\
      --source-dir _kb-journeys \\
      --output-dir _kb-journeys/html \\
      --template <skill>/templates/journey.html.hbs \\
      --shared-css <skill>/templates/shared.css.hbs \\
      [--tokens brand-tokens.css] \\
    [--skill-version 0.1.0]
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import sys
from pathlib import Path


STEP_HEADING_RE = re.compile(
    r"^###\s+Step\s+(?P<num>\d+):\s+(?P<title>.+?)\s+·\s+`(?P<id>J[\d.]+-S\d+)`\s+·\s+`\[(?P<actor>[^\]]+)\]`",
    re.MULTILINE,
)
META_LINE_RE = re.compile(r"^\s*>\s+\*\*(?P<key>[^:]+)\*\*:\s*(?P<value>.+?)\s*$", re.MULTILINE)
TITLE_RE = re.compile(r"^#\s+(?P<tp>\d+(?:\.\d+)*)\s+—\s+(?P<title>.+?)\s*$", re.MULTILINE)


def render_template(template: str, **vars: str) -> str:
    out = template
    # Resolve {{#if key}}...{{/if}} first (single-branch, truthy means non-empty string).
    def replace_if(m: re.Match) -> str:
        key = m.group(1).strip()
        body = m.group(2)
        return body if vars.get(key) else ""
    out = re.sub(r"\{\{#if\s+(\w+)\}\}([\s\S]*?)\{\{/if\}\}", replace_if, out)
    # Resolve {{#each key}}...{{/each}} — iterate list of dicts, substitute inner {{field}}.
    def replace_each(m: re.Match) -> str:
        key = m.group(1).strip()
        body = m.group(2)
        items = vars.get(key) or []
        rendered_parts = []
        for item in items:
            piece = body
            if isinstance(item, dict):
                for ik, iv in item.items():
                    piece = piece.replace("{{" + ik + "}}", str(iv))
            rendered_parts.append(piece)
        return "".join(rendered_parts)
    out = re.sub(r"\{\{#each\s+(\w+)\}\}([\s\S]*?)\{\{/each\}\}", replace_each, out)
    # Simple substitutions.
    for k, v in vars.items():
        if isinstance(v, (list, dict)):
            continue
        out = out.replace("{{" + k + "}}", str(v))
        out = out.replace("{{{" + k + "}}}", str(v))
    # Drop unresolved simple placeholders.
    out = re.sub(r"\{\{[^{}#/]+\}\}", "", out)
    return out


def parse_metadata(md: str) -> dict:
    meta = {}
    for m in META_LINE_RE.finditer(md[:2000]):
        meta[m.group("key").strip().lower()] = m.group("value").strip()
    return meta


def parse_title(md: str) -> tuple[str, str, str]:
    m = TITLE_RE.search(md)
    if not m:
        return ("", "", Path(".").stem)
    tp = m.group("tp")
    title = m.group("title")
    parts = tp.split(".")
    tier = parts[0] if parts else ""
    phase = parts[1] if len(parts) > 1 else ""
    return (tier, phase, title)


def parse_steps(md: str) -> list[dict]:
    steps = []
    for m in STEP_HEADING_RE.finditer(md):
        steps.append({
            "id": m.group("id"),
            "title": m.group("title"),
            "actor": m.group("actor"),
        })
    return steps


def md_to_flow_html(md: str) -> str:
    """Minimal markdown-to-html for the flow section. Preserves raw HTML
    (critical for mock envelopes) and handles headings, paragraphs, lists, code."""
    try:
        import markdown  # type: ignore
    except ImportError:
        print("kb-journeys render: python-markdown not installed; falling back to <pre>",
              file=sys.stderr)
        return f"<pre>{html.escape(md)}</pre>"
    return markdown.markdown(md, extensions=["fenced_code", "tables", "md_in_html"])


def split_flow(md: str) -> tuple[str, str]:
    """Return (flow_section_md, interfaces_section_md)."""
    parts = re.split(r"^##\s+Flow\s*$", md, maxsplit=1, flags=re.MULTILINE)
    after_flow = parts[1] if len(parts) == 2 else ""
    flow_md = after_flow
    interfaces_md = ""
    # Interfaces section appears before Flow in our template, so capture from original.
    im = re.search(r"^##\s+Interfaces\s*$([\s\S]*?)(?=^##\s+)", md, re.MULTILINE)
    if im:
        interfaces_md = im.group(1)
    return flow_md, interfaces_md


def merge_shared_css(base_path: Path, tokens_path: Path | None) -> str:
    base = base_path.read_text(encoding="utf-8")
    if not tokens_path or not tokens_path.exists():
        return base
    adopter = tokens_path.read_text(encoding="utf-8")
    adopter_root = re.search(r":root\s*\{[^}]*\}", adopter, re.DOTALL)
    if not adopter_root:
        return base
    return re.sub(r":root\s*\{[^}]*\}", adopter_root.group(0), base, count=1, flags=re.DOTALL)


def render_journey(
    md_path: Path,
    template: str,
    skill_version: str,
    logo_light: str,
    logo_dark: str,
    nav_entries: list[dict],
) -> str:
    md = md_path.read_text(encoding="utf-8")
    tier, phase, title = parse_title(md)
    meta = parse_metadata(md)
    steps = parse_steps(md)
    flow_md, interfaces_md = split_flow(md)

    return render_template(
        template,
        skill_version=skill_version,
        generated_at=dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        journey_title=html.escape(f"{tier}.{phase} — {title}"),
        subtitle=html.escape(meta.get("sub-journey", "")),
        tier_label=html.escape(meta.get("tier", f"Tier {tier}")),
        target_duration=html.escape(meta.get("target duration", "")),
        last_updated=html.escape(meta.get("last updated", "")),
        readiness_class="feasible",
        readiness_chip="feasible",
        readiness_label="Ready",
        readiness_rationale=html.escape(meta.get("readiness", "")),
        steps=steps,
        rendered_flow_html=md_to_flow_html(flow_md),
        rendered_interfaces_html=md_to_flow_html(interfaces_md),
        nav_entries=nav_entries,
        logo_light=logo_light or "",
        logo_dark=logo_dark or "",
        include_terminal_anim="",
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
    ap.add_argument("--skill-version", default="0.1.0")
    args = ap.parse_args()

    out_dir: Path = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Emit shared.css with adopter's tokens merged in.
    css_out = merge_shared_css(args.shared_css, args.tokens)
    (out_dir / "shared.css").write_text(css_out, encoding="utf-8")

    template = args.template.read_text(encoding="utf-8")

    journey_files = sorted(p for p in args.source_dir.glob("*.md")
                           if p.stem not in ("overview", "README"))

    nav_entries = []
    for jf in journey_files:
        tier_phase = jf.stem.split("-", 1)[0]
        tier = tier_phase.split(".")[0] if "." in tier_phase else tier_phase
        nav_entries.append({
            "tier_class": f"n{tier}" if tier.isdigit() else "n1",
            "href": f"{jf.stem.replace('.', '-')}.html",
            "label": jf.stem.replace("-", " ").title(),
        })

    count = 0
    for jf in journey_files:
        html_out = render_journey(
            jf, template, args.skill_version,
            args.logo_light, args.logo_dark, nav_entries,
        )
        out_file = out_dir / f"{jf.stem.replace('.', '-')}.html"
        out_file.write_text(html_out, encoding="utf-8")
        count += 1

    print(f"kb-journeys render: {count} journey(s) -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
