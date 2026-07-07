#!/usr/bin/env python3
"""
SUBAGENT TRANSLATOR - Run from terminal.
Usage: python3 /Users/sipi/churnlens/i18n/subagent_translate.py <lang_code> \"<lang_name>\"

Reads English source from locales, translates all segments, writes locale files.
Translates in chunks - outputs each chunk as a prompt, then reads the response.

HOW THIS WORKS:
1. The script loads all English segments (2134 keys)
2. It outputs chunks one at a time with TRANSLATION PROMPT markers
3. YOU (the subagent) must provide the translated KEY|VALUE lines after each prompt
4. After all chunks, the script writes the locale JSON files

The '|' character is NOT in any English text, so KEY|VALUE format is safe.
"""
import os, json, sys, re

BASE = "/Users/sipi/churnlens"
LOCALES_DIR = os.path.join(BASE, "i18n", "locales")

def get_lang_name(code):
    names = {
        "zh-CN":"Chinese","hi":"Hindi","es":"Spanish","fr":"French",
        "ar":"Arabic","bn":"Bengali","pt":"Portuguese","ru":"Russian",
        "ur":"Urdu","id":"Indonesian","de":"German","ja":"Japanese",
        "mr":"Marathi","te":"Telugu","tr":"Turkish","ta":"Tamil",
        "vi":"Vietnamese","yue":"Cantonese","pa-PK":"Punjabi",
        "ko":"Korean","fa":"Persian","it":"Italian","th":"Thai",
        "gu":"Gujarati","kn":"Kannada","ml":"Malayalam","or":"Odia",
        "pl":"Polish","uk":"Ukrainian","nl":"Dutch","ro":"Romanian",
        "el":"Greek","cs":"Czech","hu":"Hungarian","sv":"Swedish",
        "fi":"Finnish","no":"Norwegian","da":"Danish","he":"Hebrew",
        "sw":"Swahili","am":"Amharic","so":"Somali","ha":"Hausa",
        "yo":"Yoruba","ig":"Igbo","zu":"Zulu","xh":"Xhosa",
        "af":"Afrikaans","ms":"Malay","my":"Burmese","km":"Khmer",
        "lo":"Lao","ne":"Nepali","si":"Sinhala","ps":"Pashto",
        "kk":"Kazakh","uz":"Uzbek","az":"Azerbaijani","ka":"Georgian",
        "hy":"Armenian","mn":"Mongolian","bo":"Tibetan","ug":"Uyghur",
        "tl":"Tagalog","ceb":"Cebuano","ilo":"Ilocano","jv":"Javanese",
        "su":"Sundanese","mad":"Madurese","hmn":"Hmong","ku":"Kurdish",
        "bal":"Balochi","tg":"Tajik","tk":"Turkmen","sq":"Albanian",
        "sr":"Serbian","hr":"Croatian","bs":"Bosnian","sk":"Slovak",
        "sl":"Slovenian","lt":"Lithuanian","lv":"Latvian","et":"Estonian",
        "be":"Belarusian","bg":"Bulgarian","mk":"Macedonian","ca":"Catalan",
        "eu":"Basque","gl":"Galician","cy":"Welsh","ga":"Irish",
        "gd":"Scottish Gaelic","br":"Breton","is":"Icelandic",
        "lb":"Luxembourgish","mt":"Maltese"
    }
    return names.get(code, code)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 subagent_translate.py <lang_code>")
        print("Example: python3 subagent_translate.py es")
        sys.exit(1)
    
    lang_code = sys.argv[1]
    lang_name = get_lang_name(lang_code)
    
    # Load English source
    en_path = os.path.join(LOCALES_DIR, "en", "_combined.json")
    if not os.path.exists(en_path):
        # Try building combined
        print(f"Building English combined...")
        combined = {}
        en_dir = os.path.join(LOCALES_DIR, "en")
        for fn in sorted(os.listdir(en_dir)):
            if not fn.endswith('.json') or fn == '_combined.json':
                continue
            with open(os.path.join(en_dir, fn), encoding='utf-8') as f:
                combined[fn.replace('.json','')] = json.load(f)
        with open(en_path, 'w', encoding='utf-8') as f:
            json.dump(combined, f, indent=2, ensure_ascii=False)
    
    with open(en_path, encoding='utf-8') as f:
        en_source = json.load(f)
    
    # Flat list of all (key, text) pairs
    all_pairs = []
    for page_name, page_data in en_source.items():
        for key, text in page_data.items():
            all_pairs.append((key, text))
    
    total = len(all_pairs)
    print(f"Translating {total} segments to {lang_code} ({lang_name})")
    
    # Translate in chunks of 100
    chunk_size = 100
    translations = {}
    
    for i in range(0, total, chunk_size):
        chunk = all_pairs[i:i+chunk_size]
        chunk_num = i // chunk_size + 1
        total_chunks = (total + chunk_size - 1) // chunk_size
        
        print(f"\n=== CHUNK {chunk_num}/{total_chunks} ({len(chunk)} segments) ===")
        print(f"Translate to {lang_code} ({lang_name}).")
        print("Format: KEY|TRANSLATED_VALUE (one per line)")
        print("Rules: Keep 'Churn Lens' and 'SaaS' unchanged")
        print("Keep HTML entities: &amp; &lt; &gt; &mdash; &rarr; &times; &copy; &ldquo; &rdquo;")
        print("Output only the KEY|VALUE lines, no explanations.")
        print("---BEGIN CHUNK---")
        for key, text in chunk:
            print(f"{key}|{text}")
        print("---END CHUNK---")
        
        # Read the subagent's response
        # For a terminal-based subagent, this reads stdin
        # The subagent types/pastes the translations
        chunk_translations = {}
        reading = True
        print("\n[Enter translated KEY|VALUE lines, then type 'DONE' on a new line]")
        
        for line in sys.stdin:
            line = line.strip()
            if not line or line.startswith('---'):
                continue
            if line == 'DONE':
                break
            if '|' not in line:
                continue
            k, _, v = line.partition('|')
            k, v = k.strip(), v.strip()
            if k and v:
                chunk_translations[k] = v
        
        translations.update(chunk_translations)
        print(f"  Progress: {len(translations)}/{total}")
    
    if not translations:
        print("ERROR: No translations received!")
        sys.exit(1)
    
    # Group by page and write
    page_data = {}
    for key, val in translations.items():
        pn = key.split('__TR_')[1].split('_')[0] if '__TR_' in key else "_unknown"
        page_data.setdefault(pn, {})[key] = val
    
    out_dir = os.path.join(LOCALES_DIR, lang_code)
    os.makedirs(out_dir, exist_ok=True)
    
    written = 0
    for pn, data in sorted(page_data.items()):
        path = os.path.join(out_dir, f"{pn}.json")
        existing = {}
        if os.path.exists(path):
            with open(path) as f:
                existing = json.load(f)
        existing.update(data)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        written += len(data)
    
    missing = total - len(translations)
    print(f"\n{'='*60}")
    print(f"LANGUAGE {lang_code}: {len(translations)}/{total} translated ({missing} missing)")
    print(f"Saved {written} keys to {out_dir}")
    
    if missing > 0:
        print(f"WARNING: {missing} segments missing. Run again to translate remaining.")

if __name__ == "__main__":
    main()
