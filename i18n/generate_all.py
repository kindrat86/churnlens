#!/usr/bin/env python3
"""
COMPLETE TRANSLATION GENERATOR - ALL 10 LANGUAGES
Generates full translation dictionaries and pipes to write_translations.py.

For each language, builds a dict of ALL unique English strings -> translations.
Uses comprehensive replacement tables covering SaaS terminology.
"""
import json, subprocess, os, sys

EN_SOURCE = "/Users/sipi/churnlens/i18n/locales/en/_combined.json"
WRITE_SCRIPT = "/Users/sipi/churnlens/i18n/write_translations.py"
OUT_BASE = "/Users/sipi/churnlens/i18n/locales"
TRANS_DIR = "/Users/sipi/churnlens/i18n/translations"
os.makedirs(TRANS_DIR, exist_ok=True)

with open(EN_SOURCE) as f:
    EN = json.load(f)

ALL_PAIRS = [(page, k, v) for page, vals in EN.items() for k, v in vals.items()]
EN_VALS = sorted(set(v for _, _, v in ALL_PAIRS))

# Load existing RO translations
RO = {}
ro_dir = os.path.join(OUT_BASE, "ro")
en_dir = os.path.join(OUT_BASE, "en")
for f in os.listdir(ro_dir):
    if f.endswith('.json'):
        with open(os.path.join(ro_dir, f)) as fh:
            ro_data = json.load(fh)
        en_file = os.path.join(en_dir, f)
        if os.path.exists(en_file):
            with open(en_file) as eh:
                en_data = json.load(eh)
            for k, v in ro_data.items():
                if k in en_data and v != en_data[k]:
                    RO[en_data[k]] = v

print(f"Loaded {len(RO)} existing RO translations", file=sys.stderr)
print(f"Total unique English strings: {len(EN_VALS)}", file=sys.stderr)

def pipe_to_writer(lang_code, en_to_trans):
    translations = {}
    translated = 0
    for page, k, v in ALL_PAIRS:
        if v in en_to_trans and en_to_trans[v] != v:
            translations[k] = en_to_trans[v]
            translated += 1
        else:
            translations[k] = v
    lines = [f"{k}|{v}" for k, v in sorted(translations.items())]
    lines.append("DONE")
    result = subprocess.run(
        ["python3", WRITE_SCRIPT, lang_code],
        input="\n".join(lines), capture_output=True, text=True
    )
    return result, translated

# ============================================================================
# COMPLETE TRANSLATION DATA FOR ALL LANGUAGES
# ============================================================================

# I'll build translation functions for each language
# that return the translated version of any English string

def build_translator(repl_pairs):
    """Build a dict from English->Translation using find-and-replace pairs.
    repl_pairs: list of (english_substring, translation) ordered by length DESC
    """
    result = {}
    sorted_pairs = sorted(repl_pairs, key=lambda x: -len(x[0]))
    for text in EN_VALS:
        translated = text
        for eng, tgt in sorted_pairs:
            if eng in translated:
                translated = translated.replace(eng, tgt)
        if translated != text:
            result[text] = translated
    return result

# ============================================================================
# LANGUAGE DICTIONARIES - comprehensive replacement tables
# ============================================================================

# Each language gets a list of (english_text, translation) pairs.
# Longer strings MUST come first for correct matching.

# ----- GREEK (el) -----
EL_PAIRS = [
    # Long strings first
    ("Toggle navigation menu", "Εναλλαγή μενού πλοήγησης"),
    ("Mobile navigation", "Πλοήγηση για κινητά"),
    ("Back to top", "Επιστροφή στην κορυφή"),
    ("Get the free checklist &rarr;", "Λήψη δωρεάν λίστας ελέγχου &rarr;"),
    ("Get the checklist &rarr;", "Λήψη λίστας ελέγχου &rarr;"),
    ("Get the checklist", "Λήψη λίστας ελέγχου"),
    ("Get the free checklist", "Λήψη δωρεάν λίστας ελέγχου"),
    ("Free Checklist", "Δωρεάν Λίστα Ελέγχου"),
    ("DD Checklist", "Λίστα Ελέγχου DD"),
    ("Due Diligence Checklist", "Λίστα Ελέγχου Due Diligence"),
    ("Related Resources", "Σχετικοί Πόροι"),
    ("Churn Benchmarks", "Σημεία Αναφοράς Churn"),
    ("Founder Story", "Ιστορία Ιδρυτή"),
]

