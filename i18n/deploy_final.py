#!/usr/bin/env python3
"""
FINAL DEPLOY SCRIPT for churnlens.site i18n.
Run after ALL translations are ingested:
1. Create _combined.json for each language
2. Build localized HTML pages with language switcher
3. Generate vercel.json for i18n routing
4. Copy assets

Usage: python3 i18n/deploy_final.py
"""
import os, json, shutil, re, time

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

def make_lang_switcher(current_code):
    """Build language switcher HTML."""
    items = []
    for code, name in sorted(LANGUAGES.items(), key=lambda x: x[1]):
        active = ' active' if code == current_code else ''
        href = f"/{code}/" if code != 'en' else "/"
        items.append(f'<a href="{href}" class="{active}" lang="{code}">{name}</a>')
    
    lang_name = LANGUAGES.get(current_code, current_code)
    
    css = """<style>
.cl-lang-wrap{position:relative;display:inline-block;margin-left:.5rem}
.cl-lang-btn{display:inline-flex;align-items:center;gap:.3rem;background:var(--cl-navy-2);color:#cbd5e1;border:1px solid #334155;border-radius:.4rem;padding:.25rem .55rem;font-size:.75rem;cursor:pointer;font-family:inherit;transition:border-color .2s;line-height:1.4}
.cl-lang-btn:hover{border-color:var(--cl-blue)}
.cl-lang-ddn{display:none;position:absolute;top:100%;right:0;z-index:1000;background:var(--cl-navy-2);border:1px solid #334155;border-radius:.5rem;max-height:300px;overflow-y:auto;min-width:180px;margin-top:.25rem;box-shadow:0 8px 24px rgba(0,0,0,.4)}
.cl-lang-ddn a{display:block;padding:.35rem .7rem;color:#cbd5e1;text-decoration:none;font-size:.78rem;transition:background .1s}
.cl-lang-ddn a:hover{background:rgba(37,99,235,.1);color:#fff}
.cl-lang-ddn a.active{color:var(--cl-blue-light);font-weight:600}
</style>"""
    
    html = f'''<div class="cl-lang-wrap">
  <button class="cl-lang-btn" onclick="this.parentElement.classList.toggle('open')" aria-label="Switch language">
    &#127760; {lang_name} <svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M2 3.5L5 6.5L8 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
  </button>
  <div class="cl-lang-ddn">
    {"".join(items)}
  </div>
</div>'''
    
    return css + '\n' + html

def build_page(lang_code, page_name, translations, output_dir):
    """Build one localized page."""
    tpl = os.path.join(PAGE_BASES_DIR, f"{page_name}.html")
    if not os.path.exists(tpl):
        return False
    
    with open(tpl, encoding='utf-8') as f:
        html = f.read()
    
    # Replace placeholders
    for key, val in translations.items():
        html = html.replace(key, val)
    
    # Update lang
    html = html.replace('<html lang="en">', f'<html lang="{lang_code}">')
    
    # Update canonical
    if lang_code == 'en':
        canonical = f"https://churnlens.site/{page_name}" if page_name != "index" else "https://churnlens.site/"
    else:
        canonical = f"https://churnlens.site/{lang_code}/{page_name}" if page_name != "index" else f"https://churnlens.site/{lang_code}/"
    html = re.sub(r'<link rel="canonical"[^>]*href="[^"]*"', f'<link rel="canonical" href="{canonical}"', html)
    
    # Add hreflang links before </head>
    hreflangs = []
    for lc in LANGUAGES:
        if lc == 'en':
            h = f"https://churnlens.site/{page_name}" if page_name != "index" else "https://churnlens.site/"
        elif page_name == "index":
            h = f"https://churnlens.site/{lc}/"
        else:
            h = f"https://churnlens.site/{lc}/{page_name}"
        hreflangs.append(f'<link rel="alternate" hreflang="{lc}" href="{h}" />')
    xh = f"https://churnlens.site/{page_name}" if page_name != "index" else "https://churnlens.site/"
    hreflangs.append(f'<link rel="alternate" hreflang="x-default" href="{xh}" />')
    html = html.replace('</head>', '\n'.join(hreflangs) + '\n</head>')
    
    # Add language switcher to nav
    # Find the nav-links div or the desktop nav
    ls_html = make_lang_switcher(lang_code)
    html = html.replace('</nav>', ls_html + '\n</nav>')
    
    # Write output
    if lang_code == 'en':
        if page_name == "index":
            out = os.path.join(output_dir, "index.html")
        else:
            out = os.path.join(output_dir, f"{page_name}.html")
    else:
        d = os.path.join(output_dir, lang_code)
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, f"{page_name}.html") if page_name != "index" else os.path.join(d, "index.html")
    
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    return True

