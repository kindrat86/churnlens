#!/usr/bin/env python3
"""
Create batch instruction files for subagent delegations.
Each file contains the English source texts for ~10 languages.
"""
import os, json, sys

BASE = "/Users/sipi/churnlens"
I18N_DIR = os.path.join(BASE, "i18n")
LOCALES_DIR = os.path.join(I18N_DIR, "locales")

LANGUAGES = {
    "zh-CN": "Mandarin Chinese", "hi": "Hindi", "es": "Spanish", "fr": "French",
    "ar": "Arabic", "bn": "Bengali", "pt": "Portuguese", "ru": "Russian",
    "ur": "Urdu", "id": "Indonesian", "de": "German", "ja": "Japanese",
    "mr": "Marathi", "te": "Telugu", "tr": "Turkish", "ta": "Tamil",
    "vi": "Vietnamese", "yue": "Cantonese", "pa-PK": "Western Punjabi",
    "ko": "Korean", "fa": "Persian", "it": "Italian", "th": "Thai",
    "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam", "or": "Odia",
    "pl": "Polish", "uk": "Ukrainian", "nl": "Dutch", "ro": "Romanian",
    "el": "Greek", "cs": "Czech", "hu": "Hungarian", "sv": "Swedish",
    "fi": "Finnish", "no": "Norwegian", "da": "Danish", "he": "Hebrew",
    "sw": "Swahili", "am": "Amharic", "so": "Somali", "ha": "Hausa",
    "yo": "Yoruba", "ig": "Igbo", "zu": "Zulu", "xh": "Xhosa",
    "af": "Afrikaans", "ms": "Malay", "my": "Burmese", "km": "Khmer",
    "lo": "Lao", "ne": "Nepali", "si": "Sinhala", "ps": "Pashto",
    "kk": "Kazakh", "uz": "Uzbek", "az": "Azerbaijani", "ka": "Georgian",
    "hy": "Armenian", "mn": "Mongolian", "bo": "Tibetan", "ug": "Uyghur",
    "tl": "Tagalog", "ceb": "Cebuano", "ilo": "Ilocano", "jv": "Javanese",
    "su": "Sundanese", "mad": "Madurese", "hmn": "Hmong", "ku": "Kurdish",
    "bal": "Balochi", "tg": "Tajik", "tk": "Turkmen", "sq": "Albanian",
    "sr": "Serbian", "hr": "Croatian", "bs": "Bosnian", "sk": "Slovak",
    "sl": "Slovenian", "lt": "Lithuanian", "lv": "Latvian", "et": "Estonian",
    "be": "Belarusian", "bg": "Bulgarian", "mk": "Macedonian", "ca": "Catalan",
    "eu": "Basque", "gl": "Galician", "cy": "Welsh", "ga": "Irish",
    "gd": "Scottish Gaelic", "br": "Breton", "is": "Icelandic",
    "lb": "Luxembourgish", "mt": "Maltese"
}

# Group into batches
items = list(LANGUAGES.items())
batches = []
batch_size = 10
for i in range(0, len(items), batch_size):
    batches.append(items[i:i+batch_size])

print(f"Total: {len(LANGUAGES)} languages in {len(batches)} batches\n")

# For each batch, create a combined file with English source
# and a list of target languages

for bi, batch in enumerate(batches):
    lang_codes = [c for c, n in batch]
    lang_names = [n for c, n in batch]
    
    # Write the batch instruction file
    out_path = f"/tmp/i18n_batches/batch_{bi+1}/instructions.txt"
    
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"BATCH {bi+1}: {len(batch)} languages\n")
        f.write("Languages to translate:\n")
        for code, name in batch:
            f.write(f"  {code} - {name}\n")
        f.write(f"\nFor each language above, translate ALL the English segments below.\n")
        f.write("Save translations to: /Users/sipi/churnlens/i18n/locales/<lang_code>/\n")
        f.write("\n")
    
    print(f"Batch {bi+1}: {', '.join(f'{c}({n})' for c,n in batch)}")
    
    # Write lang codes file
    codes_path = f"/tmp/i18n_batches/batch_{bi+1}/lang_codes.txt"
    with open(codes_path, 'w', encoding='utf-8') as f:
        for code in lang_codes:
            f.write(f"{code}\n")
    
    # Write per-language input files
    for code, name in batch:
        input_path = f"/tmp/i18n_batches/batch_{bi+1}/input_{code}.txt"
        f = open(input_path, 'w', encoding='utf-8')
        print(f"  Preparing {code} ({name})...", file=sys.stderr)

print(f"\nPrepared all batch instruction files in /tmp/i18n_batches/")
