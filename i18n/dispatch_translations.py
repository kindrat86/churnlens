#!/usr/bin/env python3
"""
Translation dispatch script. Creates all translation input files
and then generates translation instructions per batch.
Run: python3 i18n/dispatch_translations.py
"""
import os, json, sys

I18N_DIR = "/Users/sipi/churnlens/i18n"
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

# Group into batches of ~10 languages
lang_items = list(LANGUAGES.items())
batches = []
batch_size = 10
for i in range(0, len(lang_items), batch_size):
    batches.append(lang_items[i:i+batch_size])

print(f"Total: {len(LANGUAGES)} languages in {len(batches)} batches\n")

for i, batch in enumerate(batches):
    codes = [c for c, n in batch]
    names = [n for c, n in batch]
    print(f"Batch {i+1}: {', '.join(f'{c}({n})' for c,n in batch)}")

# Write each batch's input files
os.makedirs("/tmp/i18n_batches", exist_ok=True)

for i, batch in enumerate(batches):
    batch_dir = f"/tmp/i18n_batches/batch_{i+1}"
    os.makedirs(batch_dir, exist_ok=True)
    
    for code, name in batch:
        input_path = os.path.join(batch_dir, f"input_{code}.txt")
        # Use the translate_batch.py --write-input
        from translate_batch import write_translation_input
        count = write_translation_input(code, name, input_path)
        print(f"  Batch {i+1}: {code} ({name}): {count} segments -> {input_path}")

print("\nAll input files written to /tmp/i18n_batches/")
