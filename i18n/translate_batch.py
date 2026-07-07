#!/usr/bin/env python3
"""
Batch translation worker for i18n.
Given a language code and a list of page+text to translate,
outputs the translated JSON files.

Called by: python3 i18n/translate_batch.py <lang_code> [pages...]
Or: python3 i18n/translate_batch.py --all-langs
"""
import os, json, sys, time, re

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

# Load English source
with open(os.path.join(LOCALES_DIR, "en", "_combined.json"), 'r', encoding='utf-8') as f:
    EN_SOURCE = json.load(f)

# Write a comprehensive text file for translation
def write_translation_input(lang_code, lang_name, output_path):
    """Write a single prompt-friendly text file for one language."""
    lines = []
    lines.append(f"# Translation: English -> {lang_name} (code: {lang_code})")
    lines.append(f"# Instructions: Translate each segment below. Preserve the exact key before each text.")
    lines.append(f"# Output format: KEY|TRANSLATION")
    lines.append(f"# IMPORTANT: Keep all HTML entities (&amp;, &lt;, etc.) and special characters intact.")
    lines.append(f"# For '{lang_code}' ({lang_name}), output the translation in {lang_name} script.")
    lines.append(f"# Do NOT translate brand names: 'Churn Lens', 'SaaS'")
    lines.append(f"")
    
    count = 0
    for page_name in PAGE_NAMES:
        if page_name not in EN_SOURCE:
            continue
        page_data = EN_SOURCE[page_name]
        lines.append(f"")
        lines.append(f"## PAGE: {page_name}")
        for key in sorted(page_data.keys()):
            text = page_data[key]
            # Escape newlines in text
            text_flat = text.replace('\n', '\\n')
            lines.append(f"{key}|{text_flat}")
            count += 1
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    return count

def parse_translation_output(input_path, output_dir):
    """Parse the translated output file and produce per-page JSON files."""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    translations = {}
    current_page = None
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('##'):
            if line.startswith('## PAGE:'):
                current_page = line.replace('## PAGE:', '').strip()
            continue
        
        if '|' not in line:
            continue
        
        key, _, val = line.partition('|')
        key = key.strip()
        val = val.strip()
        
        if not key or not val:
            continue
        
        # Determine page from key
        # Keys look like: __TR_pagename_N__
        for page_name in PAGE_NAMES:
            if f"__TR_{page_name}_" in key:
                if page_name not in translations:
                    translations[page_name] = {}
                translations[page_name][key] = val.replace('\\n', '\n')
                break
    
    # Write per-page JSON files
    os.makedirs(output_dir, exist_ok=True)
    total = 0
    for page_name, data in translations.items():
        out_path = os.path.join(output_dir, f"{page_name}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        total += len(data)
    
    return total

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-input", help="Write the translation input file for a language", nargs=3, metavar=("LANG_CODE", "LANG_NAME", "OUTPUT_PATH"))
    parser.add_argument("--parse-output", help="Parse translated output file into locale JSONs", nargs=2, metavar=("INPUT_PATH", "OUTPUT_DIR"))
    args = parser.parse_args()
    
    if args.write_input:
        code, name, path = args.write_input
        count = write_translation_input(code, name, path)
        print(f"Wrote {count} segments for {code} ({name}) to {path}")
    
    if args.parse_output:
        in_path, out_dir = args.parse_output
        count = parse_translation_output(in_path, out_dir)
        print(f"Parsed {count} translations to {out_dir}")
