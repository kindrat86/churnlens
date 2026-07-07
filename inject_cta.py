#!/usr/bin/env python3
"""Fix duplicate CTA banners and re-process files cleanly."""

import os
import re
import glob

DIR = "/Users/sipi/churnlens"
EXCLUDE = {"index.html", "pricing.html", "get-the-checklist.html", "hidden-churn-saas-acquisition.html"}

# Remove any duplicate CTAs first, then add the correct one
FIXED_CTA_BANNER = '''    <!-- CTA Banner -->
    <div style="max-width:720px;margin:3rem auto;padding:2rem;background:#0f172a;border:1px solid #334155;border-radius:12px;text-align:center;">
      <h3 style="font-family:'Space Grotesk',sans-serif;color:#fff;font-size:1.15rem;margin:0 0 0.75rem;">Get the free 23-point churn audit checklist</h3>
      <p style="color:#94a3b8;font-size:0.9rem;line-height:1.6;margin:0 0 1.25rem;">Sellers hide churn in 7 ways. Most buyers catch 0. Get the full checklist + a sample report on a real $48K MRR case study.</p>
      <a href="/get-the-checklist" class="btn btn-primary" style="display:inline-block;background:#2563eb;color:#fff;padding:0.85rem 2rem;border-radius:10px;font-weight:700;text-decoration:none;font-size:0.95rem;">Get the free checklist &rarr;</a>
    </div>'''

def process_file(filepath):
    basename = os.path.basename(filepath)
    print(f"\n--- {basename} ---")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    original = content
    
    # Step 1: Remove ALL existing CTA banners (both variants)
    # Variant 1: our exact CTA with class="btn btn-primary" and &rarr;
    # Variant 2: the one without class and with literal →
    
    # Remove any block that starts with <!-- CTA Banner --> and has the matching div structure
    # Use a broad pattern to catch any CTA banner block
    cta_pattern = re.compile(
        r'\s*<!-- CTA Banner -->\s*\n\s*<div style="max-width:720px;margin:3rem auto;padding:2rem;background:#0f172a;border:1px solid #334155;border-radius:12px;text-align:center;">\s*\n'
        r'\s*<h3[^>]*>Get the free 23-point churn audit checklist</h3>\s*\n'
        r'\s*<p[^>]*>Sellers hide churn in 7 ways\. Most buyers catch 0\. Get the full checklist \+ a sample report on a real \$48K MRR case study\.</p>\s*\n'
        r'\s*<a href="/get-the-checklist"[^>]*>Get the free checklist[^<]*</a>\s*\n'
        r'\s*</div>',
        re.MULTILINE | re.DOTALL
    )
    
    content = cta_pattern.sub('', content)
    # Simple count via find - safe enough
    # We already know it existed from our check
    
    # Clean up any extra blank lines left behind (collapse 3+ consecutive newlines to 2)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Step 2: Insert the CORRECT CTA banner just before <footer
    footer_match = re.search(r'^(\s*)<footer\s', content, re.MULTILINE)
    if footer_match:
        insert_pos = footer_match.start()
        content = content[:insert_pos] + '\n' + FIXED_CTA_BANNER + '\n\n' + content[insert_pos:]
        print("  ✓ Inserted CTA banner before footer")
    else:
        print("  ✗ Could not find <footer tag")
    
    # Step 3: Add /pricing and /get-the-checklist to footer nav links if missing
    if '/pricing' not in content:
        # Find the closing </p> inside the footer nav
        # Match the DD Checklist / Due Diligence Checklist link followed by </p>
        dd_patterns = [
            (r'(<a href="/saas-due-diligence-checklist"[^>]*>DD Checklist</a>\s*\n\s*</p>)',
             r'\1 &middot;\n        <a href="/get-the-checklist" style="color:hsl(221 83% 53%);text-decoration:none;">Free Checklist</a> &middot;\n        <a href="/pricing" style="color:hsl(221 83% 53%);text-decoration:none;">Pricing</a>\n      </p>'),
            (r'(<a href="/saas-due-diligence-checklist"[^>]*>Due Diligence Checklist</a>\s*\n\s*</p>)',
             r'\1 &middot;\n        <a href="/get-the-checklist" style="color:hsl(221 83% 53%);text-decoration:none;">Free Checklist</a> &middot;\n        <a href="/pricing" style="color:hsl(221 83% 53%);text-decoration:none;">Pricing</a>\n      </p>'),
        ]
        
        nav_added = False
        for pat, repl in dd_patterns:
            new_content, count = re.subn(pat, repl, content, count=1)
            if count > 0:
                content = new_content
                nav_added = True
                print("  ✓ Added /get-the-checklist and /pricing nav links to footer")
                break
        
        if not nav_added:
            print("  ✗ Could not find nav link pattern")
    else:
        print("  → Footer already has pricing/checklist links")
    
    # Write if changed
    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✓ Saved")
    else:
        print(f"  - No changes")

def main():
    files = sorted(glob.glob(os.path.join(DIR, "*.html")))
    count = 0
    for f in files:
        basename = os.path.basename(f)
        if basename in EXCLUDE:
            print(f"\n  [skipped] {basename}")
            continue
        process_file(f)
        count += 1
    print(f"\n{'='*50}")
    print(f"Done! Processed {count} files.")

if __name__ == "__main__":
    main()
