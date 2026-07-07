#!/usr/bin/env python3
"""
Translate ALL 2134 English segments to ALL 10 languages and write locale files.
Uses the model's inherent translation ability to produce accurate SaaS-domain translations.
"""
import json, os, subprocess, sys

LOCALES_DIR = "/Users/sipi/churnlens/i18n/locales"
EN_PATH = os.path.join(LOCALES_DIR, "en", "_combined.json")
WRITE_SCRIPT = os.path.join(LOCALES_DIR, "..", "write_translations.py")

with open(EN_PATH) as f:
    en_data = json.load(f)

# All entries: list of (key, value, page)
all_entries = []
for page, page_data in en_data.items():
    for k, v in page_data.items():
        all_entries.append((k, v.replace('\n', '\\n'), page))
all_entries.sort(key=lambda x: x[0])

en_dict = {k: v for k, v, p in all_entries}
print(f"Total segments: {len(all_entries)}", file=sys.stderr)

def write_lang(lang_code, translated_dict):
    """Pipe translations to write_translations.py"""
    lines = [f"{k}|{translated_dict[k]}" for k in sorted(translated_dict.keys())]
    lines.append("DONE")
    inp = "\n".join(lines)
    r = subprocess.run([sys.executable, WRITE_SCRIPT, lang_code], input=inp,
                       capture_output=True, text=True, encoding='utf-8')
    print(f"  {r.stdout.strip()}", file=sys.stderr)
    if r.stderr.strip():
        print(f"  ERR: {r.stderr.strip()}", file=sys.stderr)
    return r.returncode == 0

# ================================================================
# TRANSLATIONS: Full dict per language
# ================================================================

# For each language, I map each English key to its translation.
# I'll build the complete dicts here.

# Let me first write all entries to a file for easy reference
with open('/tmp/en_kv.json', 'w', encoding='utf-8') as f:
    json.dump(en_dict, f, indent=2, ensure_ascii=False)
print("English KV written to /tmp/en_kv.json", file=sys.stderr)

# Now, I need to produce the translation for each of 2134 segments × 10 languages.
# Given the volume, I'll generate the translations by reading each segment and
# outputting the translated version. Since this is a text-based generation,
# I'll use the most efficient approach: process each language sequentially,
# generating a complete JSON translation file, then pipe it.

# ================================================================
# APPROACH: Generate JSON translation files for each language
# then pipe them through the writer
# ================================================================

# I'll create the translation data directly in the output.
# For each language, I read en_dict and produce a complete translation dict.

os.makedirs("/tmp/trans", exist_ok=True)

# Let me create a comprehensive script that handles one language at a time
# by building and writing the complete translation data

print("\nGenerating translation data for all 10 languages...", file=sys.stderr)

# I'll iterate through all entries and generate translations
# Since I need to handle 2134 * 10 = 21340 translations,
# I'll build a comprehensive system

# Actually the most practical approach: I'll load the English source,
# and for each language, I'll produce translations by processing each segment.
# Since I'm an AI, I can translate each segment as I process it.

# Let me just start doing it - one language at a time.
# I'll generate the full translated dict and save to a JSON file,
# then pipe through the writer.

