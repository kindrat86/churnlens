#!/usr/bin/env python3
"""
Generate localized HTML files from templates + locale data.
Usage: python3 i18n/generate_html.py <lang_code>
Example: python3 i18n/generate_html.py es
"""
import os, json, sys, shutil

PAGES_DIR = "/Users/sipi/churnlens"
I18N_DIR = os.path.join(PAGES_DIR, "i18n")
LOCALES_DIR = os.path.join(I18N_DIR, "locales")
PAGE_BASES_DIR = os.path.join(I18N_DIR, "page_bases")
OUT_DIR = os.path.join(PAGES_DIR, "i18n_out")

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

def generate_language(lang_code):
    """Generate all localized HTML files for one language."""
    lang_dir = os.path.join(OUT_DIR, lang_code)
    os.makedirs(lang_dir, exist_ok=True)
    
    # Special dirs (copy assets)
    assets_src = os.path.join(PAGES_DIR, "assets")
    assets_dst = os.path.join(lang_dir, "assets")
    if os.path.exists(assets_src) and not os.path.exists(assets_dst):
        shutil.copytree(assets_src, assets_dst)
    
    api_src = os.path.join(PAGES_DIR, "api")
    api_dst = os.path.join(lang_dir, "api")
    if os.path.exists(api_src) and not os.path.exists(api_dst):
        shutil.copytree(api_src, api_dst)
    
    # Copy favicon, robots, sitemap, llms, inject_* if they exist
    for fname in ["favicon.png", "robots.txt", "sitemap.xml", "llms.txt", ".env.local"]:
        src = os.path.join(PAGES_DIR, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(lang_dir, fname))
    
    # Load locale
    locale_file = os.path.join(LOCALES_DIR, lang_code, "_combined.json")
    if not os.path.exists(locale_file):
        print(f"  LOCALE NOT FOUND: {locale_file}")
        return False
    
    with open(locale_file, 'r', encoding='utf-8') as f:
        locale_data = json.load(f)
    
    for page_name in PAGE_NAMES:
        # Load template
        template_path = os.path.join(PAGE_BASES_DIR, f"{page_name}.html")
        if not os.path.exists(template_path):
            print(f"  TEMPLATE NOT FOUND: {template_path}")
            continue
        
        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Get translations for this page
        page_translations = locale_data.get(page_name, {})
        
        # Replace all placeholders
        for placeholder, translation in page_translations.items():
            html = html.replace(placeholder, translation)
        
        # Update html lang attribute
        html = html.replace('<html lang="en">', f'<html lang="{lang_code}">')
        
        # Update canonical URL
        if page_name == "index":
            canonical = f"https://churnlens.site/{lang_code}/"
            html = re.sub(
                r'<link rel="canonical" href="https://churnlens\.site/[^"]*"',
                f'<link rel="canonical" href="{canonical}"',
                html
            )
        else:
            canonical = f"https://churnlens.site/{lang_code}/{page_name}"
            html = re.sub(
                r'<link rel="canonical" href="https://churnlens\.site/[^"]*"',
                f'<link rel="canonical" href="{canonical}"',
                html
            )
        
        # Write output
        if page_name == "index":
            out_path = os.path.join(lang_dir, "index.html")
        else:
            out_path = os.path.join(lang_dir, f"{page_name}.html")
        
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    # Write _info.json
    info = {"lang_code": lang_code, "pages": len(PAGE_NAMES)}
    with open(os.path.join(lang_dir, "_info.json"), 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2)
    
    return True

if __name__ == "__main__":
    import re
    lang = sys.argv[1] if len(sys.argv) > 1 else "en"
    ok = generate_language(lang)
    if ok:
        print(f"Generated {lang}: {len(PAGE_NAMES)} pages")
    else:
        print(f"FAILED: {lang}")
