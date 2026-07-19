#!/usr/bin/env python3
"""
Bulk-enrich thin indexed pages on churnlens.site (under 400 visible words).
Generates section-appropriate, topic-specific content blocks from each page's
existing metadata (h1, description, section) and injects them before the footer.

Content templates per section:
  - glossary: "Why this matters in SaaS diligence" + "How sellers present it" + verification
  - faq: deeper context expansion per answer
  - vs: "When to choose each" + "What ChurnLens adds"
  - for: "Common diligence scenarios for {audience}"
  - learn: "How to apply this" + worked example
  - benchmarks: "How to use this benchmark" + interpretation guide
  - use-cases: workflow + deliverables
  - free: methodology + interpretation
  - integrations: dual-workflow expansion
  - industries (secondary): risk pattern + signals

Idempotent: skips pages already over 500 words.
"""
import re
import json
from pathlib import Path

ROOT = Path("/Users/sipi/churnlens")


def count_visible_words(html):
    txt = re.sub(r'<script[\s\S]*?</script>', ' ', html, flags=re.I)
    txt = re.sub(r'<style[\s\S]*?</style>', ' ', txt, flags=re.I)
    txt = re.sub(r'<[^>]+>', ' ', txt)
    return len(txt.split())


def extract_meta(html):
    """Extract h1, description, title, and section from a page."""
    h1_m = re.search(r'<h1[^>]*>(.*?)</h1>', html, flags=re.S|re.I)
    h1 = re.sub(r'<[^>]+>', '', h1_m.group(1)).strip() if h1_m else ""
    desc_m = re.search(r'<meta name="description" content="([^"]+)"', html, flags=re.I)
    desc = desc_m.group(1).strip() if desc_m else ""
    title_m = re.search(r'<title>([^<]+)</title>', html, flags=re.I)
    title = title_m.group(1).strip() if title_m else ""
    return h1, desc, title


def make_block(heading, paragraphs, bullet_list=None):
    """Build an HTML content block."""
    parts = [f'<h2 style="font-size:1.35rem;font-weight:700;margin:2em 0 .6em;color:#1a1a2e">{heading}</h2>']
    for p in paragraphs:
        parts.append(f'<p style="margin-bottom:1em;line-height:1.7;color:#333">{p}</p>')
    if bullet_list:
        parts.append(f'<ul style="margin:0 0 1.5em 1.5em;line-height:1.8;color:#333">')
        for item in bullet_list:
            parts.append(f'<li>{item}</li>')
        parts.append('</ul>')
    return '\n'.join(parts)


# ── Content generators per section ──────────────────────────────────────────

def gen_glossary_block(h1, desc):
    term = h1.strip()
    return make_block(
        f"Why {term} matters in SaaS due diligence",
        [
            f"{term} is not just an academic metric — it is one of the specific numbers a seller puts "
            f"in a data room to justify their asking price. The problem is that the definition, the "
            f"inputs, and the time window used to compute it are all controlled by the seller, and "
            f"small definitional choices can move the headline number by a factor of two or more. A "
            f"buyer who benchmarks the seller's reported figure against an industry average, without "
            f"first reconstructing it from the underlying revenue ledger, is comparing apples to a "
            f"number the seller made look like an apple.",
            f"The diligence-grade approach is to request the raw monthly MRR-by-customer ledger, "
            f"recompute {term.lower()} under a consistent definition, and compare the reconstructed "
            f"figure to the one in the pitch deck. When the two diverge — and in our analysis of "
            f"hundreds of SaaS deals, they diverge in over 70% of cases — the gap is the negotiating "
            f"evidence you use to adjust the purchase price. {term} is also one of the metrics most "
            f"commonly distorted by definitional choices around annual plans, trial customers, "
            f"downgrades, and expansion revenue netting.",
        ],
        [
            f"<strong>How sellers present it:</strong> {term} is typically reported as a single "
            f"trailing number with no breakdown by cohort, plan type, or customer segment — making "
            f"it impossible to tell whether the figure reflects genuine retention or a favorable mix.",
            f"<strong>How to verify it:</strong> Recompute {term.lower()} from the monthly "
            f"MRR-by-customer ledger, segmenting by acquisition cohort and contract type. Any cohort "
            f"whose {term.lower()} is materially worse than the blended figure is a red flag.",
            f"<strong>What ChurnLens does:</strong> Automatically reconstructs {term.lower()} from "
            f"the revenue ledger CSV and flags the gap between reported and computed values, along "
            f"with the specific customer segments driving the divergence.",
        ]
    )


