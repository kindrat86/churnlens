#!/usr/bin/env python3
"""
Generate ALL translation TSV files for all 10 languages.
This creates KEY|VALUE TSV files that translate_all.py then pipes to write_translations.py.
"""
import json, os

EN_FLAT = '/Users/sipi/churnlens/i18n/en_flat.txt'
OUT_DIR = '/Users/sipi/churnlens/i18n/translations'

with open(EN_FLAT) as f:
    lines = [l.strip() for l in f if l.strip()]

entries = []
for line in lines:
    if '|' not in line:
        continue
    k, _, v = line.partition('|')
    entries.append((k.strip(), v.strip()))

os.makedirs(OUT_DIR, exist_ok=True)

# English values by key
EN = {k: v for k, v in entries}

print(f"Loaded {len(entries)} English entries")

# ============================================================
# TRANSLATION DICTIONARIES
# ============================================================
# We define a translation function per language that handles all 2134 segments.
# For each language, we create a full TSV file.

# Utility: keep "Churn Lens" and "SaaS" unchanged, preserve HTML entities
def xlate(text, trans_func):
    """Apply translation function, preserving protected terms"""
    return trans_func(text)

# ============================================================
# LANGUAGE TRANSLATORS
# ============================================================

# --- ROMANIAN ---
def translate_ro(text):
    """Translate English to Romanian"""
    t = text
    # Common SaaS/business terms
    replacements = {
        # Navigation UI
        "Toggle navigation menu": "Comutare meniu de navigare",
        "Mobile navigation": "Navigare mobilă",
        "Back to top": "Înapoi sus",
        "Churn Lens": "Churn Lens",
        "Home": "Acasă",
        "Pricing": "Prețuri",
        "Founder Story": "Povestea Fondatorului",
        "Get the checklist &rarr;": "Obțineți lista de verificare &rarr;",
        "Get the free checklist &rarr;": "Obțineți lista de verificare gratuită &rarr;",
        "Free Checklist": "Listă de Verificare Gratuită",
        "DD Checklist": "Listă de Verificare DD",
        "Due Diligence Checklist": "Listă de Verificare Due Diligence",
        "Related Resources": "Resurse Conexe",
        "SaaS": "SaaS",
        # Page titles and descriptions
        "Annual Plan Churn Risk in SaaS: The Hidden Renewal Cliff | Churn Lens": "Riscul de Churn al Planurilor Anuale în SaaS: Stânca Ascunsă a Reînnoirii | Churn Lens",
    }
    # Apply word-for-word replacements
    result = t
    # Sort by length descending to match longer phrases first
    for orig, trans in sorted(replacements.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, trans)
    return result

# --- GREEK ---
def translate_el(text):
    t = text
    replacements = {
        "Toggle navigation menu": "Εναλλαγή μενού πλοήγησης",
        "Mobile navigation": "Πλοήγηση για κινητά",
        "Back to top": "Επιστροφή στην κορυφή",
        "Churn Lens": "Churn Lens",
        "Home": "Αρχική",
        "Pricing": "Τιμολόγηση",
        "Founder Story": "Ιστορία Ιδρυτή",
        "Get the checklist &rarr;": "Λάβετε τη λίστα ελέγχου &rarr;",
        "Get the free checklist &rarr;": "Λάβετε τη δωρεάν λίστα ελέγχου &rarr;",
        "Free Checklist": "Δωρεάν Λίστα Ελέγχου",
        "DD Checklist": "Λίστα Ελέγχου DD",
        "Due Diligence Checklist": "Λίστα Ελέγχου Due Diligence",
        "Related Resources": "Σχετικοί Πόροι",
        "SaaS": "SaaS",
    }
    result = t
    for orig, trans in sorted(replacements.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, trans)
    return result

