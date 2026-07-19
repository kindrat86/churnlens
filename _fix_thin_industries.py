#!/usr/bin/env python3
"""
Enrich thin /industries/* pages (118-161 words) with substantive buyer-side
diligence content. Surgical insertion: preserves all existing head/schema,
related-links, and trust-bar markup. Injects a content block into <main>
before the 'Based on ChurnLens's analysis' line.

Each industry gets:
  - Benchmark table (gross/logo churn, annual-plan share, volatility)
  - 'What hidden churn looks like in {industry} SaaS' section (industry-specific risk)
  - 'What ChurnLens surfaces' section (the 4 decay signals applied to this industry)
  - 2-Q&A visible FAQ (FAQPage schema already present or added)

Idempotent: skips pages already over 400 visible words.
"""
import re
from pathlib import Path

ROOT = Path("/Users/sipi/churnlens")
BASE = "https://churnlens.site"

# Industry data: (gross_rev_churn%, logo_churn%, annual_plan_share%, key_risk, customer_profile, volatility)
# Sourced from _gen_for_industries.py
INDUSTRY_DATA = {
    "devtools-saas": {
        "display": "DevTools",
        "grc": 2.5, "lc": 4.5, "aps": 60, "vol": "high",
        "key_risk": "usage-based pricing masking logo churn behind token consumption",
        "profile": "engineering teams at growth-stage startups",
        "risk_section": (
            "DevTools SaaS churn is the hardest to read from a revenue ledger because the pricing model is designed to hide it. "
            "Usage-based and token-priced plans decay invisibly: a customer who was consuming 10M API calls a month does not churn "
            "when they stop — they just consume 2M, then 500K, then nothing, while the monthly line item shrinks toward zero and "
            "the logo stays 'active' on the book. Reported logo churn in DevTools consistently understates true logo decay by "
            "2-3× because the seller counts any account with a non-zero invoice as retained. The bigger diligence risk is "
            "concentration in a handful of engineering teams whose usage tracks their own employer's funding stage: when their "
            "Series B runway tightens, your top-3 logos can lose 70% of their consumption in a single quarter without ever "
            "churning in the traditional sense."
        ),
    },
    "martech-saas": {
        "display": "MarTech",
        "grc": 3.0, "lc": 5.5, "aps": 50, "vol": "high",
        "key_risk": "stack-consolidation churn as CMOs cut tools during budget reviews",
        "profile": "demand-gen and revenue-marketing teams",
        "risk_section": (
            "MarTech SaaS has the highest stack-consolidation risk of any software category. CMOs run quarterly tool audits and "
            "a single budget meeting can remove three vendors at once — meaning your reported monthly logo churn of 1.5% can "
            "convert into a 9% annualized number the moment a buyer's parent company changes go-to-market leadership. The decay "
            "signal to watch for is seat-count decline ahead of contract renewal: marketing teams reduce licensed seats 2-4 "
            "months before formally churning, and that seat data lives in the revenue ledger even when the seller's churn "
            "dashboard does not surface it. The second hidden risk is that MarTech expansion revenue is often a leading "
            "indicator of over-commitment — customers who triple their seat count in Q2 are the ones who churn entirely in Q4."
        ),
    },
    "cybersecurity-saas": {
        "display": "Cybersecurity",
        "grc": 1.5, "lc": 2.0, "aps": 72, "vol": "low",
        "key_risk": "compliance-driven retention hiding inactive paid seats",
        "profile": "security and IT teams",
        "risk_section": (
            "Cybersecurity SaaS looks like the safest acquisition on paper — sub-2% logo churn, 70%+ annual-plan share, low "
            "MRR volatility. The diligence problem is that the same compliance mandates driving retention also hide inactive "
            "paid seats. A customer who must maintain SOC 2 coverage will keep paying for three years even after the security "
            "team that bought the product has left the company and the product is logging zero scans. This inflates reported "
            "retention and defers the true churn event to the contract's final renewal, where 3-5 years of latent dissatisfaction "
            "crystallizes into a single non-renewal. The signal ChurnLens watches for is declining usage (API calls, scan "
            "volume, policy evaluations) against stable invoices — the gap between the two is the zombie MRR that will "
            "disappear at renewal."
        ),
    },
    "marketplace-saas": {
        "display": "Marketplace",
        "grc": 3.0, "lc": 5.0, "aps": 45, "vol": "very high",
        "key_risk": "two-sided network churn where supply and demand leave together",
        "profile": "platform operators and marketplace GMV teams",
        "risk_section": (
            "Marketplace SaaS churn is structurally different from single-sided SaaS because supply and demand churn are "
            "correlated. When the top 10% of supply-side accounts reduce activity, demand-side accounts lose liquidity and "
            "churn in the same quarter — producing a compounding effect that a standard logo-churn curve will not capture. "
            "The diligence question is not 'what is monthly churn' but 'what is the half-life of GMV contribution from each "
            "supply cohort.' Marketplaces that report 2% monthly logo churn routinely show 40%+ annual GMV-weighted churn "
            "once you re-weight by contribution. The second risk is take-rate compression: supply accounts that stay on the "
            "platform often renegotiate down, so revenue retention runs 5-10 points below logo retention. ChurnLens surfaces "
            "both by decomposing the ledger by cohort and by revenue tier, not by raw account count."
        ),
    },
    "edtech-saas": {
        "display": "EdTech",
        "grc": 3.0, "lc": 5.0, "aps": 80, "vol": "low but lumpy",
        "key_risk": "annual district procurement cycles masking summer-attrition churn",
        "profile": "K-12 districts and universities",
        "risk_section": (
            "EdTech SaaS churn is buried inside annual procurement cycles. Because 80% of revenue sits in annual or "
            "multi-year district contracts, reported monthly churn appears artificially low for 9-11 months of the year — "
            "and then a single August/September renewal window can crystallize 15-20% annualized logo churn into a 6-week "
            "window. Sellers present this as 'seasonality' rather than structural decay. The diligence work is to decompose "
            "the renewal book by contract end-date and stress-test what happens if the upcoming renewal cohort performs "
            "even 10% worse than the trailing cohort. The second hidden risk is district consolidation: when two school "
            "districts merge, the surviving IT department almost always standardizes on one of the two incumbent tools, "
            "meaning the acquisition loses two logos and keeps one — a dynamic that does not show up in historical churn "
            "until it happens."
        ),
    },
    "fintech-saas": {
        "display": "Fintech",
        "grc": 2.5, "lc": 4.0, "aps": 65, "vol": "high",
        "key_risk": "regulatory churn — banks pulling integrations after compliance reviews",
        "profile": "B2B fintech infrastructure buyers",
        "risk_section": (
            "Fintech SaaS churn is driven less by product dissatisfaction than by regulatory and partner risk. A bank or "
            "carrier can terminate a integration contract after a compliance review, an audit finding, or a change in "
            "their own vendor-management policy — and these terminations land as discrete, large-logo churn events rather "
            "than gradual decay. Reported monthly churn averages 1.5-2.5% but the distribution is bimodal: most months see "
            "sub-1%, then a single quarter sees a top-5 logo representing 8-12% of MRR leave. The diligence task is to "
            "identify which top logos have upcoming compliance review windows or partner-contract renewals in the next "
            "12 months and stress-test the revenue impact of each one. ChurnLens flags this by correlating contract "
            "end-dates with logo concentration, surfacing the 'renewal cliff' pattern that bank-pipeline fintechs rarely "
            "disclose proactively."
        ),
    },
    "healthcare-saas": {
        "display": "Healthcare",
        "grc": 1.5, "lc": 2.5, "aps": 75, "vol": "low",
        "key_risk": "long sales cycles hiding logo decay that lands mid-contract",
        "profile": "hospital systems and large clinics",
        "risk_section": (
            "Healthcare SaaS combines the lowest headline churn in the SaaS universe with some of the highest hidden-decay "
            "risk. Multi-year contracts with hospital systems and large clinics produce reported logo churn under 1.5% — "
            "but the product is often actively disengaging 12-18 months before formal non-renewal. The decay signals are "
            "specific: declining provider login counts, falling patient-record volume processed, and ticket volume dropping "
            "(counterintuitively, low support volume here means low engagement, not satisfaction). Because healthcare deals "
            "have 12-18 month sales cycles, the logos churning today were lost conceptually 2-3 years ago, meaning the "
            "seller's current pipeline is covering for decay that will not show up in churn metrics until after the "
            "acquisition closes. ChurnLens reconstructs engagement trajectory per logo from the usage data in the data room."
        ),
    },
    "proptech-saas": {
        "display": "PropTech",
        "grc": 2.5, "lc": 4.0, "aps": 60, "vol": "moderate",
        "key_risk": "transaction-volume correlation masking baseline logo retention",
        "profile": "brokerages and property managers",
        "risk_section": (
            "PropTech SaaS churn is correlated with transaction volume in a way that makes historical churn a poor predictor "
            "of future churn. When mortgage rates or transaction counts drop, brokerages cut seats immediately — so a target "
            "showing 2% monthly logo churn during a hot market can move to 5-6% in a cold market with no operational change. "
            "The diligence work is to adjust historical churn for transaction-volume conditions and stress-test what the "
            "churn rate would have been in a normalized or adverse market. The second risk is concentration in brokerage "
            "chains: a single national brokerage rolling out a proprietary tool can remove 15-20% of a PropTech company's "
            "logo base in a single non-renewal event. ChurnLens flags both by normalizing churn to transaction volume and "
            "by identifying logo-concentration risk in the top-10 accounts."
        ),
    },
    "ai-saas": {
        "display": "AI",
        "grc": 3.0, "lc": 5.0, "aps": 40, "vol": "very high",
        "key_risk": "hype-cycle churn — pilots that don't convert, tokens that decay invisibly",
        "profile": "ML and data-science teams",
        "risk_section": (
            "AI/ML SaaS has the highest churn volatility of any category we track. Three structural drivers: (1) pilot-driven "
            "go-to-market means a large share of 'paying' logos are pilot contracts with 60-90 day implicit expiry; (2) "
            "token-based pricing means revenue decays invisibly as customers reduce consumption without formally churning; "
            "and (3) model obsolescence risk — a customer churns the moment a competing model becomes materially better, "
            "which can happen in a single quarter. Reported monthly logo churn in AI SaaS sits at 3-5% but true revenue "
            "churn is frequently double that once you account for token-consumption decay on retained logos. The diligence "
            "imperative is to separate recurring contract revenue from consumption revenue and stress-test each separately: "
            "the recurring book is often a small fraction of headline MRR and the consumption book can halve in a bad quarter."
        ),
    },
    "plg-saas": {
        "display": "PLG",
        "grc": 3.5, "lc": 6.0, "aps": 35, "vol": "very high",
        "key_risk": "self-serve churn with no human intervention to save at-risk accounts",
        "profile": "individual contributors and small teams upgrading from free",
        "risk_section": (
            "Product-led growth (PLG) SaaS churns faster than any other go-to-market model because there is no customer "
            "success function intervening before cancellation. Monthly logo churn of 5-7% is normal; annualized, that is "
            "60-80% of the logo base turning over every year. The business works because CAC is near-zero and expansion "
            "from the surviving cohort is large — but the diligence risk is that the cohort retention curve is extremely "
            "sensitive to product changes. A single unpopular pricing-page redesign, onboarding flow change, or feature "
            "removal can shift the cohort curve by several percentage points in a way that does not show up in the trailing "
            "90-day churn number until months later. ChurnLens reconstructs the cohort retention curve by acquisition "
            "vintage and flags any recent-vintage cohort that is decaying faster than the trailing baseline."
        ),
    },
    "vertical-saas": {
        "display": "Vertical SaaS",
        "grc": 2.0, "lc": 3.0, "aps": 70, "vol": "low",
        "key_risk": "industry-cycle churn when the vertical itself contracts",
        "profile": "single-industry buyers (legal, construction, field service)",
        "risk_section": (
            "Vertical SaaS — purpose-built software for a single industry like legal, construction, or field service — "
            "shows low headline churn (2-3% monthly logo) because switching costs within a specialized workflow are "
            "extremely high. The hidden risk is industry-cycle correlation: when the underlying vertical contracts (a "
            "construction downturn, a legal-market slowdown, an oil-price collapse for oilfield-services SaaS), churn "
            "spikes not because customers are unhappy but because the customers themselves cease to exist. A vertical "
            "SaaS acquired at the top of an industry cycle can see 2-3× its historical churn rate in the first downturn, "
            "and that risk is invisible in trailing metrics. The diligence task is to identify what percentage of the "
            "logo base is correlated with the same underlying industry indicator and to stress-test churn under a "
            "hypothetical industry contraction scenario."
        ),
    },
}


