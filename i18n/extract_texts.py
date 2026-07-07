#!/usr/bin/env python3
"""
Extracts all translatable text content from churnlens HTML files
and produces a single JSON keys file per page.
"""
import os, json, re, sys

PAGES_DIR = "/Users/sipi/churnlens"
OUTPUT_DIR = "/Users/sipi/churnlens/i18n/pages"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# These are the text attributes we want to extract for translation
EXTRACTED_KEYS = {}

# List of page filenames (exclude non-content files)
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

def extract_text_blocks(html, page_name):
    """Extract translatable text blocks from an HTML page."""
    blocks = {}
    counter = 0
    
    # Remove script/style content first
    body = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL)
    
    lines = body.split('\n')
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        
        # Skip HTML tags lines without text
        if stripped.startswith('<') and stripped.endswith('>'):
            continue
            
        # Skip structural tags
        if stripped in ('<head>', '</head>', '<body>', '</body>', '<html>', '</html>', '<!doctype html>'):
            continue
        
        # Look for text between > and < in tags we care about
        # Title tags
        m = re.search(r'<title>(.*?)</title>', stripped)
        if m and m.group(1).strip():
            key = f"title_{counter}"
            blocks[key] = m.group(1).strip()
            counter += 1
            continue
        
        # Meta description
        m = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', stripped)
        if m and m.group(1).strip():
            key = f"meta_desc_{counter}"
            blocks[key] = m.group(1).strip()
            counter += 1
            continue
        
        # Alt text on images
        m = re.search(r'alt="([^"]*)"', stripped)
        if m and m.group(1).strip() and m.group(1).strip() != '':
            key = f"alt_{counter}"
            blocks[key] = m.group(1).strip()
            counter += 1
            continue
        
        # Text nodes inside HTML (text between >...<)
        # Extract any inline text content
        # Full sentences/paragraphs
        if '>' in stripped and '<' in stripped and not stripped.startswith('<meta'):
            text_content = re.sub(r'<[^>]+>', '', stripped).strip()
            if len(text_content) > 3 and text_content not in ('', '...', '/', '&rarr;'):
                key = f"text_{counter}"
                blocks[key] = text_content
                counter += 1
                continue
        
        # JSON-LD text content (schema.org descriptions)
        if '"text":' in stripped:
            m = re.search(r'"text":\s*"([^"]+)"', stripped)
            if m:
                key = f"schema_{counter}"
                blocks[key] = m.group(1)
                counter += 1
                continue
        
        # Plain text lines that look like content
        # Check if it has significant text content
        if len(stripped) > 20 and '<' not in stripped:
            key = f"plain_{counter}"
            blocks[key] = stripped
            counter += 1
    
    return blocks

def main():
    all_page_texts = {}
    
    for pf in PAGE_FILES:
        path = os.path.join(PAGES_DIR, pf)
        if not os.path.exists(path):
            print(f"SKIP: {pf} not found")
            continue
        
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        page_name = pf.replace('.html', '')
        blocks = extract_text_blocks(html, page_name)
        all_page_texts[page_name] = blocks
        
        # Save per-page extraction
        page_out = os.path.join(OUTPUT_DIR, f"{page_name}.json")
        with open(page_out, 'w', encoding='utf-8') as f:
            json.dump(blocks, f, indent=2, ensure_ascii=False)
        
        print(f"EXTRACTED {len(blocks)} keys from {pf}")
    
    # Also save combined
    combined_path = os.path.join(OUTPUT_DIR, "_combined.json")
    with open(combined_path, 'w', encoding='utf-8') as f:
        json.dump(all_page_texts, f, indent=2, ensure_ascii=False)
    
    total_keys = sum(len(v) for v in all_page_texts.values())
    print(f"\nTotal: {len(all_page_texts)} pages, {total_keys} translatable text keys")

if __name__ == "__main__":
    main()