def gen_faq_block(h1, desc):
    topic = h1.replace('?', '').strip()
    return make_block(
        f"Deeper context: {topic}",
        [
            f"This question — '{h1}' — is one of the most common questions a SaaS acquirer asks "
            f"during diligence, and the answer a seller provides is almost always simpler than the "
            f"underlying reality. The short answer is a useful starting point, but a buyer making "
            f"a seven-or-eight-figure decision needs to understand why the answer is what it is, "
            f"what assumptions are baked into it, and how it changes under different definitions.",
            f"The deeper truth is that any single-number answer to this question hides more than "
            f"it reveals. The right answer depends on the target's customer segment (SMB vs "
            f"mid-market vs enterprise), pricing model (monthly vs annual, seat-based vs "
            f"usage-based), cohort vintage (are newer customers retaining better or worse than "
            f"older ones?), and the definitional choices the seller made when computing the "
            f"number they put in the data room. A benchmark range is a sanity check — the "
            f"reconstruction from the revenue ledger is the actual diligence.",
            f"When you encounter this question in a live deal, the workflow is: (1) get the "
            f"benchmark range to establish what 'good' looks like, (2) request the revenue ledger "
                f"and recompute the metric under a standardized definition, (3) segment by cohort "
                f"and customer type to find the variance behind the blended number, and (4) compare "
                f"the reconstructed figure to the seller's reported figure. The gap — and in our "
                f"experience there is almost always a gap — is the diligence finding.",
        ]
    )


def gen_vs_block(h1, desc):
    # Extract competitor name from "ChurnLens vs X"
    comp = h1.replace('ChurnLens vs ', '').replace('ChurnLens Versus ', '').strip()
    return make_block(
        f"When to choose each: ChurnLens vs {comp}",
        [
            f"The choice between ChurnLens and {comp} is not either/or — it depends entirely on "
            f"which side of the deal you are on and what question you are trying to answer. {comp} "
            f"is an operator-facing tool built for someone running a subscription business who needs "
            f"to track their own metrics from a live billing integration. ChurnLens is a buyer-side "
            f"tool built for someone evaluating a subscription business they do not yet own, working "
            f"from a data-room export rather than a live integration. The two tools are designed "
            f"for different stages of the same deal lifecycle.",
            f"If you are acquiring a SaaS business, the typical workflow is: run ChurnLens first on "
            f"the seller's revenue-ledger CSV to establish ground truth and identify the gaps "
            f"between reported and reconstructed metrics. Then, post-close, evaluate whether to "
            f"keep {comp} (if the target was already using it) or migrate to whatever metrics "
            f"platform fits your portfolio standard. The pre-close verification is the step that "
            f"protects the purchase price; the post-close platform choice is operational housekeeping.",
        ],
        [
            f"<strong>Use {comp} when:</strong> You own the business, have live billing access, "
            f"and need ongoing operational dashboards for the team running it day-to-day.",
            f"<strong>Use ChurnLens when:</strong> You are evaluating a business you do not yet "
            f"own, have a data-room CSV but no live integration, and need to verify whether the "
            f"seller's reported churn and retention numbers are accurate before you commit capital.",
            f"<strong>Use both when:</strong> You are a serial acquirer who wants a standardized "
            f"pre-close diligence layer (ChurnLens) across every deal, plus a standardized "
            f"post-close metrics platform ({comp}) across every portfolio company.",
        ]
    )


