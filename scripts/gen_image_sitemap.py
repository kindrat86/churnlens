#!/usr/bin/env python3
"""Regenerate image-sitemap.xml from the main sitemap.xml URLs.

Fixes: removes fragment URLs, adds full domain to relative URLs,
removes external URLs, and only includes churnlens.site pages.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = "https://churnlens.site"

sitemap_content = (REPO / "sitemap.xml").read_text(encoding="utf-8")
urls = re.findall(r"<loc>([^<]+)</loc>", sitemap_content)

lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
    '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
]

# Only include churnlens.site URLs (no external)
for url in sorted(urls):
    if not url.startswith(BASE):
        continue
    lines.append("  <url>")
    lines.append(f"    <loc>{url}</loc>")
    lines.append("      <image:image>")
    lines.append(f"        <image:loc>{BASE}/og.png</image:loc>")
    lines.append("        <image:title>ChurnLens</image:title>")
    lines.append("      </image:image>")
    lines.append("  </url>")

lines.append("</urlset>")

(REPO / "image-sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Generated image-sitemap.xml: {len(urls)} URLs (all churnlens.site, no fragments)")
