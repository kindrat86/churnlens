#!/usr/bin/env python3
"""
Ingest translations from a subagent's response.
Usage: python3 i18n/ingest_translations.py <lang_code> < <(cat translated_output.txt)

Or for interactive use:
  python3 i18n/ingest_translations.py es
Then paste the KEY|VALUE lines and press Ctrl+D, then type DONE on a new line.

Actually more practical: read from a file.
  python3 i18n/ingest_translations.py <lang_code> [input_file]
  
If no input_file, reads from stdin until 'DONE' on its own line.
"""
import os, json, sys, re

I18N_DIR = "/Users/sipi/churnlens/i18n"
LOCALES_DIR = os.path.join(I18N_DIR, "locales")

def ingest(lang_code, lines_iter):
    """Parse KEY|VALUE lines and write per-page locale files."""
    translations = {}
    line_count = 0
    key_count = 0
    
    for line in lines_iter:
        line = line.strip()
        line_count += 1
        
        if not line or line.startswith('#') or line.startswith('---'):
            continue
        if line == 'DONE':
            break
        if '|' not in line:
            continue
        
        key, _, val = line.partition('|')
        key = key.strip()
        val = val.strip()
        
        if not key or not val:
            continue
        if key.startswith('#') or key.startswith('---'):
            continue
        
        translations[key] = val.replace('\\n', '\n')
        key_count += 1
    
    if not translations:
        print("No translations parsed!")
        return 0
    
    # Group by page and write
    page_data = {}
    for key, val in translations.items():
        if '__TR_' in key:
            parts = key.split('__TR_')[1]
            page_name = parts.split('_')[0] if '_' in parts else "_unknown"
        else:
            page_name = "_unknown"
        if page_name not in page_data:
            page_data[page_name] = {}
        page_data[page_name][key] = val
    
    output_dir = os.path.join(LOCALES_DIR, lang_code)
    os.makedirs(output_dir, exist_ok=True)
    
    total = 0
    for page_name, data in sorted(page_data.items()):
        out_path = os.path.join(output_dir, f"{page_name}.json")
        # Merge with existing if any
        existing = {}
        if os.path.exists(out_path):
            with open(out_path, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        existing.update(data)
        
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        total += len(existing)
        
        print(f"  Wrote {len(existing)} keys to {page_name}.json")
    
    print(f"\nIngested {key_count} new translations for {lang_code}")
    print(f"Output dir: {output_dir}")
    return key_count

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 i18n/ingest_translations.py <lang_code> [input_file]")
        sys.exit(1)
    
    lang_code = sys.argv[1]
    
    if len(sys.argv) >= 3:
        input_file = sys.argv[2]
        with open(input_file, 'r', encoding='utf-8') as f:
            ingest(lang_code, f)
    else:
        print(f"Paste translations for {lang_code}, then type 'DONE' on a new line:")
        ingest(lang_code, sys.stdin)
