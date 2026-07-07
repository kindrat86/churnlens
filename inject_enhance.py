#!/usr/bin/env python3
"""Inject churnlens enhancement CSS and JS into all .html files in a project."""
import os, glob, re

PROJECT = '/Users/sipi/churnlens'
CSS_TAG = '<link rel="stylesheet" href="/assets/cl-enhance.css" />'
JS_TAG  = '<script type="module" src="/assets/cl-enhance.js" defer></script>'
NAV_HTML = '''\
<!-- CL Mobile Nav Elements -->
<button class="cl-nav-toggle" aria-label="Toggle navigation menu" aria-expanded="false"><span></span></button>
<nav class="cl-nav-drawer" role="navigation" aria-label="Mobile navigation">
  <a href="/">Home</a>
  <a href="/pricing">Pricing</a>
  <a href="/why">Founder Story</a>
  <a href="/manifesto">Manifesto</a>
  <a href="/partners">Partners</a>
  <a href="/get-the-checklist" class="cl-drawer-cta">Get the checklist &rarr;</a>
</nav>
<div class="cl-nav-overlay"></div>
<!-- CL Progress bar -->
<div class="cl-progress"></div>
<!-- CL Back to top -->
<button class="cl-back-top" aria-label="Back to top">&uarr;</button>
<!-- CL Mobile CTA bar -->
<div class="cl-mobile-cta">
  <a href="/get-the-checklist">Get the free checklist &rarr;</a>
</div>'''
CONTENT_NAV = '''\
<!-- CL Mobile Nav Elements (light theme) -->
<button class="cl-nav-toggle" aria-label="Toggle navigation menu" aria-expanded="false"><span></span></button>
<nav class="cl-nav-drawer" role="navigation" aria-label="Mobile navigation">
  <a href="/">Home</a>
  <a href="/pricing">Pricing</a>
  <a href="/why">Founder Story</a>
  <a href="/get-the-checklist" class="cl-drawer-cta">Get the checklist &rarr;</a>
</nav>
<div class="cl-nav-overlay"></div>
<div class="cl-progress"></div>
<button class="cl-back-top" aria-label="Back to top">&uarr;</button>
<div class="cl-mobile-cta">
  <a href="/get-the-checklist">Get the free checklist &rarr;</a>
</div>'''

files = glob.glob(os.path.join(PROJECT, '*.html'))

# Files that have dark theme (navy background)
dark_pages = {'index.html', 'pricing.html', 'get-the-checklist.html', 'why.html', 'who.html', 'manifesto.html', 'partners.html'}
# Files that have light theme (white background content pages)
light_pages = set(f.split('/')[-1] for f in files) - dark_pages - {'annual-plan-churn-risk.html','inactive-paid-accounts.html'}
# These need the light content nav
content_pages = {
    'saas-churn-rate-benchmarks.html', 'saas-due-diligence-checklist.html',
    'customer-concentration-risk.html', 'hidden-churn-saas-acquisition.html',
    'saas-revenue-quality-score.html', 'saas-buyer-risk-assessment.html',
    'saas-mrr-decline-analysis.html', 'logo-retention-churn.html',
    'saas-revenue-churn-calculator.html', 'buying-a-saas-business-guide.html',
    'saas-revenue-concentration-risk.html', 'annual-plan-churn-risk.html',
    'inactive-paid-accounts.html', 'how-to-evaluate-a-saas-before-buying.html',
    'mrr-vs-revenue-quality.html', 'saas-acquisition-red-flags.html',
    'churn-lens-for-acquirers-explainer.html', 'ultimate-saas-due-diligence-guide.html',
}

for fpath in files:
    fname = os.path.basename(fpath)
    with open(fpath, 'r') as f:
        html = f.read()

    # 1. Inject CSS before </head>
    if CSS_TAG not in html and '</head>' in html:
        html = html.replace('</head>', f'  {CSS_TAG}\n</head>')

    # 2. Inject JS before </body>
    if JS_TAG not in html and '</body>' in html:
        html = html.replace('</body>', f'  {JS_TAG}\n</body>')

    # 3. Inject nav elements before </body> (for dark pages, right after nav tag)
    nav_to_use = CONTENT_NAV if fname in content_pages else NAV_HTML

    # Check if already injected
    if 'cl-nav-toggle' not in html:
        # Find nav element and insert mobile nav right before the <body> closing or after the <nav>
        if fname in dark_pages:
            # Insert after the .site-nav / .pricing-nav / .sq-nav closes
            insert_before = '</nav>'  # first nav close tag after opening
            html = html.replace('</nav>', '</nav>\n  ' + nav_to_use, 1)
        elif fname in content_pages:
            html = html.replace('</nav>', '</nav>\n  ' + nav_to_use, 1)
        else:
            # Fallback: just place before footer
            if '</footer>' in html:
                html = html.replace('</footer>', nav_to_use + '\n</footer>')
            else:
                html = html.replace('</body>', nav_to_use + '\n</body>')

    with open(fpath, 'w') as f:
        f.write(html)

    print(f'✓ {fname}')

print('\nDone. Enhanced all HTML files.')
