#!/usr/bin/env python3
"""
Self-contained translation worker for i18n batches.
Reads input files, generates output locale JSON files.

Usage: python3 i18n/translate_worker.py <batch_dir> <lang_codes...>
Example: python3 i18n/translate_worker.py /tmp/i18n_batches/batch_1 zh-CN hi es fr ar bn pt ru ur id

The script reads each lang's input file and outputs translation prompts.
The subagent should run this script repeatedly until all languages are done.

Actually, the simpler approach: this script just produces the prompts,
the subagent writes the outputs.
"""

import os, json, sys, re

I18N_DIR = "/Users/sipi/churnlens/i18n"
LOCALES_DIR = os.path.join(I18N_DIR, "locales")

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

def get_lang_name(code):
    """Get a human-readable language name from code."""
    names = {
        "zh-CN": "Mandarin Chinese", "hi": "Hindi", "es": "Spanish",
        "fr": "French", "ar": "Arabic", "bn": "Bengali", "pt": "Portuguese",
        "ru": "Russian", "ur": "Urdu", "id": "Indonesian", "de": "German",
        "ja": "Japanese", "mr": "Marathi", "te": "Telugu", "tr": "Turkish",
        "ta": "Tamil", "vi": "Vietnamese", "yue": "Cantonese",
        "pa-PK": "Western Punjabi", "ko": "Korean", "fa": "Persian",
        "it": "Italian", "th": "Thai", "gu": "Gujarati", "kn": "Kannada",
        "ml": "Malayalam", "or": "Odia", "pl": "Polish", "uk": "Ukrainian",
        "nl": "Dutch", "ro": "Romanian", "el": "Greek", "cs": "Czech",
        "hu": "Hungarian", "sv": "Swedish", "fi": "Finnish", "no": "Norwegian",
        "da": "Danish", "he": "Hebrew", "sw": "Swahili", "am": "Amharic",
        "so": "Somali", "ha": "Hausa", "yo": "Yoruba", "ig": "Igbo",
        "zu": "Zulu", "xh": "Xhosa", "af": "Afrikaans", "ms": "Malay",
        "my": "Burmese", "km": "Khmer", "lo": "Lao", "ne": "Nepali",
        "si": "Sinhala", "ps": "Pashto", "kk": "Kazakh", "uz": "Uzbek",
        "az": "Azerbaijani", "ka": "Georgian", "hy": "Armenian",
        "mn": "Mongolian", "bo": "Tibetan", "ug": "Uyghur", "tl": "Tagalog",
        "ceb": "Cebuano", "ilo": "Ilocano", "jv": "Javanese",
        "su": "Sundanese", "mad": "Madurese", "hmn": "Hmong", "ku": "Kurdish",
        "bal": "Balochi", "tg": "Tajik", "tk": "Turkmen", "sq": "Albanian",
        "sr": "Serbian", "hr": "Croatian", "bs": "Bosnian", "sk": "Slovak",
        "sl": "Slovenian", "lt": "Lithuanian", "lv": "Latvian",
        "et": "Estonian", "be": "Belarusian", "bg": "Bulgarian",
        "mk": "Macedonian", "ca": "Catalan", "eu": "Basque", "gl": "Galician",
        "cy": "Welsh", "ga": "Irish", "gd": "Scottish Gaelic", "br": "Breton",
        "is": "Icelandic", "lb": "Luxembourgish", "mt": "Maltese"
    }
    return names.get(code, code)

def read_input_file(path):
    """Read an input file and return dict of {key: english_text}."""
    result = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '|' not in line:
                continue
            key, _, val = line.partition('|')
            key = key.strip()
            val = val.strip()
            if key and val:
                result[key] = val
    return result

def write_locale_files(lang_code, translations, output_base):
    """Write per-page JSON locale files from a flat {key: translated} dict."""
    output_dir = os.path.join(output_base, lang_code)
    os.makedirs(output_dir, exist_ok=True)
    
    # Group by page
    page_data = {}
    for key, val in translations.items():
        if '__TR_' in key:
            page_name = key.split('__TR_')[1].split('_')[0]
        else:
            page_name = "_unknown"
        if page_name not in page_data:
            page_data[page_name] = {}
        page_data[page_name][key] = val
    
    total = 0
    for page_name, data in page_data.items():
        out_path = os.path.join(output_dir, f"{page_name}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        total += len(data)
    
    print(f"  Wrote {total} translations to {output_dir}")
    return total

def translate_lang_via_prompt(code, name, input_path):
    """
    Read the input file and produce a prompt asking for ALL translations.
    Since 2134 segments is too large, we split into chunks.
    """
    data = read_input_file(input_path)
    keys = list(data.keys())
    
    print(f"\n{'='*70}")
    print(f"LANGUAGE: {code} ({name}) — {len(keys)} segments to translate")
    print(f"{'='*70}")
    
    # Split into chunks of ~200 segments each
    chunk_size = 200
    for i in range(0, len(keys), chunk_size):
        chunk_keys = keys[i:i+chunk_size]
        chunk_data = {k: data[k] for k in chunk_keys}
        
        # Print the translation prompt for this chunk
        print(f"\n--- CHUNK {i//chunk_size + 1}/{(len(keys)-1)//chunk_size + 1} ({len(chunk_keys)} segments) ---")
        print(f"Translate the following {len(chunk_keys)} text segments to {code} ({name}).")
        print("Rules:")
        print("  - Keep brand names 'Churn Lens' and 'SaaS' unchanged")
        print("  - Keep HTML entities like &amp; &lt; &gt; &mdash; &rarr; &times; &copy; unchanged")
        print("  - Keep the KEY part before each | exactly as-is")
        print("  - Only translate the VALUE after the |")
        print("  - Output each line as: KEY|TRANSLATED_VALUE")
        print("  - Do not include ANY explanations, just the translated KEY|VALUE lines")
        print("")
        
        for key in chunk_keys:
            val = data[key].replace('\n', '\\n')
            print(f"{key}|{val}")
        
        print(f"--- END CHUNK {i//chunk_size + 1} ---")
    
    print(f"\n--- END LANGUAGE {code} ---")
    print(f"After translating all chunks, run: python3 /Users/sipi/churnlens/i18n/ingest_translations.py {code}")

def write_ingest_script():
    """Write the ingest script that the subagent can use after translating."""
    pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 i18n/translate_worker.py <lang_codes...>")
        sys.exit(1)
    
    batch_base = "/tmp/i18n_batches"
    
    for code in sys.argv[1:]:
        input_path = os.path.join(batch_base, f"input_{code}.txt")
        if not os.path.exists(input_path):
            # Try all batch dirs
            for b in range(1, 11):
                p = os.path.join(batch_base, f"batch_{b}", f"input_{code}.txt")
                if os.path.exists(p):
                    input_path = p
                    break
        
        name = get_lang_name(code)
        if os.path.exists(input_path):
            translate_lang_via_prompt(code, name, input_path)
        else:
            print(f"Input file not found for {code} ({name})")