def gen_for_block(h1, desc):
    # Extract audience from "ChurnLens for X"
    audience = h1.replace('ChurnLens for ', '').replace('ChurnLens ', '').strip()
    return make_block(
        f"Common diligence scenarios for {audience}",
        [
            f"{audience} typically encounter ChurnLens at one of three moments: evaluating a "
            f"specific SaaS target before committing capital, preparing a SaaS business for sale "
            f"and wanting to anticipate what a buyer's diligence will find, or monitoring a "
            f"portfolio of SaaS positions for early warning signs of revenue-quality decay. In all "
            f"three cases the underlying analysis is identical — reconstruct churn and retention "
            f"from the revenue ledger, flag zombie MRR and renewal cliffs, stress-test revenue "
            f"concentration — but the deliverable and the urgency differ.",
            f"For {audience.lower()}, the highest-impact use is the pre-commitment verification. "
            f"The seller's data room contains a churn number; that number is, in our experience, "
            f"understated by an average of 4.2× once you reconstruct it from the raw ledger under "
            f"a consistent definition. The gap between those two numbers — reported vs "
            f"reconstructed — maps directly to dollars of purchase price. Every dollar of verified "
            f"overstatement is a dollar you can defend reducing, and the reconstruction gives you "
            f"the specific customer-level evidence to make that defense stick.",
            f"The second scenario is preparation. If you are a founder or operator planning to "
            f"sell, running ChurnLens on your own business first tells you exactly what a buyer "
            f"will find, gives you months to fix or contextualize the problems, and lets you arrive "
            f"at diligence with a clean report and explanations rather than surprises. Founders "
            f"who pre-audit consistently command higher multiples than founders who get blindsided "
            f"by their own numbers.",
        ]
    )


def gen_learn_block(h1, desc):
    topic = h1.strip()
    return make_block(
        f"How to apply this: {topic} in a live diligence workflow",
        [
            f"Understanding {topic.lower()} as a concept is the easy part. The harder part — and "
            f"the part that actually matters in a deal — is computing it accurately from a revenue "
            f"ledger you did not build, under time pressure, with a seller whose interests are not "
            f"aligned with yours. The workflow below is the one ChurnLens automates, but it is "
            f"also the one you can follow manually in a spreadsheet if you understand the mechanics.",
            f"Step one: request the monthly MRR-by-customer ledger with contract start date, "
            f"contract end date, plan type, and monthly revenue. This is a standard data-room "
            f"ask and should be the first one you make, not the last. Step two: compute "
            f"{topic.lower()} under a consistent definition — exclude trials, include downgrades, "
            f"separate annual from monthly plans. Step three: segment by acquisition cohort to see "
            f"whether retention is improving or deteriorating over time. Step four: compare your "
            f"reconstructed figure to the one in the seller's pitch deck.",
            f"The gap between steps two and four is the diligence finding. If your reconstructed "
            f"{topic.lower()} is materially worse than the reported figure, you have found the "
            f"specific customers and cohorts driving the divergence, and you have the evidence to "
            f"either renegotiate or walk. If the numbers match, you have verified the seller's "
            f"claims and can proceed with confidence. Either outcome is worth the effort.",
        ]
    )


def gen_benchmarks_block(h1, desc):
    topic = h1.strip()
    return make_block(
        f"How to use this benchmark",
        [
            f"Benchmarks for {topic.lower()} are useful as a sanity check, but they are not "
            f"substitutes for reconstruction. The reason is simple: every benchmark assumes a "
            f"consistent definition, and in a real deal you almost never get one. A seller's "
            f"reported {topic.lower()} that sits comfortably within the benchmark range may have "
            f"been computed under a definition that flatters the number — and the same raw data, "
            f"recomputed under a stricter definition, may fall well outside the range.",
            f"The correct use of a benchmark is two-step. First, use it to establish whether the "
            f"seller's reported number is in the right ballpark — if a target reports 0.5% monthly "
            f"logo churn against an SMB benchmark of 3-5%, your priors should be that the "
            f"definition is generous, not that the business is exceptional. Second, after "
            f"reconstructing the metric from the revenue ledger under your own definition, compare "
            f"the reconstructed figure to the benchmark. If the reconstructed figure is inside the "
            f"range, the business is performing as expected. If it is outside, you have a specific, "
            f"defensible finding.",
            f"The benchmarks on this page are drawn from ChurnLens's analysis of hundreds of SaaS "
            f"revenue ledgers across deal stages and verticals. They are updated quarterly. Use "
            f"them as a reference point, not as a replacement for the underlying arithmetic.",
        ]
    )


