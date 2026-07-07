#!/usr/bin/env python3
"""
Generate complete translation JSON for a single language.
Usage: python3 generate_lang.py <lang_code>
Outputs: /tmp/trans/<lang_code>.json (full translated dict)
Then pipe through writer.
"""
import json, os, subprocess, sys

LOCALES_DIR = "/Users/sipi/churnlens/i18n/locales"
EN_PATH = os.path.join(LOCALES_DIR, "en", "_combined.json")
WRITE_SCRIPT = os.path.join(LOCALES_DIR, "..", "write_translations.py")

with open(EN_PATH) as f:
    en_data = json.load(f)

all_entries = []
for page, page_data in en_data.items():
    for k, v in page_data.items():
        all_entries.append((k, v.replace('\n', '\\n'), page))
all_entries.sort(key=lambda x: x[0])
en_dict = {k: v for k, v, p in all_entries}

if __name__ == '__main__':
    lang = sys.argv[1]
    
    # Import the translation data
    # For each language, we'll build the translations by loading
    # from a pre-computed file or computing them here
    
    # For now, let's create placeholder that copies English
    # (this will be replaced with actual translations)
    
    translations = dict(en_dict)  # Start with English copy
    
    out_path = f"/tmp/trans/{lang}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(translations, f, indent=2, ensure_ascii=False)
    
    print(f"Written {len(translations)} keys to {out_path}")