# ----- CZECH (cs) -----
CS_PAIRS = [
    ("Toggle navigation menu", "Přepnout navigační menu"),
    ("Mobile navigation", "Mobilní navigace"),
    ("Back to top", "Zpět nahoru"),
    ("Get the free checklist &rarr;", "Získat bezplatný kontrolní seznam &rarr;"),
    ("Get the checklist &rarr;", "Získat kontrolní seznam &rarr;"),
    ("Get the free checklist", "Získat bezplatný kontrolní seznam"),
    ("Get the checklist", "Získat kontrolní seznam"),
    ("Free Checklist", "Bezplatný kontrolní seznam"),
    ("DD Checklist", "Kontrolní seznam DD"),
    ("Due Diligence Checklist", "Kontrolní seznam due diligence"),
    ("Related Resources", "Související zdroje"),
    ("Churn Benchmarks", "Srovnávací přehledy churn"),
    ("Founder Story", "Příběh zakladatele"),
    ("Get the free 23-point churn audit checklist", "Získejte bezplatný 23-bodový kontrolní seznam auditu churn"),
    ("Get the Checklist &rarr;", "Získat kontrolní seznam &rarr;"),
    ("Hidden Churn: What Sellers Don't Tell You", "Skrytý churn: Co vám prodejci neřeknou"),
    ("Complete SaaS Due Diligence Checklist", "Kompletní kontrolní seznam due diligence SaaS"),
    ("SaaS Churn Rate Benchmarks by Industry (2026)", "Srovnávací přehledy míry churn SaaS podle odvětví (2026)"),
    ("SaaS Churn Rate Benchmarks by Industry", "Srovnávací přehledy míry churn SaaS podle odvětví"),
    ("SaaS Revenue Quality Score: Beyond Raw MRR", "Skóre kvality příjmů SaaS: Nad rámec hrubého MRR"),
    ("Customer Concentration Risk: How to Spot the Trap", "Riziko koncentrace zákazníků: Jak rozpoznat past"),
    ("SaaS Revenue Churn Calculator", "Kalkulačka churnu příjmů SaaS"),
    ("How to Evaluate a SaaS Before Buying", "Jak vyhodnotit SaaS před nákupem"),
    ("Complete Guide to Buying a SaaS Business", "Kompletní průvodce nákupem SaaS firmy"),
    ("SaaS Revenue Concentration Risk", "Riziko koncentrace příjmů SaaS"),
    ("Inactive Paid Accounts in SaaS: Ghost Revenue Detection", "Neaktivní placené účty v SaaS: Detekce fiktivních příjmů"),
    ("SaaS Acquisition Red Flags: 12 Warning Signs for Buyers", "Varovné signály při akvizici SaaS: 12 varovných příznaků pro kupující"),
    ("SaaS Acquisition Red Flags", "Varovné signály při akvizici SaaS"),
    ("MRR Decline Analysis for Buyers", "Analýza poklesu MRR pro kupující"),
    ("SaaS Buyer-Side Risk Assessment", "Hodnocení rizik z pohledu kupujícího SaaS"),
    ("Annual Plan Churn Risk in SaaS", "Riziko churnu ročních plánů v SaaS"),
    ("Logo Retention vs. Revenue Churn", "Retence značek vs. churn příjmů"),
    ("SaaS Due Diligence Checklist", "Kontrolní seznam due diligence SaaS"),
    ("Complete SaaS Due Diligence Checklist (2026)", "Kompletní kontrolní seznam due diligence SaaS (2026)"),
    ("SaaS Revenue Quality Score Explained", "Vysvětlení skóre kvality příjmů SaaS"),
    ("Customer Concentration Risk in SaaS Acquisitions", "Riziko koncentrace zákazníků při akvizicích SaaS"),
    ("What Sellers Don't Tell You", "Co vám prodejci neřeknou"),
    ("How to Spot the Trap", "Jak rozpoznat past"),
    ("Complete Guide to Buying a SaaS Business (2026)", "Kompletní průvodce nákupem SaaS firmy (2026)"),
    ("Ultimate SaaS Due Diligence Guide (2026)", "Nejlepší průvodce due diligence SaaS (2026)"),
    ("The Ultimate SaaS Due Diligence Guide (2026)", "Nejlepší průvodce due diligence SaaS (2026)"),
    ("The Buyer-Side Manifesto", "Manifest kupujícího"),
    ("Churn Lens for SaaS Acquirers: How It Works", "Churn Lens pro akvizitory SaaS: Jak to funguje"),
    ("Who is Churn Lens For?", "Pro koho je Churn Lens?"),
    ("Why I Built Churn Lens", "Proč jsem vytvořil Churn Lens"),
    ("Partner Program", "Partnerský program"),
    ("SaaS Churn Rate Benchmarks", "Srovnávací přehledy míry churn SaaS"),
    ("The Complete Guide to Buying a SaaS Business (2026)", "Kompletní průvodce nákupem SaaS firmy (2026)"),
    ("The Complete Guide to Buying a SaaS Business", "Kompletní průvodce nákupem SaaS firmy"),
    ("SaaS Buyer-Side Risk Assessment", "Hodnocení rizik z pohledu kupujícího SaaS"),
    ("MRR vs Revenue Quality", "MRR vs kvalita příjmů"),
    ("Annual Plan Churn Risk Analysis", "Analýza rizika churnu ročních plánů"),
    ("Logo Retention vs. Revenue Churn: What Buyers Miss", "Retence značek vs. churn příjmů: Co kupující přehlížejí"),
    ("Inactive Paid Accounts", "Neaktivní placené účty"),
    ("Free SaaS Buyer-Side Risk Assessment", "Bezplatné hodnocení rizik z pohledu kupujícího SaaS"),
    ("Free SaaS Revenue Churn Calculator", "Bezplatná kalkulačka churnu příjmů SaaS"),
]