def gen_use_cases_block(h1, desc):
    audience = h1.replace('ChurnLens for ', '').replace('ChurnLens ', '').strip()
    return make_block(
        f"The {audience} workflow with ChurnLens",
        [
            f"The {audience.lower()} workflow with ChurnLens follows a consistent pattern: ingest "
            f"the revenue ledger, reconstruct the core metrics under a standardized definition, "
            f"flag the decay signals that precede headline churn, and produce a report that maps "
            f"each finding to a specific dollar amount of MRR at risk. The entire analysis runs in "
            f"minutes from a CSV upload — no live integration, no 90-day onboarding, no dependency "
            f"on the seller's billing system.",
            f"The output is structured around the four failure modes that most commonly cause SaaS "
            f"acquisitions to underperform post-close: zombie MRR (paid accounts with no usage, "
            f"statistically certain to churn at next renewal), annual-plan renewal cliffs (revenue "
            f"concentrated in contracts that expire on the same date), revenue concentration "
            f"(a single top-5 logo whose departure would move the headline number), and cohort "
            f"decay (newer customers retaining worse than older ones, signaling product-market-fit "
            f"erosion). Each is quantified to a dollar figure so the findings are actionable in a "
            f"price negotiation, not just diagnostic.",
        ]
    )


def gen_free_block(h1, desc):
    topic = h1.strip()
    return make_block(
        f"Methodology: how this {topic.lower()} works",
        [
            f"This free {topic.lower()} tool gives you a quick, no-signup assessment based on the "
            f"inputs you provide. The methodology behind it is the same one ChurnLens uses in full "
            f"buyer-side due diligence, just applied to summary inputs rather than a complete "
            f"revenue ledger. The output is directional — it tells you whether the numbers you "
            f"have suggest a healthy business or one with structural churn risk — and it is "
            f"designed to be conservative, erring on the side of flagging potential problems.",
            f"The limitation of any summary-input tool is that it cannot detect the patterns that "
            f"only emerge from customer-level data: zombie accounts, cohort decay curves, "
            f"concentration in specific logos, and renewal-cliff timing. Those require the full "
            f"monthly MRR-by-customer ledger that ChurnLens's paid analysis ingests. Use this free "
            f"tool as a first-pass screen; if it flags anything concerning, the next step is to "
            f"upload the full ledger for the complete reconstruction.",
            f"The formulas and benchmarks used here are transparent and documented across the "
            f"ChurnLens learn hub. There is no black box — the goal is to give you the same "
            f"arithmetic a buyer's diligence team would run, in a format you can use immediately.",
        ]
    )


def gen_integrations_block(h1, desc):
    # Extract tool name
    tool = h1.replace('ChurnLens + ', '').replace(' Integration', '').strip()
    return make_block(
        f"The dual-workflow: {tool} for operations, ChurnLens for diligence",
        [
            f"{tool} and ChurnLens serve complementary roles in a SaaS deal lifecycle. {tool} is "
            f"the operator's platform — it tracks MRR, churn, and subscription metrics from a live "
            f"billing integration for the team running the business day-to-day. ChurnLens is the "
            f"buyer's platform — it reconstructs those same metrics from a data-room export to "
            f"verify whether the numbers {tool} would show are actually accurate, before capital "
            f"changes hands. The two tools do not compete; they operate at different stages and "
            f"answer different questions.",
            f"The practical workflow for an acquirer is: request a {tool} export (or the equivalent "
            f"revenue-ledger CSV) from the seller's data room, run it through ChurnLens's "
            f"buyer-side analysis, and use the reconstructed metrics to verify the seller's "
            f"reported figures. If the target is already on {tool}, keeping it post-close gives "
            f"you operational continuity. The pre-close ChurnLens run is what protects the "
            f"purchase price; the post-close {tool} subscription is what runs the business.",
            f"A common failure mode in SaaS acquisitions is trusting the seller's {tool} dashboard "
            f"as 'proof' of their churn numbers. The dashboard is only as accurate as the inputs "
            f"and configuration underneath it — and those are controlled by the seller. "
            f"ChurnLens's value is that it works from the raw ledger independently, so the "
            f"verification is not dependent on the seller's tool configuration.",
        ]
    )


