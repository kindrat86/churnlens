#!/usr/bin/env python3
"""
Complete i18n extraction pipeline for churnlens.site static HTML site.
Extracts ALL translatable text from each HTML page and produces locale JSON + templates.
"""
import os, json, re

PAGES_DIR = "/Users/sipi/churnlens"
I18N_DIR = os.path.join(PAGES_DIR, "i18n")
LOCALES_DIR = os.path.join(I18N_DIR, "locales")
PAGE_BASES_DIR = os.path.join(I18N_DIR, "page_bases")

os.makedirs(LOCALES_DIR, exist_ok=True)
os.makedirs(PAGE_BASES_DIR, exist_ok=True)

PAGE_FILES = [
    "index.html", "pricing.html", "why.html", "who.html", "manifesto.html",
    "partners.html", "get-the-checklist.html",
    "annual-plan-churn-risk.html", "buying-a-saas-business-guide.html",
    "churn-lens-for-acquirers-explainer.html", "customer-concentration-risk.html",
    "hidden-churn-saas-acquisition.html", "how-to-evaluate-a-saas-before-buying.html",
    "inactive-paid-accounts.html", "logo-retention-churn.html",
    "mrr-vs-revenue-quality.html", "saas-acquisition-red-flags.html",
    "saas-buyer-risk-assessment.html", "saas-churn-rate-benchmarks.html",
    "saas-due-diligence-checklist.html", "saas-mrr-decline-analysis.html",
    "saas-revenue-churn-calculator.html", "saas-revenue-concentration-risk.html",
    "saas-revenue-quality-score.html", "ultimate-saas-due-diligence-guide.html"
]

REPLACEMENT_TABLE = str.maketrans({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;'
})

def escape_xml(s):
    return s.translate(REPLACEMENT_TABLE)