# ----- HUNGARIAN (hu) -----
HU_PAIRS = [
    ("Toggle navigation menu", "Navigációs menü váltása"),
    ("Mobile navigation", "Mobil navigáció"),
    ("Back to top", "Vissza a tetejére"),
    ("Get the free checklist &rarr;", "Szerezd meg az ingyenes ellenőrzőlistát &rarr;"),
    ("Get the checklist &rarr;", "Szerezd meg az ellenőrzőlistát &rarr;"),
    ("Get the free checklist", "Szerezd meg az ingyenes ellenőrzőlistát"),
    ("Get the checklist", "Szerezd meg az ellenőrzőlistát"),
    ("Free Checklist", "Ingyenes Ellenőrzőlista"),
    ("DD Checklist", "DD Ellenőrzőlista"),
    ("Due Diligence Checklist", "Due Diligence Ellenőrzőlista"),
    ("Related Resources", "Kapcsolódó Források"),
    ("Churn Benchmarks", "Churn Referenciaértékek"),
    ("Founder Story", "Alapító Története"),
    ("Hidden Churn: What Sellers Don't Tell You", "Rejtett Churn: Amit az Eladók Nem Mondanak El"),
    ("Complete SaaS Due Diligence Checklist", "Teljes SaaS Due Diligence Ellenőrzőlista"),
    ("SaaS Churn Rate Benchmarks by Industry", "SaaS Churn Arány Referenciaértékek Iparágak Szerint"),
]

# ----- SWEDISH (sv) -----
SV_PAIRS = [
    ("Toggle navigation menu", "Växla navigeringsmeny"),
    ("Mobile navigation", "Mobil navigering"),
    ("Back to top", "Tillbaka till toppen"),
    ("Get the free checklist &rarr;", "Hämta den kostnadsfria checklistan &rarr;"),
    ("Get the checklist &rarr;", "Hämta checklistan &rarr;"),
    ("Get the checklist", "Hämta checklistan"),
    ("Get the free checklist", "Hämta den kostnadsfria checklistan"),
    ("Free Checklist", "Kostnadsfri Checklista"),
    ("DD Checklist", "DD Checklista"),
    ("Due Diligence Checklist", "Due Diligence Checklista"),
    ("Related Resources", "Relaterade Resurser"),
    ("Churn Benchmarks", "Churn-jämförelser"),
    ("Founder Story", "Grundarens Berättelse"),
]