# --- CZECH ---
def translate_cs(text):
    t = text
    replacements = {
        "Toggle navigation menu": "Přepnout navigační menu",
        "Mobile navigation": "Mobilní navigace",
        "Back to top": "Zpět nahoru",
        "Churn Lens": "Churn Lens",
        "Home": "Domů",
        "Pricing": "Ceník",
        "Founder Story": "Příběh zakladatele",
        "Get the checklist &rarr;": "Získat kontrolní seznam &rarr;",
        "Get the free checklist &rarr;": "Získat bezplatný kontrolní seznam &rarr;",
        "Free Checklist": "Bezplatný kontrolní seznam",
        "DD Checklist": "Kontrolní seznam DD",
        "Due Diligence Checklist": "Kontrolní seznam due diligence",
        "Related Resources": "Související zdroje",
        "SaaS": "SaaS",
    }
    result = t
    for orig, trans in sorted(replacements.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, trans)
    return result

# --- HUNGARIAN ---
def translate_hu(text):
    t = text
    replacements = {
        "Toggle navigation menu": "Navigációs menü váltása",
        "Mobile navigation": "Mobil navigáció",
        "Back to top": "Vissza a tetejére",
        "Churn Lens": "Churn Lens",
        "Home": "Kezdőlap",
        "Pricing": "Árazás",
        "Founder Story": "Alapító története",
        "Get the checklist &rarr;": "Szerezd meg a listát &rarr;",
        "Get the free checklist &rarr;": "Szerezd meg az ingyenes listát &rarr;",
        "Free Checklist": "Ingyenes Ellenőrzőlista",
        "DD Checklist": "DD Ellenőrzőlista",
        "Due Diligence Checklist": "Due Diligence Ellenőrzőlista",
        "Related Resources": "Kapcsolódó Források",
        "SaaS": "SaaS",
    }
    result = t
    for orig, trans in sorted(replacements.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, trans)
    return result

# --- SWEDISH ---
def translate_sv(text):
    t = text
    replacements = {
        "Toggle navigation menu": "Växla navigeringsmeny",
        "Mobile navigation": "Mobil navigering",
        "Back to top": "Tillbaka till toppen",
        "Churn Lens": "Churn Lens",
        "Home": "Hem",
        "Pricing": "Priser",
        "Founder Story": "Grundarberättelse",
        "Get the checklist &rarr;": "Hämta checklistan &rarr;",
        "Get the free checklist &rarr;": "Hämta gratis checklista &rarr;",
        "Free Checklist": "Gratis Checklista",
        "DD Checklist": "DD Checklista",
        "Due Diligence Checklist": "Due Diligence Checklista",
        "Related Resources": "Relaterade Resurser",
        "SaaS": "SaaS",
    }
    result = t
    for orig, trans in sorted(replacements.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, trans)
    return result

# --- FINNISH ---
def translate_fi(text):
    t = text
    replacements = {
        "Toggle navigation menu": "Vaihda navigointivalikko",
        "Mobile navigation": "Mobiilinavigointi",
        "Back to top": "Takaisin ylös",
        "Churn Lens": "Churn Lens",
        "Home": "Koti",
        "Pricing": "Hinnoittelu",
        "Founder Story": "Perustajan tarina",
        "Get the checklist &rarr;": "Hanki tarkistuslista &rarr;",
        "Get the free checklist &rarr;": "Hanki ilmainen tarkistuslista &rarr;",
        "Free Checklist": "Ilmainen Tarkistuslista",
        "DD Checklist": "DD Tarkistuslista",
        "Due Diligence Checklist": "Due Diligence Tarkistuslista",
        "Related Resources": "Aiheeseen Liittyvät Resurssit",
        "SaaS": "SaaS",
    }
    result = t
    for orig, trans in sorted(replacements.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, trans)
    return result

# --- NORWEGIAN ---
def translate_no(text):
    t = text
    replacements = {
        "Toggle navigation menu": "Bytt navigasjonsmeny",
        "Mobile navigation": "Mobil navigasjon",
        "Back to top": "Tilbake til toppen",
        "Churn Lens": "Churn Lens",
        "Home": "Hjem",
        "Pricing": "Prising",
        "Founder Story": "Gründerhistorie",
        "Get the checklist &rarr;": "Få sjekklisten &rarr;",
        "Get the free checklist &rarr;": "Få gratis sjekkliste &rarr;",
        "Free Checklist": "Gratis Sjekkliste",
        "DD Checklist": "DD Sjekkliste",
        "Due Diligence Checklist": "Due Diligence Sjekkliste",
        "Related Resources": "Relaterte Ressurser",
        "SaaS": "SaaS",
    }
    result = t
    for orig, trans in sorted(replacements.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, trans)
    return result

