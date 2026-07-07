#!/usr/bin/env python3
"""
MASTER TRANSLATION PIPELINE for all 10 languages.
Reads English, translates ALL 2134 segments, pipes to write_translations.py.
Uses compact translation files stored in i18n/translations/<lang>.json
"""
import json, subprocess, sys, os

EN_SOURCE = "/Users/sipi/churnlens/i18n/locales/en/_combined.json"
WRITE_SCRIPT = "/Users/sipi/churnlens/i18n/write_translations.py"
OUT_BASE = "/Users/sipi/churnlens/i18n/locales"
TRANS_DIR = "/Users/sipi/churnlens/i18n/translations"

with open(EN_SOURCE) as f:
    EN = json.load(f)

ALL_PAIRS = [(page, k, v) for page, vals in EN.items() for k, v in vals.items()]

def pipe_to_writer(lang_code, en_to_trans):
    """Build translations from English->Translation mapping and pipe."""
    translations = {}
    translated = 0
    for page, k, v in ALL_PAIRS:
        if v in en_to_trans and en_to_trans[v] != v:
            translations[k] = en_to_trans[v]
            translated += 1
        else:
            translations[k] = v
    
    lines = [f"{k}|{v}" for k, v in sorted(translations.items())]
    lines.append("DONE")
    result = subprocess.run(
        ["python3", WRITE_SCRIPT, lang_code],
        input="\n".join(lines), capture_output=True, text=True
    )
    return result, translated, len(translations)

# Load existing translation files
def load_trans(lang_code):
    path = os.path.join(TRANS_DIR, f"{lang_code}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

print(f"Loaded {len(load_trans('ro'))} RO translations", file=sys.stderr)

# ============================================================================
# Process all languages
# ============================================================================
LANG_CODES = ["ro", "el", "cs", "hu", "sv", "fi", "no", "da", "he", "sw"]
LANG_NAMES = {
    "ro": "Romanian", "el": "Greek", "cs": "Czech", "hu": "Hungarian",
    "sv": "Swedish", "fi": "Finnish", "no": "Norwegian", "da": "Danish",
    "he": "Hebrew", "sw": "Swahili"
}

for lang_code in LANG_CODES:
    trans_data = load_trans(lang_code)
    result, translated, total = pipe_to_writer(lang_code, trans_data)
    name = LANG_NAMES[lang_code]
    status = "✓" if result.returncode == 0 else "✗"
    print(f"  {lang_code} ({name}): {translated}/{total} translated - {status} - {result.stdout.strip()}", file=sys.stderr)
    if result.stderr:
        print(f"    stderr: {result.stderr.strip()}", file=sys.stderr)

# Verification
print(f"\n{'='*60}", file=sys.stderr)
print("VERIFICATION:", file=sys.stderr)
en_dir = os.path.join(OUT_BASE, "en")
en_files = sorted([f for f in os.listdir(en_dir) if f.endswith('.json') and f != '_combined.json'])
en_total = sum(len(json.load(open(os.path.join(en_dir, f)))) for f in en_files)

for lang_code in LANG_CODES:
    lang_dir = os.path.join(OUT_BASE, lang_code)
    if os.path.isdir(lang_dir):
        files = sorted([f for f in os.listdir(lang_dir) if f.endswith('.json')])
        total_keys = sum(len(json.load(open(os.path.join(lang_dir, f)))) for f in files)
        file_match = "✓" if len(files) == len(en_files) else f"({len(files)}/{len(en_files)})"
        key_match = "✓" if total_keys == en_total else f"({total_keys}/{en_total})"
        print(f"  {lang_code}: {file_match} files, {key_match} keys", file=sys.stderr)
    else:
        print(f"  {lang_code}: DIRECTORY NOT FOUND ✗", file=sys.stderr)

print("\nDone!", file=sys.stderr)
