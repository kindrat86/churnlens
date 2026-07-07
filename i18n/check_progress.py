#!/usr/bin/env python3
"""
Smart batching dispatch - sends out remaining batches one at a time.
"""
import os, json, sys

BASE = "/Users/sipi/churnlens"
LOCALES_DIR = os.path.join(BASE, "i18n", "locales")

# All languages still needing translation
REMAINING_LANGUAGES = {
    "ro": "Romanian", "el": "Greek", "cs": "Czech", "hu": "Hungarian",
    "sv": "Swedish", "fi": "Finnish", "no": "Norwegian", "da": "Danish",
    "he": "Hebrew", "sw": "Swahili",
    "am": "Amharic", "so": "Somali", "ha": "Hausa", "yo": "Yoruba",
    "ig": "Igbo", "zu": "Zulu", "xh": "Xhosa", "af": "Afrikaans",
    "ms": "Malay", "my": "Burmese",
    "km": "Khmer", "lo": "Lao", "ne": "Nepali", "si": "Sinhala",
    "ps": "Pashto", "kk": "Kazakh", "uz": "Uzbek", "az": "Azerbaijani",
    "ka": "Georgian", "hy": "Armenian",
    "mn": "Mongolian", "bo": "Tibetan", "ug": "Uyghur",
    "tl": "Tagalog", "ceb": "Cebuano", "ilo": "Ilocano",
    "jv": "Javanese", "su": "Sundanese", "mad": "Madurese", "hmn": "Hmong",
    "ku": "Kurdish", "bal": "Balochi", "tg": "Tajik", "tk": "Turkmen",
    "sq": "Albanian", "sr": "Serbian", "hr": "Croatian", "bs": "Bosnian",
    "sk": "Slovak", "sl": "Slovenian",
    "lt": "Lithuanian", "lv": "Latvian", "et": "Estonian",
    "be": "Belarusian", "bg": "Bulgarian", "mk": "Macedonian",
    "ca": "Catalan", "eu": "Basque", "gl": "Galician", "cy": "Welsh",
    "ga": "Irish", "gd": "Scottish Gaelic", "br": "Breton",
    "is": "Icelandic", "lb": "Luxembourgish", "mt": "Maltese"
}

def check_completed():
    """Check which languages already have locale files."""
    completed = set()
    for d in sorted(os.listdir(LOCALES_DIR)):
        dpath = os.path.join(LOCALES_DIR, d)
        if not os.path.isdir(dpath) or d.startswith('.') or d == 'en':
            continue
        combined = os.path.join(dpath, "_combined.json")
        if os.path.exists(combined):
            with open(combined) as f:
                data = json.load(f)
            total = sum(len(v) for v in data.values())
            if total >= 2000:  # Good enough
                completed.add(d)
                print(f"  COMPLETED: {d} ({total} keys)")
    return completed

if __name__ == "__main__":
    completed = check_completed()
    remaining = {k: v for k, v in REMAINING_LANGUAGES.items() if k not in completed}
    print(f"\nRemaining: {len(remaining)} languages: {', '.join(remaining.keys())}")
    
    # Print the batches for reference
    items = list(remaining.items())
    for i in range(0, len(items), 10):
        batch = items[i:i+10]
        codes = [c for c, n in batch]
        print(f"Batch {i//10 + 1}: {', '.join(codes)}")
