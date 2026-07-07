#!/usr/bin/env python3
"""
Generate translations for all 10 languages by reading English source and
applying systematic translations, then writing locale files.
"""
import json
import os
import subprocess
import sys

LOCALES_DIR = "/Users/sipi/churnlens/i18n/locales"
EN_PATH = os.path.join(LOCALES_DIR, "en", "_combined.json")
WRITE_SCRIPT = os.path.join(LOCALES_DIR, "..", "write_translations.py")

# Load English source
with open(EN_PATH) as f:
    en_data = json.load(f)

# Collect all entries
all_entries = []
for page, page_data in en_data.items():
    for k, v in page_data.items():
        all_entries.append((k, v))
all_entries.sort(key=lambda x: x[0])

en_dict = {k: v for k, v in all_entries}
print(f"Loaded {len(all_entries)} English segments")

def write_lang(lang_code, translations):
    """Pipe translations to write_translations.py"""
    lines = []
    for k in sorted(translations.keys()):
        v = translations[k].replace('\n', '\\n')
        lines.append(f"{k}|{v}")
    lines.append("DONE")
    
    result = subprocess.run(
        [sys.executable, WRITE_SCRIPT, lang_code],
        input="\n".join(lines),
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    print(f"  {result.stdout.strip()}")
    if result.stderr.strip():
        print(f"  stderr: {result.stderr.strip()}")
    return result.returncode == 0

# We'll generate translations programmatically.
# Since I can translate for each language, I'll create one big dict per language.

# ======================================================
# SPANISH (es)
# ======================================================
def translate_es(text):
    """Translate English text to Spanish"""
    # Brand names must stay unchanged
    t = text
    # Common substitutions for Spanish
    t = t.replace('Churn Lens', 'Churn Lens').replace('SaaS', 'SaaS')
    return t

# For the actual translation, I'll create the full dict per language
# by processing each English segment

print("\n=== SPANISH (es) ===")
es_translations = {}

# I'll build translations as a Python dict by processing each key individually
# For efficiency, I'm going to create a massive translation block

# Let me check how many unique pages there are and their text lengths
page_texts = {}
for k, v in all_entries:
    page = k.split('__TR_')[1].split('_')[0]
    page_texts.setdefault(page, []).append((k, v))

for page in sorted(page_texts.keys()):
    print(f"  {page}: {len(page_texts[page])} entries")
