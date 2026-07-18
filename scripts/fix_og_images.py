#!/usr/bin/env python3
"""
Fix og:image meta tags across the site.

Two problems:
1. 76 pages use favicon.png (256×256) as og:image → social cards render tiny
2. 150 pages have NO og:image at all → AI crawlers get no social proof image

Fixes:
- Replace favicon.png → og.png (1200×630) in og:image + width/height attrs
- Add missing og:image to pages that have other og: tags but no image

Run from ~/churnlens. Idempotent.
"""
import re
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OG_IMAGE_BLOCK = (
    '<meta property="og:image" content="https://churnlens.site/og.png" />\n'
    '    <meta property="og:image:width" content="1200" />\n'
    '    <meta property="og:image:height" content="630" />\n'
    '    <meta property="og:image:alt" content="ChurnLens" />\n'
)


def fix_file(path: Path) -> dict:
    orig = path.read_text(encoding="utf-8", errors="ignore")
    out = orig
    stats = {}

    # 1. Replace favicon.png → og.png in og:image content
    new_out, n = re.subn(
        r'(og:image"\s+content=")[^"]*favicon\.png(")',
        r'\1https://churnlens.site/og.png\2',
        out
    )
    if n:
        stats["favicon_fix"] = n
    out = new_out

    # 2. Update width/height for the image
    new_out, n_w = re.subn(
        r'(og:image:width"\s+content=")256(")',
        r'\11200\2',
        out
    )
    new_out, n_h = re.subn(
        r'(og:image:height"\s+content=")256(")',
        r'\1630\2',
        out
    )
    if n_w or n_h:
        stats["dimensions_fix"] = (n_w, n_h)
    out = new_out

    # 3. If page has og:title but NO og:image, add one
    if 'og:image' not in out and 'og:title' in out:
        # Find insertion point: after og:description or og:site_name
        m = re.search(r'(<meta property="og:(?:description|site_name)"[^>]+>)\s*\n?', out)
        if m:
            insert_after = m.group(1)
            out = out.replace(insert_after, insert_after + '\n    ' + OG_IMAGE_BLOCK.strip(), 1)
            stats["added_og_image"] = True

    if out != orig:
        path.write_text(out, encoding="utf-8")
    return stats


def main():
    total = {"fixed": 0, "added_og": 0, "fixed_fav": 0, "skipped": 0}
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.vercel', 'node_modules', 'api', '.git',
                                                  'scripts', 'assets', 'public', 'i18n_out')]
        for fname in files:
            if not fname.endswith('.html'):
                continue
            path = Path(root) / fname
            s = fix_file(path)
            if s:
                total["fixed"] += 1
                total["fixed_fav"] += s.get("favicon_fix", 0)
                if s.get("added_og_image"):
                    total["added_og"] += 1
            else:
                total["skipped"] += 1

    print(f"Fixed og:image on {total['fixed']} files "
          f"({total['fixed_fav']} favicon→og.png, {total['added_og']} missing images added) "
          f"{total['skipped']} already OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
