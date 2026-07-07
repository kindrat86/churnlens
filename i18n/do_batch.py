#!/usr/bin/env python3
"""
Self-contained i18n batch translator for subagents.
Run from terminal:
  python3 /Users/sipi/churnlens/i18n/do_batch.py <lang_codes_file>
  
Where <lang_codes_file> contains one language per line: code|name
"""
import os, json, sys, re

BASE = "/Users/sipi/churnlens"
I18N_DIR = os.path.join(BASE, "i18n")
LOCALES_DIR = os.path.join(I18N_DIR, "locales")
PAGE_NAMES = [
    "index","pricing","why","who","manifesto","partners","get-the-checklist",
    "annual-plan-churn-risk","buying-a-saas-business-guide",
    "churn-lens-for-acquirers-explainer","customer-concentration-risk",
    "hidden-churn-saas-acquisition","how-to-evaluate-a-saas-before-buying",
    "inactive-paid-accounts","logo-retention-churn","mrr-vs-revenue-quality",
    "saas-acquisition-red-flags","saas-buyer-risk-assessment",
    "saas-churn-rate-benchmarks","saas-due-diligence-checklist",
    "saas-mrr-decline-analysis","saas-revenue-churn-calculator",
    "saas-revenue-concentration-risk","saas-revenue-quality-score",
    "ultimate-saas-due-diligence-guide"
]

def read_lang_codes(path):
    """Read language codes from file: code|name per line."""
    langs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('|')
            if len(parts) >= 1:
                langs.append(parts[0].strip())
    return langs

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 do_batch.py <lang_codes_file>")
        sys.exit(1)
    
    lang_file = sys.argv[1]
    lang_codes = read_lang_codes(lang_file)
    
    print(f"Batch: {len(lang_codes)} languages: {', '.join(lang_codes)}")
    
    # Load English source once
    en_combined = os.path.join(LOCALES_DIR, "en", "_combined.json")
    if not os.path.exists(en_combined):
        print(f"ERROR: No English locale at {en_combined}")
        sys.exit(1)
    
    with open(en_combined, encoding='utf-8') as f:
        en_source = json.load(f)
    
    # Collect all English texts: flat {key: text}
    all_en = {}
    for page_name, page_data in en_source.items():
        for key, text in page_data.items():
            all_en[key] = text
    
    print(f"Loaded {len(all_en)} English segments")
    
    for lang_code in lang_codes:
        print(f"\n{'='*60}")
        print(f"Translating: {lang_code}")
        print(f"{'='*60}")
        
        # Translate all segments
        translations = translate_all(all_en, lang_code)
        
        if not translations:
            print(f"  FAILED: no translations for {lang_code}")
            continue
        
        # Group by page
        page_data = {}
        for key, val in translations.items():
            pn = key.split('__TR_')[1].split('_')[0] if '__TR_' in key else "_unknown"
            page_data.setdefault(pn, {})[key] = val
        
        # Write locale files
        out_dir = os.path.join(LOCALES_DIR, lang_code)
        os.makedirs(out_dir, exist_ok=True)
        
        total = 0
        for pn, data in sorted(page_data.items()):
            path = os.path.join(out_dir, f"{pn}.json")
            # Merge with existing
            existing = {}
            if os.path.exists(path):
                with open(path, encoding='utf-8') as f:
                    existing = json.load(f)
            existing.update(data)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            total += len(data)
        
        # Check completeness
        missing = [k for k in all_en if k not in translations]
        if missing:
            print(f"  PARTIAL: {len(translations)}/{len(all_en)} ({len(missing)} missing)")
        else:
            print(f"  COMPLETE: All {len(translations)} segments!")
        
        print(f"  Saved to {out_dir}")
    
    print(f"\n{'='*60}")
    print(f"Batch done: {len(lang_codes)} languages processed")

def translate_all(texts, lang_code):
    """
    Translate ALL texts at once.
    This function is called by the subagent, which is an LLM.
    The subagent must read this function and execute it,
    producing translations for all segments.
    
    The function signature says it takes (texts, lang_code) and
    returns {key: translated_text}.
    
    The subagent should:
    1. Take all ~2134 text segments
    2. Group them into chunks of ~100
    3. For each chunk, translate all segments
    4. Return the complete dict
    """
    # This is a stub - the subagent must implement this.
    # The subagent will output the translations inline.
    return {}

if __name__ == "__main__":
    main()
