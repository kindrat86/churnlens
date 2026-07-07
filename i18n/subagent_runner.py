#!/usr/bin/env python3
"""
Subagent translation runner.
Reads input files from a batch directory and produces translation JSONs.
"""
import os, json, sys

LOCALES_DIR = "/Users/sipi/churnlens/i18n/locales"
PAGE_NAMES = [
    "index", "pricing", "why", "who", "manifesto", "partners",
    "get-the-checklist", "annual-plan-churn-risk", "buying-a-saas-business-guide",
    "churn-lens-for-acquirers-explainer", "customer-concentration-risk",
    "hidden-churn-saas-acquisition", "how-to-evaluate-a-saas-before-buying",
    "inactive-paid-accounts", "logo-retention-churn", "mrr-vs-revenue-quality",
    "saas-acquisition-red-flags", "saas-buyer-risk-assessment",
    "saas-churn-rate-benchmarks", "saas-due-diligence-checklist",
    "saas-mrr-decline-analysis", "saas-revenue-churn-calculator",
    "saas-revenue-concentration-risk", "saas-revenue-quality-score",
    "ultimate-saas-due-diligence-guide"
]

def read_input(path):
    """Read KEY|VALUE input file."""
    data = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('##'):
                continue
            if '|' not in line:
                continue
            k, _, v = line.partition('|')
            k, v = k.strip(), v.strip()
            if k and v:
                data[k] = v
    return data

def group_by_page(data):
    """Group flat translations by page name."""
    pages = {}
    for k, v in data.items():
        if '__TR_' in k:
            pn = k.split('__TR_')[1].split('_')[0]
        else:
            pn = "_unknown"
        pages.setdefault(pn, {})[k] = v
    return pages

def write_locale(lang_code, pages):
    """Write per-page JSON files."""
    out_dir = os.path.join(LOCALES_DIR, lang_code)
    os.makedirs(out_dir, exist_ok=True)
    total = 0
    for pn, data in pages.items():
        path = os.path.join(out_dir, f"{pn}.json")
        existing = {}
        if os.path.exists(path):
            with open(path) as f:
                existing = json.load(f)
        existing.update(data)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
        total += len(existing)
    return total

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

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 runner.py <batch_dir> <lang_codes...>")
        sys.exit(1)
    
    batch_dir = sys.argv[1]
    lang_codes = sys.argv[2:]
    
    for code in lang_codes:
        inp = os.path.join(batch_dir, f"input_{code}.txt")
        if not os.path.exists(inp):
            print(f"Input not found: {inp}")
            continue
        name = get_lang_name(code)
        print(f"\n=== TRANSLATING {code} ({name}) ===")
        
        data = read_input(inp)
        pages = group_by_page(data)
        
        # For each page, output a prompt
        for pn in sorted(pages.keys()):
            items = list(pages[pn].items())
            print(f"\n--- PAGE: {pn} ({len(items)} segments) ---")
            
            # Translate in chunks of 50
            for i in range(0, len(items), 50):
                chunk = items[i:i+50]
                print(f"\n--- CHUNK {i//50+1}/{(len(items)-1)//50+1} ---")
                print(f"Translate to {code} ({name}):")
                print(f"KEY before each | unchanged, translate only the value after |")
                for k, v in chunk:
                    print(f"{k}|{v}")
                print("--- END CHUNK ---")
            
            print(f"--- END PAGE {pn} ---")
        
        print(f"\nAfter translating ALL chunks for {code}, save with:")
        print(f"cd /Users/sipi/churnlens && python3 i18n/ingest_translations.py {code} < translated_{code}.txt")
        print(f"\n--- END LANGUAGE {code} ---")
