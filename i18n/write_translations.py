#!/usr/bin/env python3
"""
WRITE TRANSLATIONS - called by subagents to write locale files.
Usage: python3 /Users/sipi/churnlens/i18n/write_translations.py <lang_code>

Reads KEY|VALUE lines from stdin (until DONE on its own line),
then writes per-page JSON locale files.
"""
import os, json, sys

LOCALES_DIR = "/Users/sipi/churnlens/i18n/locales"

if __name__ == "__main__":
    lang_code = sys.argv[1]
    translations = {}
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        if line == 'DONE':
            break
        if '|' not in line:
            continue
        k, _, v = line.partition('|')
        k, v = k.strip(), v.strip()
        if k and v:
            translations[k] = v.replace('\\n', '\n')
    
    if not translations:
        print("No translations received")
        sys.exit(1)
    
    # Group by page
    pages = {}
    for k, v in translations.items():
        pn = k.split('__TR_')[1].split('_')[0] if '__TR_' in k else "_unknown"
        pages.setdefault(pn, {})[k] = v
    
    out_dir = os.path.join(LOCALES_DIR, lang_code)
    os.makedirs(out_dir, exist_ok=True)
    
    total = 0
    for pn, data in sorted(pages.items()):
        path = os.path.join(out_dir, f"{pn}.json")
        existing = {}
        if os.path.exists(path):
            with open(path) as f:
                existing = json.load(f)
        existing.update(data)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        total += len(existing)
    
    print(f"Written {len(translations)} keys for {lang_code} to {out_dir}")
