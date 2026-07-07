#!/usr/bin/env python3
"""
TRANSLATE ALL 2134 SEGMENTS TO ALL 10 LANGUAGES
=================================================
Reads English source, generates full translations for each language,
and pipes through write_translations.py.

Brands 'Churn Lens' and 'SaaS' stay unchanged.
HTML entities (&amp; &lt; &gt; &mdash; &rarr; etc.) stay unchanged.
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

# Build unique text -> keys map
text_to_keys = {}
text_to_entry = {}
for k, v, p in all_entries:
    text_to_keys.setdefault(v, []).append(k)
    if v not in text_to_entry:
        text_to_entry[v] = (k, v, p)

unique_texts = sorted(text_to_keys.keys())

print(f"Total segments: {len(all_entries)}, Unique texts: {len(unique_texts)}", file=sys.stderr)

def write_lang(lang_code, translations):
    lines = [f"{k}|{translations[k]}" for k in sorted(translations.keys())]
    lines.append("DONE")
    r = subprocess.run([sys.executable, WRITE_SCRIPT, lang_code],
                       input="\n".join(lines), capture_output=True, text=True, encoding='utf-8')
    print(f"  {r.stdout.strip()}", file=sys.stderr)
    if r.stderr.strip():
        print(f"  ERR: {r.stderr.strip()}", file=sys.stderr)
    return r.returncode == 0

def protect(text):
    mapping = {}
    for brand in ['Churn Lens', 'SaaS']:
        if brand in text:
            ph = f"__B{len(mapping)}__"
            mapping[ph] = brand
            text = text.replace(brand, ph)
    entities = {
        '&amp;': '__AMP__', '&lt;': '__LT__', '&gt;': '__GT__',
        '&mdash;': '__MD__', '&rarr;': '__RA__', '&times;': '__TI__',
        '&copy;': '__CP__', '&ldquo;': '__LQ__', '&rdquo;': '__RQ__',
        '&ndash;': '__ND__', '&hellip;': '__HE__',
    }
    for ent, ph in entities.items():
        if ent in text:
            mapping[ph] = ent
            text = text.replace(ent, ph)
    return text, mapping

def restore(text, mapping):
    for ph, orig in mapping.items():
        text = text.replace(ph, orig)
    return text

# ====================================================================
# Build a comprehensive translation data structure
# Unique texts indexed by their English value
# ====================================================================

# I'll load or generate translations here
# Since I need 1491 unique translations per language × 10 languages = 14910 translations,
# I'll generate them now.

# Strategy: For each unique English text, produce the translation for each language.
# I'll build this as a nested dict: {english_text: {lang_code: translation}}

print("Generating all translations...", file=sys.stderr)

# I'll create the full translation data as a JSON structure
# that maps each language to the complete translation dict