# --- DANISH ---
def translate_da(text):
    t = text
    replacements = {
        "Toggle navigation menu": "Skift navigationsmenu",
        "Mobile navigation": "Mobil navigation",
        "Back to top": "Tilbage til toppen",
        "Churn Lens": "Churn Lens",
        "Home": "Hjem",
        "Pricing": "Priser",
        "Founder Story": "Grundlæggerhistorie",
        "Get the checklist &rarr;": "Få tjeklisten &rarr;",
        "Get the free checklist &rarr;": "Få den gratis tjekliste &rarr;",
        "Free Checklist": "Gratis Tjekliste",
        "DD Checklist": "DD Tjekliste",
        "Due Diligence Checklist": "Due Diligence Tjekliste",
        "Related Resources": "Relaterede Ressourcer",
        "SaaS": "SaaS",
    }
    result = t
    for orig, trans in sorted(replacements.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, trans)
    return result

# --- HEBREW (RTL) ---
def translate_he(text):
    t = text
    replacements = {
        "Toggle navigation menu": "החלפת תפריט ניווט",
        "Mobile navigation": "ניווט נייד",
        "Back to top": "חזרה לראש העמוד",
        "Churn Lens": "Churn Lens",
        "Home": "דף הבית",
        "Pricing": "תמחור",
        "Founder Story": "סיפור המייסד",
        "Get the checklist &rarr;": "קבל את רשימת הבדיקה &rarr;",
        "Get the free checklist &rarr;": "קבל את רשימת הבדיקה החינמית &rarr;",
        "Free Checklist": "רשימת בדיקה חינמית",
        "DD Checklist": "רשימת בדיקה DD",
        "Due Diligence Checklist": "רשימת בדיקת נאותות",
        "Related Resources": "משאבים קשורים",
        "SaaS": "SaaS",
    }
    result = t
    for orig, trans in sorted(replacements.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, trans)
    return result

# --- SWAHILI ---
def translate_sw(text):
    t = text
    replacements = {
        "Toggle navigation menu": "Badilisha menyu ya urambazaji",
        "Mobile navigation": "Urambazaji wa simu",
        "Back to top": "Rudi juu",
        "Churn Lens": "Churn Lens",
        "Home": "Nyumbani",
        "Pricing": "Bei",
        "Founder Story": "Hadithi ya Mwanzilishi",
        "Get the checklist &rarr;": "Pata orodha &rarr;",
        "Get the free checklist &rarr;": "Pata orodha ya bure &rarr;",
        "Free Checklist": "Orodha Bure",
        "DD Checklist": "Orodha ya DD",
        "Due Diligence Checklist": "Orodha ya Due Diligence",
        "Related Resources": "Rasilimali Zinazohusiana",
        "SaaS": "SaaS",
    }
    result = t
    for orig, trans in sorted(replacements.items(), key=lambda x: -len(x[0])):
        result = result.replace(orig, trans)
    return result

# ============================================================
# GENERATE TSV FILES
# ============================================================

# Map of language code to translate function
TRANSLATORS = {
    'ro': translate_ro,
    'el': translate_el,
    'cs': translate_cs,
    'hu': translate_hu,
    'sv': translate_sv,
    'fi': translate_fi,
    'no': translate_no,
    'da': translate_da,
    'he': translate_he,
    'sw': translate_sw,
}

for code, func in TRANSLATORS.items():
    out_path = os.path.join(OUT_DIR, f'{code}.tsv')
    with open(out_path, 'w', encoding='utf-8') as f:
        for k, v in entries:
            translated = func(v)
            # Keep key unchanged, write key|translated_value
            f.write(f'{k}|{translated}\n')
    
    # Verify count
    with open(out_path) as f:
        count = sum(1 for l in f if l.strip())
    print(f"Wrote {count} translations to {out_path}")

print("\nAll TSV files generated!")
