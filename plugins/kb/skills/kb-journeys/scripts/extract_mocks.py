#!/usr/bin/env python3
"""kb-journeys mock extractor.

Walks the generated per-journey HTML files, finds every
`<!-- mock-begin: SLUG -->...<!-- mock-end: SLUG -->` envelope,
lifts the container (plus nested <style>/<script>) into a standalone
page under <html-subdir>/mocks/, and injects an "Open standalone" link
into the mock header of the source page.

Idempotent. Generic — carries no vendor-specific strings.

Inputs:
  --html-dir   path to the directory containing per-journey HTML
  --mocks-dir  path to the mocks output subdirectory (under html-dir)
  --template   path to mock-standalone.html.hbs
  --skill-version  the kb-journeys version string to emit into metadata
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

try:
    from bs4 import BeautifulSoup, Tag
except ImportError:
    print("kb-journeys extract-mocks requires beautifulsoup4. "
          "Install with: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)


MOCK_BEGIN_RE = re.compile(r"<!--\s*mock-begin:\s*([a-z0-9][a-z0-9-]*)\s*-->")
MOCK_END_FMT = "<!-- mock-end: {slug} -->"
STEP_ID_RE = re.compile(r"^J\d+(?:\.\d+)*-S\d+$")


def slugify(value: str) -> str:
    v = value.lower()
    v = re.sub(r"[^a-z0-9]+", "-", v).strip("-")
    return v or "mock"


def derive_journey_id(path: Path) -> str:
    """Given html/1-3-bugfix-loop.html -> 1-3-bugfix-loop."""
    return path.stem


def journey_label(stem: str) -> str:
    parts = stem.split("-", 2)
    head = parts[0]
    if len(parts) > 1 and re.fullmatch(r"\d+", parts[1] or ""):
        head = parts[0] + "." + parts[1]
        rest = parts[2] if len(parts) > 2 else ""
    else:
        rest = "-".join(parts[1:])
    rest = rest.replace("-", " ").title()
    return f"{head} — {rest}".strip(" —")


def nearest_step_anchor(node: Tag) -> str | None:
    cur: Tag | None = node
    while cur is not None:
        for cand in [cur] + list(cur.find_all_previous(id=True, limit=10)):
            if not isinstance(cand, Tag):
                continue
            cid = cand.get("id")
            if cid and STEP_ID_RE.match(cid):
                return cid
        cur = cur.parent
    return None


def read_template(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def render_template(template: str, **vars: str) -> str:
    out = template
    for k, v in vars.items():
        out = out.replace("{{" + k + "}}", str(v))
        out = out.replace("{{{" + k + "}}}", str(v))
    # Strip unresolved simple placeholders (preserves triple-brace blocks we filled).
    out = re.sub(r"\{\{[^{}]+\}\}", "", out)
    return out


def extract_one(html_text: str, source_path: Path) -> tuple[list[dict], str]:
    """Return (mocks, patched_html_text)."""
    soup = BeautifulSoup(html_text, "html.parser")
    mocks: list[dict] = []

    # Find mock-begin / mock-end pairs by walking the document in source order.
    # BeautifulSoup comments are NavigableString with type Comment.
    from bs4 import Comment
    comments = list(soup.find_all(string=lambda t: isinstance(t, Comment)))

    open_slugs: dict[str, tuple[Tag, Tag]] = {}
    for c in comments:
        m = MOCK_BEGIN_RE.search(str(c))
        if m:
            slug = m.group(1)
            open_slugs[slug] = (c, None)  # type: ignore
            continue
        end = re.match(r"\s*mock-end:\s*([a-z0-9][a-z0-9-]*)\s*", str(c))
        if end:
            slug = end.group(1)
            if slug not in open_slugs:
                continue
            begin_comment, _ = open_slugs.pop(slug)
            # Find the first mockup-block between begin_comment and c (the end comment).
            container = None
            for sib in begin_comment.find_all_next():
                if sib is c:
                    break
                if isinstance(sib, Tag) and sib.has_attr("class") and "mockup-block" in sib["class"]:
                    container = sib
                    break
            if container is None:
                continue
            anchor = nearest_step_anchor(container)
            title_el = container.find(attrs={"class": "mockup-title"})
            title = title_el.get_text(strip=True) if title_el else slug
            # Lift nested <style>/<script> tags verbatim.
            styles = [str(t) for t in container.find_all("style")]
            scripts = [str(t) for t in container.find_all("script")]
            mocks.append({
                "slug": slug,
                "title": title,
                "anchor": anchor,
                "container_html": str(container),
                "styles": "\n".join(styles),
                "scripts": "\n".join(scripts),
            })

            # Patch: inject or replace the "Open standalone" link in the mockup-header.
            header = container.find(attrs={"class": "mockup-header"})
            if header is not None:
                existing = header.find("a", class_="mock-standalone-link")
                target_href = f"mocks/{source_path.stem}_{slug}.html"
                if existing is not None:
                    existing["href"] = target_href
                else:
                    link = soup.new_tag("a", href=target_href)
                    link["class"] = "mock-standalone-link"
                    link.string = "↗ Open standalone"
                    header.append(link)

    return mocks, str(soup)


def render_standalone(template: str, mock: dict, source_path: Path, skill_version: str) -> str:
    journey_stem = source_path.stem
    anchor = f"#{mock['anchor']}" if mock["anchor"] else ""
    href = f"{journey_stem}.html{anchor}"
    label = journey_label(journey_stem)
    return render_template(
        template,
        skill_version=skill_version,
        mock_title=html.escape(mock["title"]),
        journey_href=href,
        journey_label=html.escape(label),
        mock_local_styles=mock["styles"],
        mock_body_html=mock["container_html"],
        mock_local_scripts=mock["scripts"],
    )


def render_index(mocks_by_source: dict[Path, list[dict]], html_dir: Path) -> str:
    rows = []
    total = 0
    for src_path, mocks in sorted(mocks_by_source.items()):
        if not mocks:
            continue
        rows.append(f"    <section><h2>{html.escape(journey_label(src_path.stem))}</h2><ul>")
        for m in mocks:
            total += 1
            anchor = f"#{m['anchor']}" if m["anchor"] else ""
            rows.append(
                f"      <li>"
                f"<a href=\"{src_path.stem}_{m['slug']}.html\">{html.escape(m['title'])}</a> "
                f"<code class=\"sid\">{m['slug']}</code> "
                f"<a class=\"src-link\" href=\"../{src_path.stem}.html{anchor}\">(in journey)</a>"
                f"</li>"
            )
        rows.append("    </ul></section>")
    body = "\n".join(rows) if rows else "    <p>No mocks extracted yet.</p>"
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="auto"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mocks · index</title>
<link rel="stylesheet" href="../shared.css">
</head><body>
<header class="journey-header"><h1>Mocks</h1>
<div class="meta">{total} mock{'' if total == 1 else 's'} across {len([k for k, v in mocks_by_source.items() if v])} journey{'' if len(mocks_by_source) == 1 else 's'}</div>
</header>
<main class="container">
{body}
</main>
</body></html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html-dir", required=True, type=Path)
    ap.add_argument("--mocks-dir", required=True, type=Path)
    ap.add_argument("--template", required=True, type=Path)
    ap.add_argument("--skill-version", default="0.2.0")
    args = ap.parse_args()

    html_dir: Path = args.html_dir
    mocks_dir: Path = args.mocks_dir
    template = read_template(args.template)

    mocks_dir.mkdir(parents=True, exist_ok=True)

    sources = sorted(p for p in html_dir.glob("*.html") if p.stem != "index" and p.parent == html_dir)

    mocks_by_source: dict[Path, list[dict]] = {}
    for src in sources:
        text = src.read_text(encoding="utf-8")
        mocks, patched = extract_one(text, src)
        mocks_by_source[src] = mocks
        if patched != text:
            src.write_text(patched, encoding="utf-8")
        for m in mocks:
            out = mocks_dir / f"{src.stem}_{m['slug']}.html"
            out.write_text(render_standalone(template, m, src, args.skill_version), encoding="utf-8")

    (mocks_dir / "index.html").write_text(render_index(mocks_by_source, html_dir), encoding="utf-8")

    total_mocks = sum(len(v) for v in mocks_by_source.values())
    print(f"kb-journeys extract-mocks: {total_mocks} mock(s) across {len(sources)} journey(s) "
          f"-> {mocks_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
