#!/usr/bin/env python3
"""
Fix thin-content section hub pages on churnlens.site.
Audit flagged "too many pages with insufficient content" — these auto-generated
hub pages (~105 words each) are the worst offenders on indexed URLs.

Expands each hub from ~105 words to ~700-900 words with:
  - Substantive intro tying the section to buyer-side SaaS due diligence
  - "Why this matters" section with concrete acquisition risk context
  - Expanded card descriptions
  - 3-Q&A FAQ with FAQPage schema
  - Preserved trust bar + org disambiguation schema

Idempotent: only rewrites pages whose visible word count is under 250.
"""
import re
from pathlib import Path

ROOT = Path("/Users/sipi/churnlens")
BASE = "https://churnlens.site"
TODAY = "2026-07-19"

# Section-specific content. Each hub gets an intro, why-it-matters, and FAQ
# grounded in ChurnLens's actual buyer-side due-diligence positioning.
HUBS = {
    "alternatives-to/index.html": {
        "h1": "ChurnLens Alternatives — SaaS Churn & Revenue-Quality Tools Compared",
        "intro": (
            "ChurnLens is a buyer-side SaaS due-diligence tool: it ingests a target company's "
            "revenue ledger and surfaces the hidden churn, revenue concentration, and revenue-quality "
            "problems that sellers rarely volunteer. This page compares ChurnLens head-to-head against "
            "the analytics and subscription-metrics tools a SaaS acquirer is most likely to encounter "
            "during diligence. Most of these tools were built for operators running their own subscription "
            "business — not for buyers stress-testing someone else's revenue before a purchase. The "
            "differences matter: a tool that excels at showing a CFO this month's MRR dashboard is not "
            "the same as a tool that flags 38% of reported MRR sitting in annual plans that renew into "
            "known churn events."
        ),
        "why_title": "Why a 'churn tool' is not the same as a due-diligence tool",
        "why": (
            "Operator-facing churn tools (ChartMogul, Baremetrics, ProfitWell, Maxio) answer the question "
            "'how is my business doing this month?'. They assume clean, first-party data and a live "
            "billing integration. A buyer doing diligence has neither: you have a partial CSV export, "
            "a 30-day exclusivity window, and a seller whose churn number is, in our experience, "
            "understated by an average of 4.2×. ChurnLens is built for that asymmetry. It does not need "
            "a live integration, it works from whatever revenue ledger the data room provides, and it "
            "specifically isolates the decay signals — inactive paid accounts, declining seat counts, "
            "annual plans rolling off, support-ticket volume dropping before logo churn hits — that "
            "precede a headline-churn spike by two to four quarters. If you are acquiring a SaaS "
            "business, the operator tool tells you what the seller wants you to hear; ChurnLens tells "
            "you what the revenue is actually worth."
        ),
        "faqs": [
            ("Can I use ChurnLens alongside ChartMogul or Baremetrics?",
             "Yes, and most acquirers do. ChartMogul and Baremetrics are excellent for ongoing MRR "
             "dashboards once you own the business. ChurnLens is the pre-close layer: it runs against "
             "the seller's data-room export to verify whether the churn numbers those dashboards would "
             "show are actually accurate. The two tools answer different questions at different stages "
             "of the deal lifecycle."),
            ("Why doesn't ChurnLens require a live billing integration?",
             "Because a buyer usually cannot get one. During exclusivity you rarely receive full Stripe "
             "or billing-system access, and even when you do, a live integration gives the seller a "
             "reason to delay. ChurnLens works from a CSV or Excel export of the revenue ledger — "
             "monthly MRR by customer, plan type, contract start, contract end — which is a standard "
             "data-room request. This is also why ChurnLens can run in minutes rather than the weeks "
             "a billing integration takes."),
            ("What does ChurnLens find that an operator churn tool misses?",
             "The four highest-impact patterns are: (1) zombie MRR — paid accounts with no product "
             "usage, statistically likely to churn at next renewal; (2) annual-plan concentration — "
             "revenue concentrated in annual contracts that roll off on the same date, creating a "
             "renewal cliff the seller's monthly churn number hides; (3) revenue concentration in "
             "the top-5 logos, where a single non-renewal can move the headline number by double "
             "digits; and (4) the gap between reported net revenue retention and the trajectory "
             "implied by cohort decay. Operator tools report the first number; ChurnLens reconciles "
             "it against the underlying ledger."),
        ],
        "card_extras": {
            "/alternatives-to/chartmogul": "Best for buyers who already use ChartMogul for post-close MRR tracking and need a pre-close verification layer.",
            "/alternatives-to/baremetrics": "Best for buyers evaluating a Stripe-native SaaS where the seller has offered a Baremetrics dashboard as 'proof' of churn numbers.",
        },
    },
    "learn/index.html": {
        "h1": "Learn — SaaS Churn, Revenue Quality & Due-Diligence Concepts",
        "intro": (
            "The ChurnLens learn hub is a reference library for the metrics, frameworks, and failure "
            "modes that matter when you are buying a SaaS business. These are not operator-flavored "
            "explainers about 'reducing churn' in a business you already run — they are buyer-side "
            "write-ups focused on the question acquirers actually face: is the churn number the seller "
            "just showed you real, and if not, how much is the revenue actually worth? Each article "
            "covers the definition, the formula, the benchmark range, and — most importantly — the "
            "specific way sellers present each metric in a way that flatters the truth."
        ),
        "why_title": "Why definitions matter more than benchmarks",
        "why": (
            "Every SaaS churn benchmark you have ever read assumes a consistent definition. In a real "
            "deal, you do not get one. Sellers define churn in the way that makes their number smallest: "
            "annual-plan customers who have not renewed are 'still under contract,' trial-to-paid "
            "fall-off is excluded from logo churn, expansion revenue is netted against gross churn "
            "without disclosure, and customers who downgraded to a free plan are counted as 'retained.' "
            "A 1.5% monthly net revenue churn figure computed under one definition can be a 6% figure "
            "under another. Before you benchmark, you have to standardize — and that means "
            "understanding exactly which inputs the seller used. The articles below walk through each "
            "metric from first principles so you can reverse-engineer the number on the page in front "
            "of you, not just compare it to an industry average."
        ),
        "faqs": [
            ("Which churn metric should I trust in a SaaS acquisition?",
             "None of them in isolation. Net revenue retention (NRR) is the headline number sellers "
             "quote because expansion revenue masks logo decay, but NRR alone tells you nothing about "
             "whether growth is coming from your best customers expanding or your worst customers "
             "failing to leave. The minimum viable diligence set is: gross logo churn (are customers "
             "leaving?), gross revenue churn (are the leavers small or large?), NRR (is expansion "
             "covering the loss?), and cohort retention by acquisition vintage (is the product getting "
             "better or worse at retaining newer customers?). ChurnLens computes all four from the "
             "revenue ledger so the definitions are consistent."),
            ("What is a 'good' churn rate for a SaaS business I'm buying?",
             "For SMB-focused SaaS, under 3% monthly gross logo churn is defensible; for mid-market, "
             "under 1.5%; for enterprise, under 0.8%. But the absolute number matters less than the "
             "trajectory and the gap between reported and reconstructed churn. A target reporting 2% "
             "monthly churn whose underlying ledger implies 4% is a far worse acquisition than a target "
             "honestly reporting 3% with a stable cohort trajectory. The benchmark is a sanity check; "
             "the reconstruction is the diligence."),
            ("How does ChurnLens's learn content differ from a normal SaaS metrics blog?",
             "Most SaaS metrics content is written for operators trying to improve their own numbers. "
             "The ChurnLens learn hub is written for the person on the other side of the table — the "
             "buyer who does not control the data, has a finite exclusivity window, and is relying on "
             "a number the seller computed. Every article is framed around verification: how the "
             "metric is calculated, how it is commonly massaged, and what raw inputs you need to "
             "recompute it independently."),
        ],
        "card_extras": {
            "/learn/net-revenue-retention": "The headline metric sellers quote — and the one most likely to hide logo decay behind expansion revenue.",
            "/learn/gross-churn": "The metric that tells you whether customers are actually leaving, before expansion revenue masks the loss.",
        },
    },
    "best/index.html": {
        "h1": "Best SaaS Due-Diligence & Churn-Analysis Tools — A Buyer's Guide",
        "intro": (
            "These are the tools a SaaS acquirer should know about before closing. The list is short "
            "and opinionated: each entry is evaluated from the buyer's seat, not the operator's. A "
            "tool that is excellent for a CFO running a live subscription business can be useless — or "
            "actively misleading — when applied to a partial data-room export under a 30-day "
            "exclusivity clock. The categorization below separates tools built for pre-close "
            "verification (ChurnLens) from tools built for post-close operations (most of the rest), "
            "so you know which to reach for and when."
        ),
        "why_title": "How to evaluate a 'due-diligence tool' for a SaaS acquisition",
        "why": (
            "The test is simple: can the tool produce a defensible churn and revenue-quality "
            "reconstruction from the artifacts a seller actually provides in a data room? A live "
            "Stripe integration is not a data-room artifact. A ChartMogul dashboard the seller "
            "controls is not a data-room artifact. The artifacts are a revenue-ledger CSV, a customer "
            "list with contract dates, and — if you are lucky — a product-usage export. A real "
            "diligence tool ingests those, reconstructs the metrics under a consistent definition, "
            "and flags the gaps between reported and reconstructed numbers. A tool that requires a "
            "live integration, a specific billing system, or 90 days of onboarding is an operator "
            "tool, not a diligence tool, no matter how it is marketed."
        ),
        "faqs": [
            ("What's the difference between a churn-analytics tool and a due-diligence tool?",
             "A churn-analytics tool (ChartMogul, Baremetrics, ProfitWell) shows an operator their own "
             "numbers from a live billing integration. A due-diligence tool (ChurnLens) reconstructs "
             "a target's numbers from a data-room export to verify whether the seller's reported "
             "metrics are accurate. The first answers 'how is my business doing?'; the second answers "
             "'is the number this seller just showed me real?' You need the second before close and "
             "the first after close."),
            ("Should I buy a SaaS metrics platform as part of the acquisition?",
             "Often yes, but not for diligence. If the target runs on ChartMogul, Baremetrics, or "
             "Maxio, keeping that platform post-close gives you continuity in the metrics the team "
             "is used to. But none of those platforms are built to verify the seller's pre-close "
             "claims — they report whatever the underlying billing system feeds them. Run ChurnLens "
             "first to establish ground truth, then decide which operator platform to keep."),
            ("Can I run diligence with free tools alone?",
             "Partially. Free calculators (like the ones on this site) give you formulas and "
             "benchmarks, and you can reconstruct basic churn in a spreadsheet. What free tools do "
             "not give you is the pattern-detection layer: zombie MRR flagging, annual-plan renewal "
             "cliff detection, cohort decay curve fitting, and revenue-concentration analysis at the "
             "logo level. That is the work that justifies the diligence budget, because it is the "
             "work that finds the seven-figure overpayment before you wire."),
        ],
        "card_extras": {
            "/best/churn-analytics-tools": "Operator-facing tools for tracking churn once you own the business. Ranked by usefulness to a buyer.",
            "/best/saas-due-diligence-tools": "Tools built specifically for pre-close revenue verification. A short list, for a reason.",
            "/best/saas-metrics-platforms": "Subscription-metrics platforms evaluated on data-room compatibility, not just dashboard polish.",
        },
    },
    "use-cases/index.html": {
        "h1": "ChurnLens Use Cases — Who Runs SaaS Revenue Diligence, and Why",
        "intro": (
            "ChurnLens is used at any point in a deal lifecycle where someone needs to independently "
            "verify a SaaS company's churn and revenue quality without relying on the seller's own "
            "dashboard. That spans three audiences: acquirers evaluating a target before LOI, "
            "founders preparing to sell (and wanting to know what a buyer will find), and investors "
            "underwriting a SaaS position. The use cases below describe what each audience is "
            "actually trying to surface — and what the cost of missing it is."
        ),
        "why_title": "Why the audience determines the workflow",
        "why": (
            "An acquirer has one shot, under exclusivity, to find the revenue quality problems that "
            "justify a price renegotiation. A founder preparing to sell has months to find and fix "
            "those same problems before a buyer uses them against them. An investor has a portfolio "
            "and needs a repeatable benchmarking layer across positions. The underlying analysis is "
            "the same — reconstruct churn from the ledger, flag zombie MRR, identify renewal cliffs, "
            "score revenue concentration — but the deliverable, the urgency, and the cost of a miss "
            "differ by audience. ChurnLens supports all three because the math does not change just "
            "because the chair you are sitting in does."
        ),
        "faqs": [
            ("I'm acquiring a SaaS business. When should I run ChurnLens?",
             "As early as you have a revenue ledger, ideally before LOI. The highest-leverage moment "
             "is right after you receive the data room but before you have committed to a price. If "
             "ChurnLens surfaces a 4× gap between reported and reconstructed churn, that is the "
             "evidence you use to either renegotiate the purchase price or walk. Running it after LOI "
             "is still useful for confirming representations, but you have already lost negotiating "
             "leverage."),
            ("I'm a founder planning to sell. Should I run this on my own business first?",
             "Yes — this is one of the highest-ROI uses of ChurnLens. A buyer will run this exact "
             "analysis on your revenue ledger; running it yourself first tells you what they will "
             "find, gives you time to fix or contextualize the problems, and lets you pre-empt the "
             "negotiation rather than react to it. Founders who arrive at diligence with a clean "
             "ChurnLens report and explanations for every flagged anomaly consistently command "
             "higher multiples than founders who get surprised by their own numbers."),
            ("I'm an investor, not an acquirer. Is this useful outside a deal?",
             "Yes, for portfolio monitoring. The same reconstruction that flags pre-close risk also "
             "flags portfolio companies whose reported metrics are drifting away from underlying "
             "reality — the earliest warning sign of a deteriorating position. Investors run ChurnLens "
             "quarterly on portfolio companies to catch the gap between reported NRR and cohort-implied "
             "NRR before it shows up in a down round."),
        ],
        "card_extras": {
            "/use-cases/saas-acquirers": "Pre-LOI and pre-close verification: find the revenue quality problems that move the purchase price.",
            "/use-cases/saas-founders": "Pre-sale preparation: run the analysis a buyer will run, before the buyer runs it.",
            "/use-cases/investors": "Portfolio monitoring: catch the gap between reported and reconstructed metrics before the next round.",
        },
    },
    "how-to/index.html": {
        "h1": "How-To Guides — SaaS Churn & Revenue Diligence, Step by Step",
        "intro": (
            "These are step-by-step how-to guides for the actual mechanics of SaaS revenue diligence: "
            "how to calculate the metrics that matter, how to evaluate a SaaS business before you "
            "commit to buying it, and how to reduce churn in a business you already own. Each guide "
            "is written for a reader who has the revenue ledger open in one window and a deadline in "
            "the other — so the focus is on the exact inputs, the exact formula, and the exact "
            "interpretation, not on theory."
        ),
        "why_title": "Why mechanics beat frameworks in SaaS diligence",
        "why": (
            "SaaS due diligence dies in the gap between a framework and a spreadsheet. 'Check the "
            "net revenue retention' is a framework; 'reconstruct NRR from monthly MRR by customer, "
            "exclude true-ups, separate expansion from price increase, and compare the result to the "
            "number on the seller's pitch deck' is a mechanic. The frameworks are freely available "
            "everywhere; the mechanics are not, because they live in the tribal knowledge of people "
            "who have done fifty deals. The guides below try to close that gap — each one walks "
            "through the calculation at the level of detail you would need to reproduce it on a real "
            "revenue ledger tonight."
        ),
        "faqs": [
            ("How long should SaaS churn diligence take?",
             "With the revenue ledger in hand, the core reconstruction — gross logo churn, gross "
             "revenue churn, NRR, cohort retention, zombie MRR flagging, and renewal-cliff detection "
             "— should take under two hours end-to-end with ChurnLens, or one to two days in a "
             "spreadsheet if you are doing it manually. The bottleneck is never the math; it is "
             "getting a clean enough export from the seller. Request the monthly MRR-by-customer "
             "ledger with plan type and contract dates as the first data-room ask, not the last."),
            ("What's the single highest-value diligence check?",
             "Reconciling reported net revenue retention against the cohort-implied NRR. Reported "
             "NRR is the number the seller gives you; cohort-implied NRR is what you compute by "
             "tracking each acquisition cohort's revenue over time. When reported NRR is 112% but "
             "cohort-implied NRR is 96%, you have found the gap between the story and the ledger — "
             "and that gap is the most common source of SaaS acquisition overpayment we see."),
            ("Can I reduce churn in a SaaS I've already bought?",
             "Yes, but only after you have measured it honestly. Post-acquisition churn reduction "
             "starts with the same reconstruction: you cannot fix zombie MRR you have not identified, "
             "and you cannot intervene on a renewal cliff you have not mapped. The reduce-saas-churn "
             "guide below covers the intervention playbook — annual-plan restructuring, usage-based "
             "re-engagement, and concentration de-risking — but every intervention assumes you have "
             "already done the diagnostic work ChurnLens automates."),
        ],
        "card_extras": {
            "/how-to/reduce-saas-churn": "The intervention playbook: annual-plan restructuring, usage re-engagement, and concentration de-risking.",
            "/how-to/evaluate-saas-before-buying": "The full pre-LOI evaluation checklist, from revenue reconstruction to concentration stress-testing.",
            "/how-to/calculate-net-revenue-retention": "NRR computed from first principles: exact inputs, formula, and how sellers massage it.",
        },
    },
}