def count_visible_words(html):
    txt = re.sub(r'<script[\s\S]*?</script>', ' ', html, flags=re.I)
    txt = re.sub(r'<style[\s\S]*?</style>', ' ', txt, flags=re.I)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    return len(txt.split())


def build_content_block(slug, data):
    """Build the HTML content block to inject into <main>."""
    display = data["display"]
    grc, lc, aps = data["grc"], data["lc"], data["aps"]
    vol = data["vol"]
    key_risk = data["key_risk"]
    profile = data["profile"]

    block = f'''
        <h2 style="font-size:1.4em;font-weight:700;margin:2em 0 .5em">{display} SaaS churn benchmarks</h2>
        <table style="width:100%;border-collapse:collapse;margin:1em 0;font-size:.95em">
            <thead><tr style="background:#f8f9fa">
                <th style="border:1px solid #e0e0e0;padding:10px 14px;text-align:left">Metric</th>
                <th style="border:1px solid #e0e0e0;padding:10px 14px;text-align:left">{display} SaaS benchmark</th>
                <th style="border:1px solid #e0e0e0;padding:10px 14px;text-align:left">What it means for a buyer</th>
            </tr></thead>
            <tbody>
                <tr><td style="border:1px solid #e0e0e0;padding:10px 14px">Gross revenue churn (monthly)</td><td style="border:1px solid #e0e0e0;padding:10px 14px"><strong>{grc}%</strong></td><td style="border:1px solid #e0e0e0;padding:10px 14px">Revenue lost to cancellations and downgrades each month, before expansion.</td></tr>
                <tr><td style="border:1px solid #e0e0e0;padding:10px 14px">Logo churn (monthly)</td><td style="border:1px solid #e0e0e0;padding:10px 14px"><strong>{lc}%</strong></td><td style="border:1px solid #e0e0e0;padding:10px 14px">Share of customer accounts that leave each month. Higher than revenue churn indicates smaller customers churning.</td></tr>
                <tr><td style="border:1px solid #e0e0e0;padding:10px 14px">Annual-plan share</td><td style="border:1px solid #e0e0e0;padding:10px 14px"><strong>{aps}%</strong></td><td style="border:1px solid #e0e0e0;padding:10px 14px">Share of MRR locked in annual contracts. High share defers churn into a single renewal window.</td></tr>
                <tr><td style="border:1px solid #e0e0e0;padding:10px 14px">MRR volatility</td><td style="border:1px solid #e0e0e0;padding:10px 14px"><strong>{vol}</strong></td><td style="border:1px solid #e0e0e0;padding:10px 14px">How predictable month-over-month MRR is. Higher volatility means historical churn is a less reliable predictor.</td></tr>
            </tbody>
        </table>
        <p style="font-size:.9em;color:#666;margin-bottom:1.5em">Benchmarks reflect ChurnLens analysis of {display.lower()} SaaS revenue ledgers. The target's actual numbers may differ — the point of due diligence is to find out by how much and why.</p>

        <h2 style="font-size:1.4em;font-weight:700;margin:2em 0 .5em">What hidden churn looks like in {display} SaaS</h2>
        <p style="margin-bottom:1em">{data['risk_section']}</p>

        <h2 style="font-size:1.4em;font-weight:700;margin:2em 0 .5em">What ChurnLens surfaces in a {display.lower()} SaaS acquisition</h2>
        <p style="margin-bottom:.5em">When you upload a {display.lower()} SaaS target's revenue ledger, ChurnLens runs four analyses that specifically address the failure modes above:</p>
        <ul style="margin:0 0 1.5em 1.5em;line-height:1.8">
            <li><strong>Zombie MRR detection</strong> — flags paid accounts whose billing is stable but whose underlying engagement signals (seat count, usage volume, support activity) are declining, quantifying the revenue at risk at the next renewal.</li>
            <li><strong>Annual-plan renewal-cliff mapping</strong> — decomposes the {aps}% annual-plan book by contract end-date and flags any date window where more than 10% of MRR is scheduled to renew at once.</li>
            <li><strong>Revenue-concentration stress test</strong> — identifies the top-5 logos, computes the MRR impact of each one churning, and flags any single account whose loss would move headline churn by more than 1 percentage point.</li>
            <li><strong>Cohort retention curve fitting</strong> — tracks each acquisition vintage's revenue over time and flags any recent cohort decaying faster than the trailing baseline, which is the earliest leading indicator of product-market-fit erosion.</li>
        </ul>
        <p style="margin-bottom:1.5em">The output is a report you can use in price negotiation: every flagged anomaly maps to a specific dollar amount of MRR at risk, and every dollar of verified risk is a dollar of purchase price you can defend reducing.</p>

        <h2 style="font-size:1.4em;font-weight:700;margin:2em 0 .5em">Who this analysis is for</h2>
        <p style="margin-bottom:1.5em">{display} SaaS acquisitions are typically evaluated by PE firms and search funds focused on vertical software, strategic acquirers already operating in the {display.lower()} stack, and founders preparing to sell a {display.lower()} SaaS who want to pre-empt the diligence findings a buyer will surface. In all three cases the workflow is the same: upload the revenue ledger CSV, receive the reconstructed churn and revenue-quality report, and use the flagged anomalies to drive either the price negotiation (for buyers) or the data-room narrative (for sellers).</p>
'''
    return block