def main():
    # Step 1: Create _combined.json for each language
    print("=== Creating combined locale files ===")
    for d in sorted(os.listdir(LOCALES_DIR)):
        dpath = os.path.join(LOCALES_DIR, d)
        if not os.path.isdir(dpath) or d.startswith('.'):
            continue
        combined = {}
        for fname in sorted(os.listdir(dpath)):
            if not fname.endswith('.json') or fname == '_combined.json':
                continue
            ppath = os.path.join(dpath, fname)
            with open(ppath, encoding='utf-8') as f:
                combined[fname.replace('.json','')] = json.load(f)
        if combined:
            with open(os.path.join(dpath, '_combined.json'), 'w', encoding='utf-8') as f:
                json.dump(combined, f, indent=2, ensure_ascii=False)
            total_k = sum(len(v) for v in combined.values())
            print(f"  {d}: {len(combined)} pages, {total_k} keys")
    
    # Step 2: Build dist directory
    print("\n=== Building localized pages ===")
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)
    
    # Copy assets
    for item in os.listdir(PAGES_DIR):
        if item.startswith('.') or item.startswith('i18n') or item in ('dist_i18n', 'node_modules'):
            continue
        sp = os.path.join(PAGES_DIR, item)
        dp = os.path.join(DIST_DIR, item)
        # Skip .html in root (we'll generate them), but copy assets, api, etc.
        if item.endswith('.html') or item.endswith('.py'):
            continue
        if os.path.isdir(sp):
            if item in ('assets', 'api'):
                shutil.copytree(sp, dp, dirs_exist_ok=True)
        else:
            if item in ('favicon.png', 'robots.txt', 'llms.txt', 'sitemap.xml'):
                shutil.copy2(sp, dp)
    
    # Build pages
    completed = 0
    failed = 0
    total_pages = 0
    
    for lang_code in LANGUAGES:
        combined_path = os.path.join(LOCALES_DIR, lang_code, "_combined.json")
        if not os.path.exists(combined_path):
            print(f"  SKIP {lang_code}: no locale data")
            continue
        
        with open(combined_path, encoding='utf-8') as f:
            translations = json.load(f)
        
        lang_ok = 0
        for page_name in PAGE_NAMES:
            page_trans = translations.get(page_name, {})
            if not page_trans:
                continue
            ok = build_page(lang_code, page_name, page_trans, DIST_DIR)
            if ok:
                lang_ok += 1
        
        if lang_ok > 0:
            completed += 1
            total_pages += lang_ok
            print(f"  {lang_code} ({LANGUAGES[lang_code]}): {lang_ok} pages")
        else:
            failed += 1
            print(f"  FAILED {lang_code}")
    
    print(f"\nBUILT: {completed} languages, {total_pages} pages total")
    
    # Step 3: Write vercel.json
    print("\n=== Writing vercel.json ===")
    write_vercel_json(DIST_DIR)
    
    # Step 4: Write _languages.json
    with open(os.path.join(DIST_DIR, "_languages.json"), 'w', encoding='utf-8') as f:
        json.dump(LANGUAGES, f, indent=2, ensure_ascii=False)
    
    # Step 5: Write deploy manifest
    manifest = {
        "project": "churnlens.site",
        "i18n": True,
        "languages_completed": completed,
        "pages_per_language": len(PAGE_NAMES),
        "total_pages": total_pages,
        "build_time": time.ctime()
    }
    with open(os.path.join(DIST_DIR, "_deploy_manifest.json"), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n=== DONE ===")
    print(f"Output: {DIST_DIR}")
    print(f"Total languages: {completed}")
    print(f"Total pages: {total_pages}")

def write_vercel_json(dist_dir):
    """Generate vercel.json with i18n rewrites."""
    rewrites = []
    for lang_code in LANGUAGES:
        if lang_code == 'en':
            continue
        if not os.path.exists(os.path.join(LOCALES_DIR, lang_code, "_combined.json")):
            continue
        
        for page_name in PAGE_NAMES:
            src = f"/{lang_code}/{page_name}" if page_name != "index" else f"/{lang_code}"
            dst = f"/{lang_code}/{page_name}.html" if page_name != "index" else f"/{lang_code}/index.html"
            rewrites.append({"source": src, "destination": dst})
        
        # Catch-all
        rewrites.append({"source": f"/{lang_code}/(.*)", "destination": f"/{lang_code}/$1.html"})
    
    redirects = []
    for lang_code in LANGUAGES:
        if lang_code == 'en':
            continue
        if not os.path.exists(os.path.join(LOCALES_DIR, lang_code, "_combined.json")):
            continue
        redirects.append({"source": f"/{lang_code}", "destination": f"/{lang_code}/", "permanent": True})
    
    config = {
        "buildCommand": None,
        "outputDirectory": ".",
        "redirects": redirects,
        "rewrites": rewrites,
        "headers": [
            {"source": "/(.*)", "headers": [
                {"key": "X-Content-Type-Options", "value": "nosniff"},
                {"key": "X-Frame-Options", "value": "DENY"},
                {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
                {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload"}
            ]}
        ]
    }
    
    with open(os.path.join(dist_dir, "vercel.json"), 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"  {len(rewrites)} i18n rewrites, {len(redirects)} redirects")

if __name__ == "__main__":
    main()
