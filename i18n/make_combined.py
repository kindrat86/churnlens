#!/usr/bin/env python3
"""Create _combined.json for a language from per-page files."""
import os, json, sys

LOCALES_DIR = "/Users/sipi/churnlens/i18n/locales"
lang = sys.argv[1] if len(sys.argv) > 1 else "en"

lang_dir = os.path.join(LOCALES_DIR, lang)
combined = {}

for fname in sorted(os.listdir(lang_dir)):
    if not fname.endswith('.json') or fname == '_combined.json':
        continue
    page_name = fname.replace('.json', '')
    with open(os.path.join(lang_dir, fname), 'r', encoding='utf-8') as f:
        combined[page_name] = json.load(f)

out_path = os.path.join(lang_dir, '_combined.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(combined, f, indent=2, ensure_ascii=False)

total = sum(len(v) for v in combined.values())
print(f"Created {out_path}: {len(combined)} pages, {total} keys")
