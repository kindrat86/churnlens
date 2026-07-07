#!/usr/bin/env python3
"""
Post-processing: after all translations are done:
1. Create _combined.json for each language
2. Add language switcher HTML snippet
3. Generate localized HTML in a deployable structure
4. Update vercel.json for i18n routing
5. Copy assets
"""
import os, json, shutil, re

PAGES_DIR = "/Users/sipi/churnlens"
I18N_DIR = os.path.join(PAGES_DIR, "i18n")
LOCALES_DIR = os.path.join(I18N_DIR, "locales")
PAGE_BASES_DIR = os.path.join(I18N_DIR, "page_bases")
DIST_DIR = os.path.join(PAGES_DIR, "dist_i18n")

LANGUAGES = {
    "en": "English",
    "zh-CN": "中文", "hi": "हिन्दी", "es": "Español", "fr": "Français",
    "ar": "العربية", "bn": "বাংলা", "pt": "Português", "ru": "Русский",
    "ur": "اردو", "id": "Bahasa Indonesia", "de": "Deutsch", "ja": "日本語",
    "mr": "मराठी", "te": "తెలుగు", "tr": "Türkçe", "ta": "தமிழ்",
    "vi": "Tiếng Việt", "yue": "粵語", "pa-PK": "پنجابی", "ko": "한국어",
    "fa": "فارسی", "it": "Italiano", "th": "ไทย", "gu": "ગુજરાતી",
    "kn": "ಕನ್ನಡ", "ml": "മലയാളം", "or": "ଓଡ଼ିଆ", "pl": "Polski",
    "uk": "Українська", "nl": "Nederlands", "ro": "Română", "el": "Ελληνικά",
    "cs": "Čeština", "hu": "Magyar", "sv": "Svenska", "fi": "Suomi",
    "no": "Norsk", "da": "Dansk", "he": "עברית", "sw": "Kiswahili",
    "am": "አማርኛ", "so": "Soomaali", "ha": "Hausa", "yo": "Yorùbá",
    "ig": "Igbo", "zu": "isiZulu", "xh": "isiXhosa", "af": "Afrikaans",
    "ms": "Bahasa Melayu", "my": "မြန်မာဘာသာ", "km": "ភាសាខ្មែរ",
    "lo": "ລາວ", "ne": "नेपाली", "si": "සිංහල", "ps": "پښتو",
    "kk": "Қазақ", "uz": "O'zbek", "az": "Azərbaycan", "ka": "ქართული",
    "hy": "Հայերեն", "mn": "Монгол", "bo": "བོད་སྐད", "ug": "ئۇيغۇرچە",
    "tl": "Tagalog", "ceb": "Cebuano", "ilo": "Ilocano", "jv": "Basa Jawa",
    "su": "Basa Sunda", "mad": "Madhurâ", "hmn": "Hmoob", "ku": "Kurdî",
    "bal": "بلوچی", "tg": "Тоҷикӣ", "tk": "Türkmen", "sq": "Shqip",
    "sr": "Српски", "hr": "Hrvatski", "bs": "Bosanski", "sk": "Slovenčina",
    "sl": "Slovenščina", "lt": "Lietuvių", "lv": "Latviešu", "et": "Eesti",
    "be": "Беларуская", "bg": "Български", "mk": "Македонски",
    "ca": "Català", "eu": "Euskara", "gl": "Galego", "cy": "Cymraeg",
    "ga": "Gaeilge", "gd": "Gàidhlig", "br": "Brezhoneg", "is": "Íslenska",
    "lb": "Lëtzebuergesch", "mt": "Malti"
}

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

LANG_SWITCHER_HTML = """
<!-- LANGUAGE SWITCHER - I18N -->
<div class="cl-lang-switcher">
  <button class="cl-lang-btn" onclick="this.parentElement.classList.toggle('open')" aria-label="Switch language">
    <span class="cl-lang-current">LANG_NAME</span>
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M2 4L6 8L10 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
  </button>
  <div class="cl-lang-dropdown">
    LANG_LIST
  </div>
</div>
<style>
.cl-lang-switcher { position: relative; display: inline-block; margin-left: 0.75rem; }
.cl-lang-btn {
  display: inline-flex; align-items: center; gap: 0.3rem;
  background: var(--cl-navy-2); color: #cbd5e1;
  border: 1px solid #334155; border-radius: 0.4rem;
  padding: 0.3rem 0.6rem; font-size: 0.78rem; cursor: pointer;
  font-family: inherit; transition: border-color 0.2s;
}
.cl-lang-btn:hover { border-color: var(--cl-blue); }
.cl-lang-dropdown {
  display: none; position: absolute; top: 100%; right: 0; z-index: 1000;
  background: var(--cl-navy-2); border: 1px solid #334155;
  border-radius: 0.5rem; max-height: 280px; overflow-y: auto;
  min-width: 180px; margin-top: 0.25rem; box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.cl-lang-switcher.open .cl-lang-dropdown { display: block; }
.cl-lang-dropdown a {
  display: block; padding: 0.4rem 0.75rem; color: #cbd5e1;
  text-decoration: none; font-size: 0.8rem; transition: background 0.15s;
}
.cl-lang-dropdown a:hover { background: rgba(37,99,235,0.1); color: #fff; }
.cl-lang-dropdown a.active { color: var(--cl-blue-light); font-weight: 600; }
</style>
"""

