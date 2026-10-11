#!/usr/bin/env python3
"""Render the catalog JSON into crawlable, accessible fallback HTML.

Run from the repository root with: python3 tools/build_catalog_html.py
The JavaScript catalog remains the interactive version; generated markup keeps all
catalog names and descriptions available to crawlers and no-JavaScript visitors.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "tools" / "index.html"
DATA = ROOT / "tools" / "catalog.json"
START = "      <!-- CATALOG:START -->"
END = "      <!-- CATALOG:END -->"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def card(item: dict) -> str:
    title = esc(item["title"])
    category = esc(item["category"])
    description = esc(item["description"])
    price = esc(item["price"])
    url = esc(item["url"])
    image = esc(item.get("image", ""))
    free = bool(item.get("free"))
    action = "Dùng miễn phí trên AIZENING" if free else "Mở công cụ trên AIZENING"
    cls = "card-action free-action" if free else "card-action"
    image_markup = (
        f'<img src="{image}" alt="{title}" loading="lazy" decoding="async">'
        if image else '<div class="preview-placeholder"><span class="placeholder-mark" aria-hidden="true">AI</span></div>'
    )
    badge = '<span class="free-badge">MIỄN PHÍ</span>' if free else ""
    limit = f'<span class="limit">{esc(item["limit"])}</span>' if free and item.get("limit") else ""
    return (
        f'        <article class="tool-card" data-tool-id="{esc(item["id"])}">\n'
        f'          <div class="preview">{image_markup}<span class="preview-shade" aria-hidden="true"></span>'
        f'<span class="category-chip">{category}</span>{badge}</div>\n'
        f'          <div class="card-body"><h2>{title}</h2><p>{description}</p>'
        f'<div class="card-meta"><span class="price{" free-price" if free else ""}">{price}</span>{limit}</div>'
        f'<a class="{cls}" href="{url}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="{esc(action)}: {title} trên AIZENING"><span>{action}</span>'
        f'<span class="external-arrow" aria-hidden="true">↗</span></a></div>\n'
        f'        </article>'
    )


def main() -> None:
    items = json.loads(DATA.read_text(encoding="utf-8"))
    source = PAGE.read_text(encoding="utf-8")
    if source.count(START) != 1 or source.count(END) != 1:
        raise SystemExit("Expected exactly one catalog marker pair in tools/index.html")
    before, remainder = source.split(START, 1)
    _, after = remainder.split(END, 1)
    rendered = "\n" + "\n".join(card(item) for item in items) + "\n      "
    PAGE.write_text(before + START + rendered + END + after, encoding="utf-8")
    print(f"Rendered {len(items)} catalog entries into {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