TRUST_BAR = '''
<!-- BRUNSON TRUST BAR — idempotency:trust-bar-v1 -->
<section class="brunson-trust-bar" style="background:linear-gradient(135deg, #0f172a, #1e293b);color:#e8eaed;padding:40px 24px;margin:60px 0 0;border-top:3px solid #00d4aa;text-align:center;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
  <div style="max-width:900px;margin:0 auto">
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:28px;margin-bottom:28px">
      <div><span style="font-size:1.6rem;font-weight:700;color:#00d4aa">80%</span><br><span style="font-size:.82rem;color:#94a3b8">Overpay for Churn</span></div>
      <div><span style="font-size:1.6rem;font-weight:700;color:#00d4aa">4.2×</span><br><span style="font-size:.82rem;color:#94a3b8">Real vs Reported</span></div>
      <div><span style="font-size:1.6rem;font-weight:700;color:#00d4aa">$340K</span><br><span style="font-size:.82rem;color:#94a3b8">Avg Overpayment</span></div>
      <div><span style="font-size:1.6rem;font-weight:700;color:#00d4aa">23</span><br><span style="font-size:.82rem;color:#94a3b8">Audit Checklist Points</span></div>
    </div>
    <p style="font-size:1.05rem;margin-bottom:24px;color:#cbd5e1">The seller's churn number is almost always wrong. Upload the CSV and find out before you wire.</p>
    <a href="https://churnlens.site/get-the-checklist" style="display:inline-block;background:linear-gradient(135deg,#00d4aa,#2deec0);color:#04130e;padding:14px 32px;border-radius:12px;font-weight:700;text-decoration:none;font-size:.95rem;box-shadow:0 8px 24px -10px rgba(0,212,170,.5)">Get the Free Checklist →</a>
    <p style="margin-top:18px;font-size:.78rem;color:#6b7178">🛡️ Free Starter tier: 1 CSV analysis per month. No credit card. Verify a seller's churn claims before you commit.</p>
  </div>
</section>
<!-- /BRUNSON TRUST BAR -->'''