def extract_translatable_segments(html, page_name):
    """Extract every translatable segment and return (segments_list, template_html)."""
    segments = []
    counter = [0]  # use list for mutability in nested funcs
    
    processed = html
    
    # 1. <title>
    def repl_title(m):
        key = f"__TR_{page_name}_{counter[0]}__"
        counter[0] += 1
        segments.append({"id": key, "text": m.group(1), "type": "title"})
        return f"<title>{key}</title>"
    processed = re.sub(r'<title>(.*?)</title>', repl_title, processed, flags=re.DOTALL)
    
    # 2. <meta name="description" content="...">
    def repl_meta_desc(m):
        key = f"__TR_{page_name}_{counter[0]}__"
        counter[0] += 1
        segments.append({"id": key, "text": m.group(1), "type": "meta_desc"})
        return m.group(0).replace(f'content="{m.group(1)}"', f'content="{key}"')
    processed = re.sub(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', repl_meta_desc, processed)
    
    # 3. og:title, og:description, twitter:title, twitter:description
    for prop_attr in [
        'property="og:title"', 'property="og:description"',
        'name="twitter:title"', 'name="twitter:description"',
        'property="og:site_name"'
    ]:
        pattern1 = rf'<meta[^>]*{re.escape(prop_attr)}[^>]*content="([^"]*)"'
        pattern2 = rf'<meta[^>]*content="([^"]*)"[^>]*{re.escape(prop_attr)}'
        for pat in [pattern1, pattern2]:
            def make_repl(pa):
                def r(m):
                    key = f"__TR_{page_name}_{counter[0]}__"
                    counter[0] += 1
                    segments.append({"id": key, "text": m.group(1), "type": f"meta_{pa}"})
                    return m.group(0).replace(f'content="{m.group(1)}"', f'content="{key}"')
                return r
            processed = re.sub(pat, make_repl(prop_attr), processed)
    
    # 4. alt="..."
    def repl_alt(m):
        t = m.group(1)
        if not t.strip():
            return m.group(0)
        key = f"__TR_{page_name}_{counter[0]}__"
        counter[0] += 1
        segments.append({"id": key, "text": t, "type": "alt"})
        return m.group(0).replace(f'alt="{t}"', f'alt="{key}"')
    processed = re.sub(r'alt="([^"]*)"', repl_alt, processed)
    
    # 5. aria-label="..."
    def repl_aria(m):
        t = m.group(1)
        if not t.strip():
            return m.group(0)
        key = f"__TR_{page_name}_{counter[0]}__"
        counter[0] += 1
        segments.append({"id": key, "text": t, "type": "arialabel"})
        return m.group(0).replace(f'aria-label="{t}"', f'aria-label="{key}"')
    processed = re.sub(r'aria-label="([^"]*)"', repl_aria, processed)
    
    # 6. JSON-LD values
    def repl_jsonld(m):
        raw = m.group(1)
        for field in ['"name"', '"description"', '"text"']:
            def make_jsonr(fname):
                def r(m2):
                    val = m2.group(2)
                    if len(val) > 2 and not val.startswith('__TR_'):
                        key = f"__TR_{page_name}_{counter[0]}__"
                        counter[0] += 1
                        segments.append({"id": key, "text": val, "type": "jsonld"})
                        return f'{fname}: "{escape_xml(key)}"'
                    return m2.group(0)
                return r
            raw = re.sub(rf'{re.escape(field)}:\s*"([^"]+)"', make_jsonr(field), raw)
        return f'<script type="application/ld+json">{raw}</script>'
    processed = re.sub(
        r'<script type="application/ld+json">(.*?)</script>',
        repl_jsonld,
        processed,
        flags=re.DOTALL
    )
    
    # 7. Visible text nodes in body (between > and <)
    # Extract body, process text nodes, reconstruct
    body_match = re.search(r'<body[^>]*>(.*)</body>', processed, re.DOTALL)
    if not body_match:
        return segments, processed
    
    body_start = body_match.start(1)
    body_end = body_match.end(1)
    body_content = body_match.group(1)
    
    # Remove script and style blocks for text extraction but keep original positions
    body_clean = re.sub(r'<script[^>]*>.*?</script>', '', body_content, flags=re.DOTALL)
    body_clean = re.sub(r'<style[^>]*>.*?</style>', '', body_clean, flags=re.DOTALL)
    
    # Find text between > and <
    text_pat = re.compile(r'>(?!\s*<)([^<>{}\n]+?)(?=<|\n|$)', re.MULTILINE)
    
    # Build mapping of positions to replace in body_content
    # We iterate over matches in body_clean and map back to positions in body_content
    replacements = []
    
    # Simple approach: iterate body_clean to find text, then search in body_content
    for m in text_pat.finditer(body_clean):
        raw_text = m.group(1).strip()
        if not raw_text:
            continue
        # Filter out non-translatable
        if raw_text.startswith('http') or raw_text.startswith('/') or raw_text.startswith('#'):
            continue
        if raw_text in ('&rarr;', '&times;', '&ldquo;', '&mdash;', '&bull;', '&copy;', '&uarr;'):
            continue
        if raw_text.startswith('&'):
            continue
        if len(raw_text) < 3:
            continue
        # Check if it's pure numbers/symbols
        stripped_nums = raw_text.replace(' ', '').replace('.', '').replace(',', '').replace('%', '').replace('$', '').replace('£', '').replace('€', '').replace('₹', '').replace('₩', '').replace('¥', '').replace('₽', '')
        if stripped_nums and all(c in '0123456789' for c in stripped_nums):
            continue
        
        key = f"__TR_{page_name}_{counter[0]}__"
        counter[0] += 1
        segments.append({"id": key, "text": raw_text, "type": "text"})
        
        # Now find and replace this text in body_content
        # Use the exact match from body_clean position
        original = m.group(1)  # includes the opening >
        # The actual text is m.group(1)
        escaped = re.escape(raw_text)
        body_content = re.sub(r'(?<=>)' + escaped + r'(?=<|$)', key, body_content, count=1)
    
    processed = processed[:body_start] + body_content + processed[body_end:]
    
    return segments, processed

# Run extraction
all_segments = {}

for pf in PAGE_FILES:
    path = os.path.join(PAGES_DIR, pf)
    if not os.path.exists(path):
        print(f"SKIP: {pf}")
        continue
    
    page_name = pf.replace('.html', '')
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    segments, template_html = extract_translatable_segments(html, page_name)
    all_segments[page_name] = segments
    
    # Save template
    with open(os.path.join(PAGE_BASES_DIR, f"{page_name}.html"), 'w', encoding='utf-8') as f:
        f.write(template_html)
    
    # Save English locale
    en_dict = {seg['id']: seg['text'] for seg in segments}
    os.makedirs(os.path.join(LOCALES_DIR, 'en'), exist_ok=True)
    with open(os.path.join(LOCALES_DIR, 'en', f"{page_name}.json"), 'w', encoding='utf-8') as f:
        json.dump(en_dict, f, indent=2, ensure_ascii=False)
    
    print(f"  {pf}: {len(segments)} segments")

total = sum(len(v) for v in all_segments.values())
print(f"\nTotal: {len(all_segments)} pages, {total} segments")