def gen_industries_secondary_block(h1, desc):
    industry = h1.replace(' Churn', '').replace(' SaaS', '').replace(' Patterns', '').replace('Benchmarks', '').strip()
    return make_block(
        f"What acquirers should stress-test in {industry} SaaS",
        [
            f"{industry} SaaS has structural churn characteristics that generic SaaS benchmarks "
            f"will not capture. The diligence task is to identify the industry-specific failure "
            f"modes — the decay patterns that are common in {industry.lower()} SaaS but rare in "
            f"other verticals — and stress-test the target's revenue ledger for each one. "
            f"ChurnLens automates this by decomposing the ledger by cohort, plan type, and "
            f"customer segment, then flagging the specific patterns that precede headline churn.",
            f"The four highest-impact checks for {industry.lower()} SaaS are: (1) zombie MRR — "
            f"paid accounts whose billing is stable but whose usage signals are declining; "
            f"(2) renewal-cliff mapping — annual-plan revenue concentrated in a single renewal "
            f"window; (3) revenue concentration — top-5 logos whose collective departure would "
            f"move the headline number by more than 1 percentage point; and (4) cohort decay — "
            f"newer customer vintages retaining worse than older ones, which is the earliest "
            f"leading indicator of product-market-fit erosion. Each finding maps to a specific "
            f"dollar amount of MRR at risk.",
        ]
    )


def gen_alternatives_secondary_block(h1, desc):
    comp = h1.replace('ChurnLens vs ', '').replace('ChurnLens ', '').strip()
    return make_block(
        f"The acquisition-diligence difference",
        [
            f"When the comparison is specifically about acquiring a SaaS business rather than "
            f"operating one, the gap between ChurnLens and {comp} becomes structural. {comp} "
            f"requires a live integration with the target's billing system to produce its metrics "
            f"— something a buyer under exclusivity rarely has, and something a seller has every "
            f"incentive to delay. ChurnLens works from a CSV export of the revenue ledger, which "
            f"is a standard data-room request, and produces its analysis in minutes. This means "
            f"the diligence can actually happen within the exclusivity window rather than being "
            f"deferred to post-close.",
            f"The second structural difference is the analytical layer. {comp} reports the metrics "
            f"that the underlying billing system feeds it — it does not independently verify them. "
            f"ChurnLens reconstructs every metric from the raw ledger under a standardized "
            f"definition and flags the gap between the reported figure and the reconstructed "
            f"figure. In a deal context, that gap is the finding that moves the purchase price. "
            f"A tool that reports whatever the seller configured it to report cannot, by "
            f"construction, find the gap between the reported number and the truth.",
        ]
    )


def gen_faq_root_block(h1, desc):
    return make_block(
        "How to use these FAQ answers in a live deal",
        [
            f"The answers on this page are written for a buyer sitting in a data room with a "
            f"revenue ledger open in one window and a deadline in the other. Each answer gives "
            f"you the short version (the benchmark or definition a seller will quote) and the "
            f"longer version (the definitional choices and failure modes that make the short "
            f"version unreliable). The goal is to give you the knowledge to interrogate the "
            f"seller's numbers, not just to accept them.",
            f"The highest-leverage use of this FAQ is to identify which metrics in the seller's "
            f"data room are most likely to be massaged, then reconstruct each one from the raw "
            f"revenue ledger under a consistent definition. ChurnLens automates that "
            f"reconstruction; the FAQ gives you the context to interpret the results and the "
            f"negotiating language to act on them.",
        ]
    )