def make_lang_list(current_code):
    """Generate HTML for the language dropdown."""
    items = []
    for code, name in sorted(LANGUAGES.items(), key=lambda x: x[1]):
        active = 'active' if code == current_code else ''
        href = f"/{code}/" if code != 'en' else "/"
        items.append(f'<a href="{href}" class="{active}" lang="{code}">{name}</a>')
    return '\n'.join(items)

def add_language_switcher(html, lang_code):
    """Inject language switcher into the nav area."""
    lang_name = LANGUAGES.get(lang_code, lang_code)
    lang_list = make_lang_list(lang_code)
    switcher = LANG_SWITCHER_HTML.replace('LANG_NAME', lang_name).replace('LANG_LIST', lang_list)
    
    # Insert before the closing </nav> tag
    html = html.replace('</nav>', switcher + '\n</nav>')
    
    # Also add to mobile drawer
    html = html.replace('</nav>\n<!-- CL Mobile Nav', '</nav>\n' + switcher + '\n<!-- CL Mobile Nav')
    
    return html

def build_page(lang_code, page_name, translations, output_dir):
    """Build a localized page with language switcher."""
    # Load template
    template_path = os.path.join(PAGE_BASES_DIR, f"{page_name}.html")
    if not os.path.exists(template_path):
        return False
    
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace placeholders
    for placeholder, translation in translations.items():
        html = html.replace(placeholder, translation)
    
    # Update html lang
    html = html.replace('<html lang="en">', f'<html lang="{lang_code}">')
    
    # Update canonical
    if page_name == "index":
        canonical = f"https://churnlens.site/{lang_code}/" if lang_code != 'en' else "https://churnlens.site/"
    else:
        canonical = f"https://churnlens.site/{lang_code}/{page_name}" if lang_code != 'en' else f"https://churnlens.site/{page_name}"
    html = re.sub(
        r'<link rel="canonical" href="https://churnlens\.site/[^"]*"',
        f'<link rel="canonical" href="{canonical}"',
        html
    )
    
    # Add language switcher
    # Skip for index.html which is the default - we handle it differently
    html = add_language_switcher(html, lang_code)
    
    # Add hreflang tags
    hreflang_tags = []
    for lc in LANGUAGES:
        if lc == 'en':
            href = f"https://churnlens.site/{page_name}" if page_name != "index" else "https://churnlens.site/"
        elif page_name == "index":
            href = f"https://churnlens.site/{lc}/"
        else:
            href = f"https://churnlens.site/{lc}/{page_name}"
        hreflang_tags.append(f'<link rel="alternate" hreflang="{lc}" href="{href}" />')
    
    # Add x-default
    xhref = f"https://churnlens.site/{page_name}" if page_name != "index" else "https://churnlens.site/"
    hreflang_tags.append(f'<link rel="alternate" hreflang="x-default" href="{xhref}" />')
    
    html = html.replace('</head>', '\n'.join(hreflang_tags) + '\n</head>')
    
    # Write output
    if lang_code == 'en':
        if page_name == "index":
            out_path = os.path.join(output_dir, "index.html")
        else:
            out_path = os.path.join(output_dir, f"{page_name}.html")
    else:
        lang_dir = os.path.join(output_dir, lang_code)
        os.makedirs(lang_dir, exist_ok=True)
        if page_name == "index":
            out_path = os.path.join(lang_dir, "index.html")
        else:
            out_path = os.path.join(lang_dir, f"{page_name}.html")
    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return True