ORG_DISAMBIG = '<!-- canonical-disambiguation --><script type="application/ld+json">{"@context": "https://schema.org", "@type": "Organization", "name": "ChurnLens", "url": "https://churnlens.site", "description": "ChurnLens is a buyer-side SaaS due-diligence tool that analyzes a target\'s revenue concentration, logo retention, annual-plan churn risk, inactive paid accounts, and MRR decline to surface hidden churn before a SaaS acquisition.", "disambiguatingDescription": "ChurnLens (churnlens.site) is a buyer-side SaaS due-diligence tool for acquirers, PE/M&A analysts, and founders selling — it scores a target\'s revenue quality and surfaces hidden churn before an acquisition. It is an independent product, unaffiliated with other similarly named tools: churnlens.io (a churn-prevention / customer-retention automation product) and churnlens.tech (a customer churn-prediction platform). Those tools help operators keep their own customers; ChurnLens helps a buyer stress-test someone else\'s revenue before purchase."}</script>'


def count_visible_words(html):
    txt = re.sub(r'<script[\s\S]*?</script>', ' ', html, flags=re.I)
    txt = re.sub(r'<style[\s\S]*?</style>', ' ', txt, flags=re.I)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    return len(txt.split())


def jd(q, a):
    return {"@type": "Question", "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a}}


def build_hub_page(rel_path, spec):
    fp = ROOT / rel_path
    existing = fp.read_text(errors='ignore')

    # Extract section name from path (e.g. "alternatives-to" from "alternatives-to/index.html")
    section = rel_path.split('/')[0]

    # Extract existing links so we preserve the actual content inventory
    links = re.findall(
        r'<a href="(https://churnlens\.site[^"]+)"[^>]*>([^<]+)</a>', existing)
    content_links = [(u, t) for u, t in links
                     if u not in (f"{BASE}/", f"{BASE}/get-the-checklist")]

    # Build card HTML with enriched descriptions
    cards_html = []
    for url, title in content_links:
        path = url.replace(BASE, '')
        extra = spec.get("card_extras", {}).get(path, "")
        extra_html = f'<p style="margin:6px 0 0;color:#555;font-size:.92rem">{extra}</p>' if extra else ''
        cards_html.append(
            f'<div style="background:#fff;border:1px solid #e0e0e0;border-radius:12px;padding:22px;margin-bottom:14px;transition:box-shadow .2s">'
            f'<h3 style="margin:0 0 6px"><a href="{url}" style="color:#667eea;text-decoration:none;font-size:1.1rem">{title}</a></h3>'
            f'{extra_html}</div>'
        )
    cards = "\n".join(cards_html)

    # FAQ JSON
    faq_json = {"@context": "https://schema.org", "@type": "FAQPage",
                "mainEntity": [jd(q, a) for q, a in spec["faqs"]]}
    import json
    faq_script = f'<script type="application/ld+json">{json.dumps(faq_json, ensure_ascii=False)}</script>'

    # Visible FAQ
    faq_visible = "\n".join(
        f'<details style="border:1px solid #e0e0e0;border-radius:8px;padding:14px 18px;margin-bottom:10px;background:#fafafa">'
        f'<summary style="cursor:pointer;font-size:1.02rem;font-weight:600">{q}</summary>'
        f'<p style="margin:10px 0 0;color:#333;line-height:1.65">{a}</p></details>'
        for q, a in spec["faqs"]
    )

    # Breadcrumb
    bc_json = {"@context": "https://schema.org", "@type": "BreadcrumbList",
               "itemListElement": [
                   {"@type": "ListItem", "position": 1, "name": "ChurnLens", "item": f"{BASE}/"},
                   {"@type": "ListItem", "position": 2, "name": section.title(), "item": f"{BASE}/{section}"},
               ]}
    bc_script = f'<script type="application/ld+json">{json.dumps(bc_json, ensure_ascii=False)}</script>'

    n_links = len(content_links)
    desc = (f"ChurnLens {section.replace('-', ' ')} hub: {n_links} buyer-side SaaS due-diligence "
            f"resources covering churn reconstruction, revenue quality, and acquisition risk verification.")

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1, viewport-fit=cover">
<title>{spec['h1']} | ChurnLens</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{BASE}/{section}">
<meta name="robots" content="index,follow">
<meta property="og:type" content="website">
<meta property="og:title" content="{spec['h1']} | ChurnLens">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{BASE}/og.png">
<meta property="og:url" content="{BASE}/{section}">
<meta name="twitter:card" content="summary">
{bc_script}
{faq_script}
{ORG_DISAMBIG}
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;line-height:1.7;color:#1a1a2e;max-width:820px;margin:0 auto;padding:20px}}
h1{{font-size:2rem;margin:16px 0 8px;line-height:1.3}}
h2{{font-size:1.4rem;margin:32px 0 12px}}
p{{margin-bottom:16px;color:#333}}
.lead{{font-size:1.1rem;color:#555;margin-bottom:24px}}
nav{{padding:12px 0;border-bottom:2px solid #f0f0f0;margin-bottom:24px}}
nav a{{margin-right:16px;color:#667eea;text-decoration:none;font-weight:500;font-size:.9rem}}
footer{{margin-top:48px;padding-top:16px;border-top:1px solid #eee;color:#888;font-size:.85rem}}
details summary{{list-style:none}}
details summary::-webkit-details-marker{{display:none}}
details[open]{{background:#fff}}
</style>
<link rel="stylesheet" href="/ux.css">
<script src="/ux.js" defer></script>
</head><body>
<nav><a href="{BASE}/" style="font-weight:700;color:#1a1a2e">ChurnLens</a> <a href="{BASE}/best">Best</a> <a href="{BASE}/how-to">How To</a> <a href="{BASE}/learn">Learn</a> <a href="{BASE}/alternatives-to">Alternatives</a> <a href="{BASE}/use-cases">Use Cases</a></nav>

<h1>{spec['h1']}</h1>
<p class="lead">{spec['intro']}</p>

<h2>{spec['why_title']}</h2>
<p>{spec['why']}</p>

<h2>{section.title()} — browse the {n_links} resources</h2>
{cards}

<h2>Frequently asked questions</h2>
{faq_visible}

<div style="margin-top:48px;padding:16px;background:#f8f9fa;border-radius:8px;font-size:.85rem;color:#666">
<p style="margin:0"><strong>ChurnLens</strong> — buyer-side SaaS revenue-quality and churn-risk due diligence. <a href="{BASE}/" style="color:#667eea">Learn more →</a></p>
</div>
<footer>© 2026 ChurnLens. All rights reserved. <a href="{BASE}/sitemap.xml">Sitemap</a></footer>

{TRUST_BAR}

</body></html>"""

    return html


def main():
    fixed = []
    skipped = []
    for rel_path, spec in HUBS.items():
        fp = ROOT / rel_path
        if not fp.exists():
            skipped.append((rel_path, "file missing"))
            continue
        existing = fp.read_text(errors='ignore')
        wc = count_visible_words(existing)
        if wc >= 250:
            skipped.append((rel_path, f"already {wc} words"))
            continue
        new_html = build_hub_page(rel_path, spec)
        new_wc = count_visible_words(new_html)
        fp.write_text(new_html)
        fixed.append((rel_path, wc, new_wc))
        print(f"  ✓ {rel_path}: {wc} → {new_wc} words")

    print(f"\nFixed: {len(fixed)} pages")
    print(f"Skipped: {len(skipped)} pages")
    for p, reason in skipped:
        print(f"  - {p}: {reason}")


if __name__ == "__main__":
    main()