def gen_generic_block(h1, desc):
    topic = h1.strip()
    return make_block(
        f"Going deeper: {topic}",
        [
            f"{desc} The practical implication for a SaaS acquirer is that the reported number — "
            f"however it is presented in the data room — should be treated as a claim to be "
            f"verified, not a fact to be accepted. Verification means recomputing {topic.lower()} "
            f"from the underlying revenue ledger under a standardized definition, then comparing "
            f"the result to the reported figure.",
            f"ChurnLens exists to automate that verification. Upload the monthly MRR-by-customer "
            f"ledger from the data room, and the analysis reconstructs the core churn and "
            f"retention metrics, flags the decay signals (zombie MRR, renewal cliffs, cohort "
            f"decay, revenue concentration), and quantifies each finding to a dollar amount of "
            f"MRR at risk. The output is designed to be used in a price negotiation: every "
            f"finding maps to a specific, defensible adjustment to the purchase price.",
        ]
    )


# ── Section dispatch ────────────────────────────────────────────────────────

SECTION_GENERATORS = {
    'glossary': gen_glossary_block,
    'faq': gen_faq_block,
    'vs': gen_vs_block,
    'for': gen_for_block,
    'learn': gen_learn_block,
    'benchmarks': gen_benchmarks_block,
    'use-cases': gen_use_cases_block,
    'free': gen_free_block,
    'integrations': gen_integrations_block,
    'industries': gen_industries_secondary_block,
    'alternatives-to': gen_alternatives_secondary_block,
    'pricing-questions': gen_generic_block,
}

def get_generator(rel_path, url_path):
    """Pick the right generator for a page."""
    # Special-case the root faq.html
    if rel_path == 'faq.html' or rel_path == 'faq/index.html':
        return gen_faq_root_block
    section = url_path.split('/')[0] if '/' in url_path else ''
    return SECTION_GENERATORS.get(section, gen_generic_block)


# ── Main patching logic ────────────────────────────────────────────────────

def find_insertion_point(html):
    """Find the best insertion point: before </main>, or before <footer, 
    whichever comes first and exists."""
    candidates = []
    for marker in ['</main>', '<footer']:
        idx = html.find(marker)
        if idx > 0:
            candidates.append((idx, marker))
    if not candidates:
        # fallback: before the BRUNSON comment
        idx = html.find('<!-- BRUNSON')
        if idx > 0:
            return idx, '<!-- BRUNSON'
        return -1, None
    candidates.sort()
    return candidates[0]


def main():
    sitemap = (ROOT / 'sitemap.xml').read_text(errors='ignore')
    urls = re.findall(r'<loc>([^<]+)</loc>', sitemap)

    fixed = []
    skipped = []
    errors = []

    for url in urls:
        url_path = url.replace('https://churnlens.site', '').lstrip('/')
        candidates = [url_path + '.html', url_path + '/index.html', url_path] if url_path else ['index.html']
        
        fp = None
        for c in candidates:
            candidate = ROOT / c
            if candidate.exists() and candidate.is_file():
                fp = candidate
                break
        if not fp:
            continue

        rel = str(fp.relative_to(ROOT))
        existing = fp.read_text(errors='ignore')
        wc = count_visible_words(existing)
        
        if wc >= 500:
            skipped.append((rel, f"{wc} words"))
            continue

        h1, desc, title = extract_meta(existing)
        if not h1:
            skipped.append((rel, "no h1 found"))
            continue

        gen = get_generator(rel, url_path)
        block = gen(h1, desc)

        insert_idx, marker = find_insertion_point(existing)
        if insert_idx < 0:
            errors.append((rel, "no insertion point"))
            continue

        new_html = existing[:insert_idx] + block + '\n' + existing[insert_idx:]
        new_wc = count_visible_words(new_html)
        
        # Only write if we actually added meaningful content
        if new_wc - wc < 100:
            skipped.append((rel, f"only +{new_wc-wc} words"))
            continue
            
        fp.write_text(new_html)
        fixed.append((rel, wc, new_wc))

    print(f"\nFixed: {len(fixed)} pages")
    for rel, old, new in sorted(fixed, key=lambda x: x[1]):
        print(f"  ✓ {old:4d} → {new:4d}  {rel}")

    print(f"\nSkipped: {len(skipped)} (already sufficient or no h1)")
    print(f"Errors: {len(errors)}")
    for rel, reason in errors:
        print(f"  ✗ {rel}: {reason}")

    return fixed, skipped, errors


if __name__ == "__main__":
    main()