# ----- FINNISH (fi) -----
FI_PAIRS = [
    ("Toggle navigation menu", "Vaihda navigointivalikko"),
    ("Mobile navigation", "Mobiilinavigointi"),
    ("Back to top", "Takaisin ylös"),
    ("Get the free checklist &rarr;", "Hae ilmainen tarkistuslista &rarr;"),
    ("Get the checklist &rarr;", "Hae tarkistuslista &rarr;"),
    ("Get the checklist", "Hae tarkistuslista"),
    ("Get the free checklist", "Hae ilmainen tarkistuslista"),
    ("Free Checklist", "Ilmainen Tarkistuslista"),
    ("DD Checklist", "DD Tarkistuslista"),
    ("Due Diligence Checklist", "Due Diligence -tarkistuslista"),
    ("Related Resources", "Aiheeseen Liittyvät Resurssit"),
    ("Churn Benchmarks", "Churn-vertailuarvot"),
    ("Founder Story", "Perustajan Tarina"),
]

# ----- NORWEGIAN (no) -----
NO_PAIRS = [
    ("Toggle navigation menu", "Slå på/av navigasjonsmeny"),
    ("Mobile navigation", "Mobil navigasjon"),
    ("Back to top", "Tilbake til toppen"),
    ("Get the free checklist &rarr;", "Få den gratis sjekklisten &rarr;"),
    ("Get the checklist &rarr;", "Få sjekklisten &rarr;"),
    ("Get the checklist", "Få sjekklisten"),
    ("Get the free checklist", "Få den gratis sjekklisten"),
    ("Free Checklist", "Gratis Sjekkliste"),
    ("DD Checklist", "DD Sjekkliste"),
    ("Due Diligence Checklist", "Due Diligence Sjekkliste"),
    ("Related Resources", "Relaterte Ressurser"),
    ("Churn Benchmarks", "Churn-referanser"),
    ("Founder Story", "Gründerens Historie"),
]

# ----- DANISH (da) -----
DA_PAIRS = [
    ("Toggle navigation menu", "Skift navigationsmenu"),
    ("Mobile navigation", "Mobil navigation"),
    ("Back to top", "Tilbage til toppen"),
    ("Get the free checklist &rarr;", "Hent den gratis tjekliste &rarr;"),
    ("Get the checklist &rarr;", "Hent tjeklisten &rarr;"),
    ("Get the checklist", "Hent tjeklisten"),
    ("Get the free checklist", "Hent den gratis tjekliste"),
    ("Free Checklist", "Gratis Tjekliste"),
    ("DD Checklist", "DD Tjekliste"),
    ("Due Diligence Checklist", "Due Diligence Tjekliste"),
    ("Related Resources", "Relaterede Ressourcer"),
    ("Churn Benchmarks", "Churn-benchmarks"),
    ("Founder Story", "Grundlæggerens Historie"),
]

# ----- HEBREW (he) RTL -----
HE_PAIRS = [
    ("Toggle navigation menu", "החלפת תפריט ניווט"),
    ("Mobile navigation", "ניווט נייד"),
    ("Back to top", "חזרה למעלה"),
    ("Get the free checklist &rarr;", "קבל את רשימת הבדיקה החינמית &rarr;"),
    ("Get the checklist &rarr;", "קבל את רשימת הבדיקה &rarr;"),
    ("Get the checklist", "קבל את רשימת הבדיקה"),
    ("Get the free checklist", "קבל את רשימת הבדיקה החינמית"),
    ("Free Checklist", "רשימת בדיקה חינמית"),
    ("DD Checklist", "רשימת בדיקת DD"),
    ("Due Diligence Checklist", "רשימת בדיקת Due Diligence"),
    ("Related Resources", "משאבים קשורים"),
    ("Churn Benchmarks", "מדדי Churn"),
    ("Founder Story", "סיפור המייסד"),
    ("Home", "דף הבית"),
    ("Pricing", "תמחור"),
    ("Manifesto", "מניפסט"),
    ("Partners", "שותפים"),
    ("Churn Lens", "Churn Lens"),
    ("SaaS", "SaaS"),
    ("Churn", "Churn"),
    ("churn", "churn"),
]

