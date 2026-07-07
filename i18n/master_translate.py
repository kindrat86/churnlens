#!/usr/bin/env python3
"""
MASTER BATCH TRANSLATOR - Translates ALL remaining languages using Google Translate.
Uses the deep_translator library which is already installed.

This runs ONE process per language and saves locale files.
Usage: python3 i18n/master_translate.py [lang_code1 lang_code2 ...]
       python3 i18n/master_translate.py --all   (translates all 96 non-English languages)
       python3 i18n/master_translate.py it      (just Italian)
"""
import json, sys, time, os, re, subprocess

BASE = "/Users/sipi/churnlens"
LOCALES_DIR = os.path.join(BASE, "i18n", "locales")
KEYS_FILE = os.path.join(BASE, "i18n", "all_keys.txt")
WRITE_SCRIPT = os.path.join(BASE, "i18n", "write_translations.py")
CACHE_DIR = os.path.join(BASE, "i18n", "translation_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

PRESERVE_WORDS = ["Churn Lens", "SaaS"]
PRESERVE_ENTITIES = ["&amp;", "&lt;", "&gt;", "&mdash;", "&rarr;", "&times;", "&copy;", "&ldquo;", "&rdquo;"]

ALL_LANGS = {
    "zh-CN":"Chinese","hi":"Hindi","es":"Spanish","fr":"French","ar":"Arabic",
    "bn":"Bengali","pt":"Portuguese","ru":"Russian","ur":"Urdu","id":"Indonesian",
    "de":"German","ja":"Japanese","mr":"Marathi","te":"Telugu","tr":"Turkish",
    "ta":"Tamil","vi":"Vietnamese","yue":"Cantonese","pa-PK":"Punjabi","ko":"Korean",
    "fa":"Persian","it":"Italian","th":"Thai","gu":"Gujarati","kn":"Kannada",
    "ml":"Malayalam","or":"Odia","pl":"Polish","uk":"Ukrainian","nl":"Dutch",
    "ro":"Romanian","el":"Greek","cs":"Czech","hu":"Hungarian","sv":"Swedish",
    "fi":"Finnish","no":"Norwegian","da":"Danish","he":"Hebrew","sw":"Swahili",
    "am":"Amharic","so":"Somali","ha":"Hausa","yo":"Yoruba","ig":"Igbo",
    "zu":"Zulu","xh":"Xhosa","af":"Afrikaans","ms":"Malay","my":"Burmese",
    "km":"Khmer","lo":"Lao","ne":"Nepali","si":"Sinhala","ps":"Pashto",
    "kk":"Kazakh","uz":"Uzbek","az":"Azerbaijani","ka":"Georgian","hy":"Armenian",
    "mn":"Mongolian","bo":"Tibetan","ug":"Uyghur","tl":"Tagalog","ceb":"Cebuano",
    "ilo":"Ilocano","jv":"Javanese","su":"Sundanese","mad":"Madurese","hmn":"Hmong",
    "ku":"Kurdish","bal":"Balochi","tg":"Tajik","tk":"Turkmen","sq":"Albanian",
    "sr":"Serbian","hr":"Croatian","bs":"Bosnian","sk":"Slovak","sl":"Slovenian",
    "lt":"Lithuanian","lv":"Latvian","et":"Estonian","be":"Belarusian","bg":"Bulgarian",
    "mk":"Macedonian","ca":"Catalan","eu":"Basque","gl":"Galician","cy":"Welsh",
    "ga":"Irish","gd":"Scottish Gaelic","br":"Breton","is":"Icelandic",
    "lb":"Luxembourgish","mt":"Maltese"
}

BATCH_SIZE = 15

def protect_text(text):
    """Replace preserved words/entities with placeholders."""
    ph = {}
    for i, ent in enumerate(PRESERVE_ENTITIES):
        if ent in text:
            tok = f"__EN{i}__"; ph[tok] = ent; text = text.replace(ent, tok)
    for i, w in enumerate(PRESERVE_WORDS):
        if w in text:
            tok = f"__PW{i}__"; ph[tok] = w; text = text.replace(w, tok)
    return text, ph

def restore_text(text, ph):
    for k, v in ph.items():
        text = text.replace(k, v)
    return text

def translate_lang(lc):
    from deep_translator import GoogleTranslator
    print(f"\n{'='*60}")
    print(f"Translating: {lc} ({ALL_LANGS.get(lc, lc)})")
    print(f"{'='*60}")
    
    # Check if already done
    out_dir = os.path.join(LOCALES_DIR, lc)
    existing_keys = 0
    if os.path.exists(out_dir):
        for fn in os.listdir(out_dir):
            if fn.endswith('.json') and fn != '_combined.json':
                with open(os.path.join(out_dir, fn)) as f:
                    existing_keys += len(json.load(f))
    if existing_keys >= 2134:
        print(f"  Already complete ({existing_keys} keys)")
        return True
    
    # Read all keys
    with open(KEYS_FILE) as f:
        lines = [l.strip() for l in f if l.strip()]
    total = len(lines)
    
    # Load cache
    cache_file = os.path.join(CACHE_DIR, f"{lc}.jsonl")
    cache = {}
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            for l in f:
                if '|' in l:
                    k, v = l.strip().split('|', 1)
                    cache[k] = v
        print(f"  Cache: {len(cache)} entries")
    
    # Determine what needs translation
    to_translate = []
    for idx, line in enumerate(lines):
        if '|' not in line:
            continue
        k, v = line.split('|', 1)
        if k not in cache:
            to_translate.append((k, v))
    
    if not to_translate:
        print(f"  All cached! Writing files...")
    else:
        print(f"  Need to translate: {len(to_translate)} / {total}")
    
    # Translate
    translator = GoogleTranslator(source="en", target=lc)
    new_translations = dict(cache)
    
    for batch_start in range(0, len(to_translate), BATCH_SIZE):
        batch = to_translate[batch_start:batch_start + BATCH_SIZE]
        
        protected = []
        ph_list = []
        for k, v in batch:
            pv, ph = protect_text(v)
            protected.append(pv)
            ph_list.append(ph)
        
        for attempt in range(3):
            try:
                results = translator.translate_batch(protected)
                break
            except Exception as e:
                if attempt < 2:
                    print(f"  Retry batch {batch_start}: {e}")
                    time.sleep(3)
                else:
                    print(f"  FAILED batch {batch_start}: {e}")
                    results = protected
        
        for (k, v), ph, translated in zip(batch, ph_list, results):
            if translated is None:
                translated = v
            else:
                translated = restore_text(translated, ph)
            new_translations[k] = translated
            with open(cache_file, 'a') as cf:
                cf.write(f"{k}|{translated}\n")
        
        done = min(batch_start + BATCH_SIZE, len(to_translate))
        if batch_start % (BATCH_SIZE * 4) == 0 or done >= len(to_translate):
            pct = done / max(1, len(to_translate)) * 100
            print(f"  Progress: {done}/{len(to_translate)} ({pct:.0f}%)")
        
        time.sleep(0.35)
    
    # Write locale files
    print(f"  Writing {len(new_translations)} translations...")
    proc = subprocess.Popen(
        ["python3", WRITE_SCRIPT, lc],
        stdin=subprocess.PIPE, text=True
    )
    for k, v in new_translations.items():
        proc.stdin.write(f"{k}|{v}\n")
    proc.stdin.write("DONE\n")
    proc.stdin.close()
    proc.wait()
    
    # Verify
    written = 0
    for fn in os.listdir(out_dir):
        if fn.endswith('.json') and fn != '_combined.json':
            with open(os.path.join(out_dir, fn)) as f:
                written += len(json.load(f))
    
    if written >= 2134:
        print(f"  COMPLETE: {written} keys for {lc}")
        return True
    else:
        print(f"  PARTIAL: {written}/{total} keys for {lc}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 master_translate.py [--all | lang_code1 lang_code2 ...]")
        sys.exit(1)
    
    target_langs = []
    if sys.argv[1] == '--all':
        target_langs = list(ALL_LANGS.keys())
    else:
        target_langs = sys.argv[1:]
    
    print(f"Translating {len(target_langs)} languages")
    ok = 0
    fail = 0
    
    for lc in target_langs:
        try:
            if translate_lang(lc):
                ok += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ERROR translating {lc}: {e}")
            fail += 1
        time.sleep(1.5)
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {ok} OK, {fail} FAILED out of {len(target_langs)}")

if __name__ == "__main__":
    main()
