#!/usr/bin/env python3
"""
Efficient batch translator - sends all 2134 segments together for translation.
Uses GoogleTranslator via deep_translator but with persistent session.
"""

import json
import sys
import time
import os
import re

LOCALES_DIR = "/Users/sipi/churnlens/i18n/locales"
KEYS_FILE = "/Users/sipi/churnlens/i18n/all_keys.txt"
WRITE_SCRIPT = "/Users/sipi/churnlens/i18n/write_translations.py"
CACHE_DIR = "/Users/sipi/churnlens/i18n/translation_cache"

os.makedirs(CACHE_DIR, exist_ok=True)

# Preserve tokens
PRESERVE_WORDS = ["Churn Lens", "SaaS"]
PRESERVE_ENTITIES = ["&amp;", "&lt;", "&gt;", "&mdash;", "&rarr;", "&times;", "&copy;"]

ALL_LANGS = {
    "fa": "Persian (Farsi)",
    "it": "Italian",
    "th": "Thai",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "or": "Odia",
    "pl": "Polish",
    "uk": "Ukrainian",
    "nl": "Dutch",
}

def protect_text(text):
    """Replace preserved words/entities with placeholders."""
    placeholders = {}
    
    # Replace {{variables}}
    curly_vars = re.findall(r'\{\{[^}]+\}\}', text)
    for i, cv in enumerate(curly_vars):
        ph = f"__CURLY_{i}__"
        placeholders[ph] = cv
        text = text.replace(cv, ph, 1)
    
    # Replace preserved entities
    for i, ent in enumerate(PRESERVE_ENTITIES):
        if ent in text:
            ph = f"__ENT_{i}__"
            placeholders[ph] = ent
            text = text.replace(ent, ph)
    
    # Replace preserved words
    for i, word in enumerate(PRESERVE_WORDS):
        if word in text:
            ph = f"__PRSV_{i}__"
            placeholders[ph] = word
            text = text.replace(word, ph)
    
    return text, placeholders


def restore_text(text, placeholders):
    """Restore placeholders back to original text."""
    for ph, original in placeholders.items():
        text = text.replace(ph, original)
    return text


def translate_language_optimized(lang_code):
    """Translate using batched approach with persistent translator."""
    print(f"\n{'='*60}")
    print(f"Translating to {lang_code} ({ALL_LANGS.get(lang_code, 'Unknown')})")
    print(f"{'='*60}")
    
    # Read all key|value lines
    with open(KEYS_FILE) as f:
        lines = [line.strip() for line in f if line.strip()]
    
    total = len(lines)
    
    # Check for existing cache
    cache_file = os.path.join(CACHE_DIR, f"{lang_code}.jsonl")
    cached = {}
    if os.path.exists(cache_file):
        with open(cache_file) as cf:
            for cl in cf:
                cl = cl.strip()
                if "|" in cl:
                    k, v = cl.split("|", 1)
                    cached[k] = v
        print(f"Loaded {len(cached)} cached translations for {lang_code}")
    
    # Check for existing output - see what's already been written
    out_dir = os.path.join(LOCALES_DIR, lang_code)
    existing_keys = set()
    if os.path.exists(out_dir):
        for fn in os.listdir(out_dir):
            if fn.endswith(".json"):
                with open(os.path.join(out_dir, fn)) as f:
                    data = json.load(f)
                    existing_keys.update(data.keys())
    
    # Create translator instance (persistent session)
    from deep_translator import GoogleTranslator
    translator = GoogleTranslator(source="en", target=lang_code)
    
    results = []
    new_count = 0
    cached_count = 0
    error_count = 0
    batch_buffer = []  # Accumulate lines for batch writing
    
    # Process in chunks, checkpointing frequently
    for idx, line in enumerate(lines):
        if "|" not in line:
            continue
        
        key, value = line.split("|", 1)
        
        # Skip if already translated and cached
        if key in cached:
            results.append((key, cached[key]))
            cached_count += 1
            continue
        
        # Skip if already in output files
        if key in existing_keys:
            # Add to cache too
            with open(cache_file, "a") as cf:
                # We need the value from existing...
                pass
            cached_count += 1
            continue
        
        # Protect special tokens
        protected_text, placeholders = protect_text(value)
        
        # Translate
        try:
            if not protected_text.strip():
                translated = value
            else:
                translated = translator.translate(protected_text)
                if translated is None:
                    translated = value
            
            # Restore placeholders
            translated = restore_text(translated, placeholders)
            results.append((key, translated))
            new_count += 1
            
            # Cache it
            with open(cache_file, "a") as cf:
                cf.write(f"{key}|{translated}\n")
            
        except Exception as e:
            # Fall back to original
            results.append((key, value))
            error_count += 1
            if new_count % 10 == 0:
                print(f"  [WARN] at idx {idx} ({key[:40]}): {e}", file=sys.stderr)
        
        # Progress
        if (idx + 1) % 100 == 0:
            pct = (idx + 1) / total * 100
            print(f"  Progress: {idx+1}/{total} ({pct:.1f}%) - new:{new_count} cached:{cached_count} errors:{error_count}")
        
        # Rate limit
        if (idx + 1) % 10 == 0:
            time.sleep(0.5)
    
    print(f"\nTranslation complete: {new_count} new, {cached_count} cached, {error_count} errors")
    
    # Now write all results using the write_translations.py script
    print(f"Writing {len(results)} translations to locale files via write_translations.py...")
    
    # Write to stdin of write_translations.py
    import subprocess
    proc = subprocess.Popen(
        ["python3", WRITE_SCRIPT, lang_code],
        stdin=subprocess.PIPE,
        text=True
    )
    
    for key, val in results:
        proc.stdin.write(f"{key}|{val}\n")
    
    proc.stdin.write("DONE\n")
    proc.stdin.flush()
    proc.stdin.close()
    proc.wait()
    
    print(f"Written {len(results)} keys for {lang_code}")
    return new_count, cached_count, error_count


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if target == "all":
        for lc in ALL_LANGS:
            t, c, e = translate_language_optimized(lc)
            print(f"\n  {lc}: {t} new, {c} cached, {e} errors")
            time.sleep(3)  # Cooldown
    else:
        translate_language_optimized(target)