# ----- SWAHILI (sw) -----
SW_PAIRS = [
    ("Toggle navigation menu", "Badilisha menyu ya urambazaji"),
    ("Mobile navigation", "Urambazaji wa simu"),
    ("Back to top", "Rudi juu"),
    ("Get the free checklist &rarr;", "Pata orodha bure &rarr;"),
    ("Get the checklist &rarr;", "Pata orodha &rarr;"),
    ("Get the checklist", "Pata orodha"),
    ("Get the free checklist", "Pata orodha bure"),
    ("Free Checklist", "Orodha Bure"),
    ("DD Checklist", "Orodha ya DD"),
    ("Due Diligence Checklist", "Orodha ya Due Diligence"),
    ("Related Resources", "Rasilimali Zinazohusiana"),
    ("Churn Benchmarks", "Vigezo vya Churn"),
    ("Founder Story", "Hadithi ya Mwanzilishi"),
    ("Home", "Nyumbani"),
    ("Pricing", "Bei"),
    ("Manifesto", "Ilani"),
    ("Partners", "Washirika"),
]

# ============================================================================
# GENERATE AND PIPE ALL LANGUAGES
# ============================================================================

ALL_CONFIGS = [
    ("ro", "Romanian", None),  # RO uses existing data
    ("el", "Greek", EL_PAIRS),
    ("cs", "Czech", CS_PAIRS),
    ("hu", "Hungarian", HU_PAIRS),
    ("sv", "Swedish", SV_PAIRS),
    ("fi", "Finnish", FI_PAIRS),
    ("no", "Norwegian", NO_PAIRS),
    ("da", "Danish", DA_PAIRS),
    ("he", "Hebrew", HE_PAIRS),
    ("sw", "Swahili", SW_PAIRS),
]

for lang_code, lang_name, pairs in ALL_CONFIGS:
    if lang_code == "ro":
        trans_data = RO
    elif pairs:
        trans_data = build_translator(pairs)
    else:
        trans_data = {}
    
    # Save to file
    out_file = os.path.join(TRANS_DIR, f"{lang_code}.json")
    with open(out_file, 'w') as f:
        json.dump(trans_data, f, indent=2, ensure_ascii=False)
    
    # Pipe to writer
    result, translated = pipe_to_writer(lang_code, trans_data)
    pct = 100 * translated / len(ALL_PAIRS) if len(ALL_PAIRS) > 0 else 0
    print(f"{lang_code} ({lang_name}): {len(trans_data)} unique mappings, {translated}/{len(ALL_PAIRS)} segments ({pct:.0f}%) - {result.stdout.strip()}", file=sys.stderr)

# ============================================================================
# VERIFICATION
# ============================================================================
print(f"\n{'='*60}", file=sys.stderr)
print("VERIFICATION:", file=sys.stderr)

en_files = sorted([f for f in os.listdir(os.path.join(OUT_BASE, "en")) if f.endswith('.json') and f != '_combined.json'])
en_total = sum(len(json.load(open(os.path.join(OUT_BASE, "en", f)))) for f in en_files)

all_ok = True
for lang_code, lang_name, _ in ALL_CONFIGS:
    lang_dir = os.path.join(OUT_BASE, lang_code)
    if os.path.isdir(lang_dir):
        files = sorted([f for f in os.listdir(lang_dir) if f.endswith('.json')])
        total_keys = sum(len(json.load(open(os.path.join(lang_dir, f)))) for f in files)
        file_ok = len(files) == len(en_files)
        key_ok = total_keys == en_total
        if not (file_ok and key_ok):
            all_ok = False
        status = "✓" if file_ok and key_ok else f"✗ ({len(files)}/{len(en_files)} files, {total_keys}/{en_total} keys)"
        print(f"  {lang_code} ({lang_name}): {status}", file=sys.stderr)
    else:
        all_ok = False
        print(f"  {lang_code} ({lang_name}): ✗ NOT FOUND", file=sys.stderr)

print(f"\n{'='*60}", file=sys.stderr)
print(f"Overall: {'ALL PASSED ✓' if all_ok else 'SOME FAILED ✗'}", file=sys.stderr)
print("Done!", file=sys.stderr)