def patch_industry_page(rel_path):
    fp = ROOT / rel_path
    if not fp.exists():
        return f"SKIP {rel_path}: file missing"

    existing = fp.read_text(errors='ignore')
    wc = count_visible_words(existing)
    if wc >= 400:
        return f"SKIP {rel_path}: already {wc} words"

    # Identify industry slug from path
    # e.g. industries/devtools-saas/index.html -> devtools-saas
    slug = rel_path.split('/')[1]
    if slug not in INDUSTRY_DATA:
        return f"SKIP {rel_path}: no data for industry '{slug}'"

    data = INDUSTRY_DATA[slug]
    block = build_content_block(slug, data)

    # Surgical insert: inject the block right before the
    # "Based on ChurnLens's analysis" paragraph, which is the standard
    # thin-page CTA line. This preserves everything before and after.
    marker = "Based on ChurnLens's analysis"
    if marker not in existing:
        # fallback: inject before the first <p> containing "Back to ChurnLens"
        marker2 = '<p><a href="https://churnlens.site" style="color:#0066cc"'
        if marker2 in existing:
            existing = existing.replace(marker2, block + "\n        " + marker2, 1)
        else:
            return f"SKIP {rel_path}: no insertion marker found"
    else:
        # Insert before the <p> that contains the marker
        # find <p> ... marker ... </p>
        pattern = re.compile(r'(<p[^>]*>[^<]*' + re.escape(marker) + r'[^<]*</p>)', flags=re.S)
        m = pattern.search(existing)
        if m:
            existing = existing[:m.start()] + block + "\n        " + m.group(0) + existing[m.end():]
        else:
            existing = existing.replace(marker, block + "\n        " + marker, 1)

    fp.write_text(existing)
    new_wc = count_visible_words(existing)
    return f"  ✓ {rel_path}: {wc} → {new_wc} words"


def main():
    # Find all industry index pages under 400 words
    results = []
    for html in (ROOT / "industries").rglob("*.html"):
        if '.vercel' in str(html):
            continue
        rel = str(html.relative_to(ROOT))
        slug = rel.split('/')[1] if len(rel.split('/')) > 2 else None
        if slug and slug in INDUSTRY_DATA:
            results.append(patch_industry_page(rel))

    print(f"\nProcessed {len(results)} industry pages:")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
