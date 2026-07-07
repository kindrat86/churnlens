#!/usr/bin/env python3
"""
Fast batch translator using translate_batch with optimal batch sizing.
Runs one language at a time with checkpointing.
"""
import json, sys, time, os, re, subprocess

LOCALES_DIR = "/Users/sipi/churnlens/i18n/locales"
KEYS_FILE = "/Users/sipi/churnlens/i18n/all_keys.txt"
WRITE_SCRIPT = "/Users/sipi/churnlens/i18n/write_translations.py"
CACHE_DIR = "/Users/sipi/churnlens/i18n/translation_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

PRESERVE_WORDS = ["Churn Lens", "SaaS"]
PRESERVE_ENTITIES = ["&amp;", "&lt;", "&gt;", "&mdash;", "&rarr;", "&times;", "&copy;"]

ALL_LANGS = {
    "fa": "Persian (Farsi)", "it": "Italian", "th": "Thai",
    "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam",
    "or": "Odia", "pl": "Polish", "uk": "Ukrainian", "nl": "Dutch",
}

BATCH_SIZE = 15  # Safe batch size for reliability

def protect(text):
    """Replace preserved tokens with placeholders."""
    ph = {}
    for i, cv in enumerate(re.findall(r'\{\{[^}]+\}\}', text)):
        tok = f"__CV_{i}__"; ph[tok] = cv; text = text.replace(cv, tok, 1)
    for i, ent in enumerate(PRESERVE_ENTITIES):
        if ent in text:
            tok = f"__EN_{i}__"; ph[tok] = ent; text = text.replace(ent, tok)
    for i, w in enumerate(PRESERVE_WORDS):
        if w in text:
            tok = f"__PW_{i}__"; ph[tok] = w; text = text.replace(w, tok)
    return text, ph

def restore(text, ph):
    for k, v in ph.items(): text = text.replace(k, v)
    return text

def translate_lang(lc):
    from deep_translator import GoogleTranslator
    print(f"\n=== Translating {lc} ===")
    
    with open(KEYS_FILE) as f:
        lines = [l.strip() for l in f if l.strip()]
    total = len(lines)
    
    # Load cache
    cache_file = os.path.join(CACHE_DIR, f"{lc}.jsonl")
    cache = {}
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            for l in f:
                if "|" in l:
                    k, v = l.strip().split("|", 1)
                    cache[k] = v
        print(f"  Cache: {len(cache)} entries")
    
    # Check existing files
    out_dir = os.path.join(LOCALES_DIR, lc)
    existing = set()
    if os.path.exists(out_dir):
        for fn in os.listdir(out_dir):
            if fn.endswith(".json"):
                with open(os.path.join(out_dir, fn)) as f:
                    existing.update(json.load(f).keys())
        print(f"  Existing files: {len(existing)} keys")
    
    to_translate = []
    for idx, line in enumerate(lines):
        if "|" not in line: continue
        k, v = line.split("|", 1)
        if k not in cache and k not in existing:
            to_translate.append((idx, k, v))
    
    print(f"  Need to translate: {len(to_translate)} / {total}")
    
    if not to_translate:
        print(f"  All already translated!")
        return
    
    # Translate in batches
    translator = GoogleTranslator(source="en", target=lc)
    new_translations = {}
    
    # First, load existing cache entries
    for k, v in cache.items():
        new_translations[k] = v
    
    for batch_start in range(0, len(to_translate), BATCH_SIZE):
        batch = to_translate[batch_start:batch_start + BATCH_SIZE]
        
        # Protect texts
        protected = []
        originals = []
        placeholders_list = []
        
        for idx, k, v in batch:
            pv, ph = protect(v)
            protected.append(pv)
            originals.append((idx, k, v))
            placeholders_list.append(ph)
        
        # Translate
        max_retries = 3
        for attempt in range(max_retries):
            try:
                results = translator.translate_batch(protected)
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"  Batch fail at {batch_start}: {e}")
                    results = protected  # fallback to original
        
        # Restore and cache
        for (idx, k, v), ph, translated in zip(originals, placeholders_list, results):
            if translated is None:
                translated = v
            else:
                translated = restore(translated, ph)
            new_translations[k] = translated
            # Write to cache immediately
            with open(cache_file, "a") as cf:
                cf.write(f"{k}|{translated}\n")
        
        # Progress
        done = min(batch_start + BATCH_SIZE, len(to_translate))
        pct = done / len(to_translate) * 100
        if batch_start % (BATCH_SIZE * 3) == 0 or done == len(to_translate):
            print(f"  Batch: {done}/{len(to_translate)} ({pct:.0f}%)")
        
        time.sleep(0.3)
    
    # Now write all results
    print(f"  Writing {len(new_translations)} translations to locale files...")
    proc = subprocess.Popen(["python3", WRITE_SCRIPT, lc], stdin=subprocess.PIPE, text=True)
    for k, v in new_translations.items():
        proc.stdin.write(f"{k}|{v}\n")
    proc.stdin.write("DONE\n")
    proc.stdin.close()
    proc.wait()
    print(f"  Done! Written {len(new_translations)} keys for {lc}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    if target == "all":
        for lc in ALL_LANGS:
            translate_lang(lc)
            time.sleep(2)
    else:
        translate_lang(target)