def main():
    os.makedirs(DIST_DIR, exist_ok=True)
    
    # Copy assets
    for item in ['assets', 'favicon.png', 'robots.txt', '.env.local']:
        src = os.path.join(PAGES_DIR, item)
        dst = os.path.join(DIST_DIR, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
    
    # Copy api directory
    api_src = os.path.join(PAGES_DIR, "api")
    api_dst = os.path.join(DIST_DIR, "api")
    if os.path.exists(api_src) and not os.path.exists(api_dst):
        shutil.copytree(api_src, api_dst)
    
    # Also copy sitemap and llms
    for f in ['sitemap.xml', 'llms.txt']:
        src = os.path.join(PAGES_DIR, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(DIST_DIR, f))
    
    completed = 0
    failed = 0
    total_pages = 0
    
    # Process each language
    for lang_code in sorted(LANGUAGES.keys()):
        # Ensure _combined.json exists
        combined_path = os.path.join(LOCALES_DIR, lang_code, "_combined.json")
        if not os.path.exists(combined_path):
            print(f"SKIP {lang_code}: no _combined.json")
            continue
        
        with open(combined_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        lang_ok = 0
        for page_name in PAGE_NAMES:
            page_translations = translations.get(page_name, {})
            if not page_translations:
                continue
            ok = build_page(lang_code, page_name, page_translations, DIST_DIR)
            if ok:
                lang_ok += 1
        
        if lang_ok > 0:
            completed += 1
            total_pages += lang_ok
            print(f"  {lang_code} ({LANGUAGES[lang_code]}): {lang_ok} pages built")
        else:
            failed += 1
            print(f"  FAILED {lang_code}: no pages built")
    
    print(f"\n{'='*60}")
    print(f"BUILD COMPLETE: {completed} languages, {total_pages} pages")
    
    # Write _languages.json in dist
    lang_info = {k: v for k, v in LANGUAGES.items() 
                 if os.path.exists(os.path.join(LOCALES_DIR, k, "_combined.json"))}
    with open(os.path.join(DIST_DIR, "_languages.json"), 'w', encoding='utf-8') as f:
        json.dump(lang_info, f, indent=2, ensure_ascii=False)
    
    # Write vercel.json
    write_vercel_config(DIST_DIR)
    
    # Create deploy manifest
    write_manifest(DIST_DIR, completed, total_pages)

def write_vercel_config(dist_dir):
    """Generate vercel.json for i18n routing."""
    # Read existing vercel.json for headers
    existing_path = os.path.join(PAGES_DIR, "vercel.json")
    existing = {}
    if os.path.exists(existing_path):
        with open(existing_path, 'r') as f:
            existing = json.load(f)
    
    rewrites = []
    
    # Rewrites: /<lang>/<page> -> /<lang>/<page>.html
    for lang_code in LANGUAGES:
        if not os.path.exists(os.path.join(LOCALES_DIR, lang_code, "_combined.json")):
            continue
        if lang_code == 'en':
            continue  # English is at root
        
        for page_name in PAGE_NAMES:
            if page_name == "index":
                source = f"/{lang_code}"
                destination = f"/{lang_code}/index.html"
            else:
                source = f"/{lang_code}/{page_name}"
                destination = f"/{lang_code}/{page_name}.html"
            rewrites.append({"source": source, "destination": destination})
        
        # Catch-all: /<lang-code>/anything -> /<lang-code>/anything.html if file exists
        rewrites.append({
            "source": f"/{lang_code}/(.+)",
            "destination": f"/{lang_code}/$1.html"
        })
    
    # Root language redirect: /fr -> /fr/
    redirects = []
    for lang_code in LANGUAGES:
        if lang_code == 'en':
            continue
        if not os.path.exists(os.path.join(LOCALES_DIR, lang_code, "_combined.json")):
            continue
        redirects.append({
            "source": f"/{lang_code}",
            "destination": f"/{lang_code}/",
            "permanent": True
        })
    
    # Copy existing rewrites from original vercel.json
    existing_rewrites = existing.get("rewrites", [])
    
    vercel_config = {
        "buildCommand": None,
        "outputDirectory": ".",
        "redirects": redirects + existing.get("redirects", []),
        "rewrites": rewrites + existing_rewrites,
        "headers": existing.get("headers", [])
    }
    
    with open(os.path.join(dist_dir, "vercel.json"), 'w') as f:
        json.dump(vercel_config, f, indent=2)
    
    print(f"  vercel.json written with {len(rewrites)} i18n rewrites")

def write_manifest(dist_dir, lang_count, page_count):
    """Write a deploy manifest."""
    manifest = {
        "project": "churnlens.site",
        "i18n": True,
        "languages": lang_count,
        "pages_per_language": len(PAGE_NAMES),
        "total_pages_deployed": page_count,
        "build_timestamp": __import__('time').ctime()
    }
    with open(os.path.join(dist_dir, "_deploy_manifest.json"), 'w') as f:
        json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    main()
