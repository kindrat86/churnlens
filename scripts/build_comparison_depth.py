#!/usr/bin/env python3
"""Deepen the /alternatives-to/* and /vs/* comparison pages and protect them
from the pSEO generators that keep flattening them.

WHY THIS EXISTS
---------------
~/.growth-engine/isenberg-pseo-round15.py rebuilds churnlens /alternatives-to/*
and /vs/* on every run. Its skip-guard reads

    <repo>/alternatives-to/<slug>/index.html   (the DIRECTORY twin)

and only skips when that file exists AND contains "<!-- isenberg-round15 -->".
Its write_page() is otherwise UNCONDITIONAL and writes BOTH the dir twin and the
flat .html. Because the dir twins never existed, every round15 run overwrote the
hand-built pages -- which is how these dropped from ~1,140 words to ~150.

So protection requires two things, both handled here:
  1. the marker string present in the dir-twin index.html, and
  2. the dir twin actually existing.

round16 / round18 / round19 use the opposite polarity -- their write_page skips
any existing page that does NOT contain their own marker -- so we deliberately
do NOT add those markers.

DESIGN RULES (from repo CLAUDE.md + prior incidents)
---------------------------------------------------
* INJECT into the existing HTML; never bare-regen. The base template is "bare" and
  a regen strips PostHog, hreflang, ux.css and the entity @graph.
* Brand is ONE word: "ChurnLens".
* No fabricated competitor capabilities and no invented numbers. Competitor facts
  here are category-level and checkable; the single worked example is explicitly
  labelled illustrative.
* Canonical stays on the NON-slash URL in BOTH twins, so the newly-created
  /path/ variant consolidates onto /path instead of splitting it.
* Visible FAQ and FAQPage JSON-LD are generated from one source, so they cannot drift.

Idempotent: safe to re-run.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKER = "<!-- isenberg-round15 -->"
GUARD_NOTE = "<!-- hand-built: deep comparison page. Do not bare-regen. See scripts/build_comparison_depth.py -->"

BASE = "https://churnlens.site"

# --------------------------------------------------------------------------
# Competitor facts. Category-level and checkable; nothing invented.
# `csv_import` changes how the buyer-side gap is framed, honestly.
# --------------------------------------------------------------------------
TOOLS = {
    "baremetrics": {
        "name": "Baremetrics",
        "category": "operator-side subscription analytics",
        "who": (
            "Baremetrics launched in 2013 as a Stripe-first subscription-analytics dashboard. "
            "It is aimed squarely at founders and operators who want to watch their own revenue move in real time."
        ),
        "does_well": [
            "Live MRR, ARR, LTV and churn dashboards driven by a connected billing account (Stripe, Recurly, Chargebee, Braintree, the app stores).",
            "Recover, its dunning product, which chases failed and expired-card payments automatically.",
            "Cancellation Insights and Trial Insights, both designed for an operator trying to reduce their own churn.",
            "Forecasting and public benchmarks for a business you actively run.",
        ],
        "csv_import": False,
        "data_source": "A live billing integration — you connect your own Stripe or billing account.",
        "pricing_shape": "Paid plans that scale with the revenue you track; a trial rather than a permanent free tier.",
        "buyer_gap": (
            "Baremetrics assumes you own the account it is watching. In an acquisition you almost never get the "
            "seller's Stripe keys — you get a CSV export. And because Baremetrics reports churn according to the "
            "connected account's own configuration, it inherits the seller's definition of churn rather than "
            "stress-testing it. In diligence, the seller's definition is precisely the thing under examination."
        ),
        "overlap": (
            "Both tools compute churn and both will show you an MRR trend line. The divergence is whose account is "
            "being measured and who chose the definitions. Baremetrics answers \"how is my subscription business "
            "doing?\" continuously. ChurnLens answers \"is this other company's reported churn believable?\" once, "
            "at a point in time, from data the seller handed over."
        ),
        "example": (
            "Suppose a target reports 2.3% monthly churn. Connect Baremetrics to that account and — if the account "
            "excludes downgrades from its churn definition, and annual plans that cancelled mid-term are recorded "
            "at renewal date rather than cancellation date — you will see roughly 2.3% too, because you have "
            "inherited the same configuration. Recomputing from the raw subscription rows is what surfaces the gap."
        ),
        "verdict_keep": "you are running a SaaS and want continuous metrics plus dunning",
        "verdict_switch": "you are evaluating someone else's SaaS from an export and need the reported number challenged",
    },
    "chartmogul": {
        "name": "ChartMogul",
        "category": "operator-side subscription analytics with flexible data import",
        "who": (
            "ChartMogul launched in 2014 as a subscription-analytics platform, and is best known for its depth in "
            "cohort retention analysis and subscriber-level segmentation."
        ),
        "does_well": [
            "Cohort retention analysis and MRR-movement breakdowns (new, expansion, contraction, churn) that are genuinely best-in-class.",
            "Flexible data ingestion: Stripe, Recurly, Chargebee, Braintree, Paddle and the app stores, or direct CSV and API import.",
            "Rich segmentation and subscriber-level drill-down for teams running ongoing revenue analytics.",
            "An entry tier that is free below an MRR threshold, then scales with tracked MRR.",
        ],
        "csv_import": True,
        "data_source": "Billing integrations or direct CSV/API import — so a buyer genuinely can load a target's data.",
        "pricing_shape": "Free below an entry MRR threshold, then priced on tracked MRR.",
        "buyer_gap": (
            "ChartMogul is the closest of the analytics platforms to being usable in diligence, because it will ingest "
            "a CSV. The gap is not data access — it is opinion. ChartMogul is a neutral platform: you map the columns, "
            "choose the definitions, build the segments and draw the conclusions. It will faithfully show you whatever "
            "you configured. It will not tell you that a 34% top-five concentration is a financing problem, and it does "
            "not emit a buyer-side grade you can put in a committee paper."
        ),
        "overlap": (
            "This is the most genuine overlap of any tool on this list. If you are experienced, patient, and know "
            "exactly which cuts of the data expose an inflated retention story, ChartMogul can get you most of the way "
            "there. The difference is how much of the reasoning you supply yourself: ChartMogul is a very good "
            "instrument, and ChurnLens is an opinionated checklist that happens to run on the same raw data."
        ),
        "example": (
            "Load a target's export into ChartMogul and you will get an accurate cohort chart. Whether you notice that "
            "the cohorts thin out sharply at month 13 — the signature of annual plans not renewing — depends entirely "
            "on whether you thought to look at month 13. An acquisition-shaped tool asks that question by default; "
            "a general analytics platform waits for you to ask it."
        ),
        "verdict_keep": "you want the deepest cohort analysis available and are happy to supply the diligence judgement yourself",
        "verdict_switch": "you want the acquisition-specific questions asked for you, and a defensible grade at the end",
    },
    "profitwell": {
        "name": "ProfitWell",
        "category": "free operator-side subscription metrics",
        "who": (
            "ProfitWell — now ProfitWell Metrics, part of Paddle — became widely used because its core subscription "
            "metrics are free and carefully normalised. It is monetised through its retention and pricing products "
            "rather than the dashboard."
        ),
        "does_well": [
            "Free MRR, ARR, churn and LTV dashboards from a connected billing account — genuinely strong value for an operator.",
            "Retain, its dunning and retention-automation product for winning back your own churning customers.",
            "Price Intelligently, its pricing research and strategy practice.",
            "Careful metric normalisation, which is why its numbers are widely trusted as a reference.",
        ],
        "csv_import": False,
        "data_source": "A live billing integration — you connect your own Stripe or billing account.",
        "pricing_shape": "Core metrics are free; revenue comes from Retain and the pricing services.",
        "buyer_gap": (
            "Because ProfitWell is free, it is often the first thing a first-time buyer reaches for. But free and "
            "operator-side are different axes. ProfitWell connects to a billing account you control and monitors it "
            "going forward. It is not built to interrogate a third party's business from a static export, and it will "
            "not produce a concentration analysis, a red-flag list, or a revenue-quality grade for a target."
        ),
        "overlap": (
            "The overlap is narrower than the price tag suggests. Both will tell you a churn percentage. Only one of "
            "them was designed on the assumption that the number it is given might be wrong — which is the working "
            "assumption of every buyer-side diligence process."
        ),
        "example": (
            "A searcher evaluating a $1.2M ARR target signs up for ProfitWell because it costs nothing, then discovers "
            "the seller will not hand over billing credentials — only a CSV. At that point the free dashboard has "
            "nothing to connect to, and the diligence work reverts to a spreadsheet."
        ),
        "verdict_keep": "you run a SaaS and want accurate metrics at no cost, plus dunning",
        "verdict_switch": "you have a CSV rather than credentials, and the number you were given is the thing you need to test",
    },
    "churnzero": {
        "name": "ChurnZero",
        "category": "customer-success platform for retention teams",
        "who": (
            "ChurnZero is a customer-success platform built for CS teams whose job is to keep existing customers. "
            "Its centre of gravity is the account manager's daily workflow, not the finance or diligence workflow."
        ),
        "does_well": [
            "Customer health scoring that blends product usage, support activity and engagement signals.",
            "Automated playbooks and in-app messaging that trigger when an account starts to look at risk.",
            "Renewal and expansion pipeline management for CS and account teams.",
            "Survey and NPS instrumentation feeding back into account health.",
        ],
        "csv_import": False,
        "data_source": "Live integrations with your CRM, product telemetry and support tooling.",
        "pricing_shape": "Subscription pricing aimed at teams, typically with an implementation period.",
        "buyer_gap": (
            "ChurnZero is the furthest of any tool here from acquisition diligence, and the distance is structural "
            "rather than a missing feature. It is forward-looking and intervention-oriented: it exists to change the "
            "future by flagging accounts a human should call. Diligence is backward-looking and forensic: it asks what "
            "already happened, and whether the record of it is honest. ChurnZero also needs deep live integrations "
            "into systems a target company will not connect for a prospective buyer."
        ),
        "overlap": (
            "Almost none, despite the shared vocabulary. Both tools use the word churn and both talk about risk, but "
            "ChurnZero's risk is \"this customer may leave next quarter, intervene now\" while a buyer's risk is "
            "\"this revenue may not be what the seller says it is, price accordingly.\" Confusing the two is a common "
            "and expensive category error in first acquisitions."
        ),
        "example": (
            "A post-acquisition team may well deploy ChurnZero on day 31 to defend the revenue they just bought. That "
            "is a sound plan and a different project from deciding, on day minus 30, whether the revenue was real."
        ),
        "verdict_keep": "you have a CS team whose job is defending revenue you already own",
        "verdict_switch": "you are deciding whether to buy the revenue in the first place",
    },
    "saasoptics": {
        "name": "SaaSOptics",
        "category": "subscription management and financial operations",
        "who": (
            "SaaSOptics is a B2B subscription-management and financial-operations platform — revenue recognition, "
            "invoicing, and audit-ready SaaS reporting. It now sits within Maxio, formed in 2022 from SaaSOptics "
            "and Chargify."
        ),
        "does_well": [
            "Revenue recognition and deferred-revenue schedules that stand up to an audit.",
            "Invoicing, billing operations and collections for B2B subscription contracts.",
            "GAAP-oriented SaaS reporting and investor-grade metric packs.",
            "Contract-level revenue modelling for businesses with non-trivial deal structures.",
        ],
        "csv_import": True,
        "data_source": "Your own billing, contract and accounting systems, implemented as a system of record.",
        "pricing_shape": "Platform pricing with an implementation project; positioned as finance infrastructure.",
        "buyer_gap": (
            "SaaSOptics is the most financially rigorous tool on this list, and it is rigorous about the company that "
            "implemented it. It is a system of record you install and operate, over months, for your own entity. "
            "No seller is going to stand up a Maxio implementation so a prospective buyer can inspect them. Its "
            "outputs are also accounting-shaped — correct revenue recognition — rather than diligence-shaped, which "
            "asks a different question: is this revenue durable, concentrated, or quietly decaying?"
        ),
        "overlap": (
            "Genuine but sequential rather than simultaneous. SaaSOptics is often exactly the right answer for the "
            "acquired company after close, particularly if the target has been running on spreadsheets. It is the "
            "wrong shape for the four weeks before an LOI, when all you have is an export and a deadline."
        ),
        "example": (
            "If a target already runs SaaSOptics, ask for its reports — they are good evidence and worth having. You "
            "should still recompute churn from the raw subscription rows, because a correct revenue-recognition "
            "schedule and a durable revenue base are not the same claim."
        ),
        "verdict_keep": "you need audit-ready revenue recognition for a business you own or are integrating",
        "verdict_switch": "you are pre-close, working from an export, and need durability rather than recognition",
    },
    "capterra": {
        "name": "Capterra",
        "category": "software review and comparison directory",
        "who": (
            "Capterra is a software review directory: buyers browse categories, read user reviews, and shortlist "
            "vendors. It is a discovery surface, not an analysis tool, and it reviews software rather than analysing "
            "any particular company's revenue."
        ),
        "does_well": [
            "Aggregating user reviews across a very large number of software categories.",
            "Helping a buyer discover which tools exist in a category they are unfamiliar with.",
            "Side-by-side feature and pricing comparison of vendors within a category.",
            "Surfacing qualitative signal about what using a product is actually like day to day.",
        ],
        "csv_import": False,
        "data_source": "User-submitted reviews and vendor-supplied profile data.",
        "pricing_shape": "Free for buyers; monetised through vendor listings and lead generation.",
        "buyer_gap": (
            "Comparing Capterra to ChurnLens is really comparing two different stages of a decision. Capterra can "
            "help you decide which diligence tool to use. It cannot analyse a target company, because it holds "
            "reviews of products, not any company's subscription data. If you are on this page because you found "
            "ChurnLens in a directory, Capterra has already done its job."
        ),
        "overlap": (
            "None in function. The reason the comparison gets made at all is that both appear when someone searches "
            "for how to evaluate a SaaS purchase — but one is evaluating which software to buy for yourself, and the "
            "other is evaluating a company you intend to acquire."
        ),
        "example": (
            "Use a directory to build a shortlist of diligence tools. Use a diligence tool to decide whether a target's "
            "reported 2.3% churn survives contact with its own raw data. Neither substitutes for the other."
        ),
        "verdict_keep": "you are still choosing which tools to shortlist",
        "verdict_switch": "you have a specific target company and an export to interrogate",
    },
}

# Which pages to build: (directory, slug, kind)
#
# CONSOLIDATION NOTE: /vs/<tool> and /alternatives-to/<tool> for the SAME tool
# were 0.86-0.87 Jaccard-identical -- two URLs competing for one intent. GSC shows
# the /alternatives-to/* URLs are the ones earning impressions ("baremetrics
# alternative", "profitwell alternatives") while the /vs/* twins earn zero. So the
# four overlapping tools live at /alternatives-to/ only, and /vs/<tool> 301s there
# (see vercel.json). /vs/ keeps only the two tools with no alternatives-to twin.
PAGES = [
    ("alternatives-to", "baremetrics", "alt"),
    ("alternatives-to", "chartmogul", "alt"),
    ("alternatives-to", "profitwell", "alt"),
    ("alternatives-to", "churnzero", "alt"),
    ("vs", "saasoptics", "vs"),
    ("vs", "capterra", "vs"),
]

# /vs/<slug> -> /alternatives-to/<slug>; redirects live in vercel.json
CONSOLIDATED = ["baremetrics", "chartmogul", "profitwell", "churnzero"]

CL_DOES = [
    "Recomputes churn from the target's raw subscription rows instead of trusting the reported figure.",
    "Scores revenue concentration, so a top-five customer share that would worry a lender shows up before the LOI.",
    "Isolates annual-plan decay — cancellations dated at renewal rather than at the moment the customer left.",
    "Flags zombie MRR: accounts still being billed that stopped using the product.",
    "Returns a benchmarked A–F revenue-quality grade and a ranked red-flag list you can attach to a committee paper.",
]

# Per-tool unique blocks. These exist to make each page genuinely different rather
# than one template with the tool name swapped -- the failure mode that made the
# previous generation of these pages worthless. Each tool gets its own framing,
# its own objection section, and its own closing caveat.
ANGLES = {
    "baremetrics": {
        "frame": (
            "The reason Baremetrics comes up in acquisition conversations at all is that it is the tool most "
            "founders already have installed. So when a buyer asks \"what are you using to track churn?\", the "
            "answer is often Baremetrics — and the buyer reasonably concludes that if they get access to the same "
            "dashboard, they will see the same truth. That inference is the trap. A dashboard connected to the "
            "seller's account is not an independent measurement; it is the seller's measurement, rendered more "
            "attractively. The instrument is fine. The problem is that in diligence you need a second instrument, "
            "calibrated differently, pointed at the raw data."
        ),
        "objection": (
            "<h2>\"But Baremetrics has churn analytics — isn't that the same thing?\"</h2>"
            "<p>It has excellent churn analytics, and that is genuinely not the same thing. Churn analytics answers "
            "\"what is my churn?\" Diligence answers \"is the churn figure I was given defensible?\" Those questions "
            "diverge the moment definitions are involved — and definitions are always involved. Whether a downgrade "
            "counts as churn, whether a mid-term annual cancellation is dated at cancellation or at renewal, whether "
            "paused accounts sit in the denominator: each is a defensible configuration choice, and each moves the "
            "headline number. A tool reading the seller's configuration reproduces the seller's answer. That is "
            "correct behaviour for an operator and useless behaviour for a buyer.</p>"
        ),
        "closing_caveat": (
            "If what you actually need is a live dashboard and automated dunning for a business you own, Baremetrics "
            "is a better purchase than ChurnLens and we would rather you knew that now."
        ),
        "faq_extra": (
            "Can I just ask the seller for Baremetrics access?",
            "You can, and it is worth having as one input. Just treat it as the seller's presentation of their "
            "numbers rather than as verification of them — it reports according to that account's configuration. "
            "Ask for the raw subscription export as well, because that is the only artefact you can independently "
            "recompute from.",
        ),
    },
    "chartmogul": {
        "frame": (
            "ChartMogul deserves a more careful comparison than the other tools here, because it is the one that "
            "could plausibly do the job. It imports CSVs, so the data-access objection that rules out most operator "
            "tools does not apply. Its cohort analysis is genuinely excellent and is exactly the right lens for "
            "spotting retention problems. If you are an experienced analyst who already knows which cuts of "
            "subscription data betray an inflated retention story, ChartMogul plus your own judgement is a "
            "legitimate diligence stack. The honest question is not capability but who supplies the reasoning."
        ),
        "objection": (
            "<h2>\"ChartMogul imports CSVs — so why would I need anything else?\"</h2>"
            "<p>This is the strongest objection on any of these pages and it deserves a straight answer: for some "
            "buyers, you do not. If you have done twenty deals and carry the red-flag checklist in your head, a "
            "neutral analytics platform is arguably better than an opinionated one, because it will not impose "
            "someone else's thresholds on your judgement.</p>"
            "<p>The case for an opinionated tool is about defaults and recall under time pressure. A general platform "
            "shows you what you configured it to show; it does not volunteer that month 13 is where this particular "
            "cohort falls apart, or that top-five concentration crossed the level at which lenders start asking "
            "questions. On a four-week timeline, across several targets, the questions you forget to ask are the "
            "expensive ones. An acquisition-shaped tool asks a fixed list every time, which is a weaker instrument "
            "than an expert but a more reliable one than a tired expert.</p>"
        ),
        "closing_caveat": (
            "If you want maximum analytical flexibility and are confident supplying the diligence judgement yourself, "
            "ChartMogul is the more powerful instrument and you should use it."
        ),
        "faq_extra": (
            "Is ChurnLens just ChartMogul with opinions bolted on?",
            "Not quite, though the framing is fair. Both read subscription data, but ChartMogul is built as a "
            "configurable platform for ongoing analytics, while ChurnLens is built as a fixed diligence pass: the "
            "same acquisition-risk questions asked of every target, ending in a comparable grade. Flexibility versus "
            "repeatability is the real trade, and which one you want depends on how many deals you look at.",
        ),
    },
    "profitwell": {
        "frame": (
            "ProfitWell shows up in diligence conversations for one reason above all others: it is free. For a "
            "first-time buyer working without a deal budget, that matters, and it would be dishonest to pretend "
            "price is irrelevant. But free and fit-for-purpose are separate questions, and the one that decides "
            "this comparison is not cost. It is whether the tool can run at all on what a seller will actually "
            "give you — which, in the overwhelming majority of small SaaS transactions, is a spreadsheet export "
            "and not a set of billing credentials."
        ),
        "objection": (
            "<h2>\"ProfitWell is free — why pay for anything?\"</h2>"
            "<p>Because in this specific situation free is not the binding constraint; access is. ProfitWell's "
            "metrics are free and carefully normalised, which is exactly why so many operators trust them. But it "
            "is built around a billing account you connect and control. A seller who is three weeks from signing "
            "is not going to hand a prospective buyer live access to their Stripe account, and most would be "
            "unwise to. So the free dashboard has nothing to attach to.</p>"
            "<p>The comparison that matters is not $0 against a paid tool. It is $0-that-cannot-run against the "
            "cost of a mispriced deal. A single undetected concentration problem or a cohort of annual plans "
            "quietly not renewing changes a valuation by multiples of any software fee.</p>"
        ),
        "closing_caveat": (
            "If you run a SaaS and want trustworthy metrics for nothing, ProfitWell is an excellent choice and this "
            "page is not trying to talk you out of it."
        ),
        "faq_extra": (
            "Does ChurnLens have a free option too?",
            "Yes — there is a free tier, and single one-off analyses start at $9, which exists precisely because "
            "many buyers are evaluating one target rather than running a portfolio. Cost is rarely the reason to "
            "choose between these two; data access is.",
        ),
    },
    "churnzero": {
        "frame": (
            "ChurnZero and ChurnLens get compared almost entirely because of the word they share. That is worth "
            "stating plainly, because the shared vocabulary hides a genuine category difference that catches out "
            "first-time acquirers. ChurnZero is customer-success software: its user is an account manager, its unit "
            "of work is an at-risk customer, and its purpose is to change what happens next. Diligence software has "
            "a different user, a different unit of work, and the opposite relationship to time — it is forensic "
            "about what already happened, and it cannot intervene in any of it."
        ),
        "objection": (
            "<h2>\"Both tools are about churn — surely they overlap?\"</h2>"
            "<p>They overlap in vocabulary and almost nowhere else, and the distinction is worth getting right "
            "because acting on the wrong one is expensive.</p>"
            "<p>ChurnZero's churn is predictive and account-level: this customer's usage is falling, someone should "
            "call them this week. It is only useful if you can act — which means you must already own the "
            "relationship, and the tool must be wired into your CRM, product telemetry and support desk. A target "
            "company will not connect those systems for a prospective buyer, and even if they did, the output would "
            "answer a question no buyer is asking.</p>"
            "<p>A buyer's churn is historical and aggregate: over the last twenty-four months, did revenue behave "
            "the way the seller says it did? You cannot intervene in that. You can only price it.</p>"
        ),
        "closing_caveat": (
            "If you already own the revenue and want to defend it, ChurnZero is addressing your problem and ChurnLens "
            "is not. The two belong at opposite ends of the same deal."
        ),
        "faq_extra": (
            "Should I buy ChurnZero for the company after I acquire it?",
            "Quite possibly, and that is a coherent plan — defend the revenue you just bought. It is simply a "
            "separate decision from whether the revenue was worth buying, which is the question that has to be "
            "answered first and cannot be answered with a customer-success platform.",
        ),
    },
    "saasoptics": {
        "frame": (
            "SaaSOptics is the most financially serious tool on this list, which makes the comparison more "
            "interesting than most. It is not a dashboard — it is finance infrastructure, concerned with revenue "
            "recognition, deferred revenue and reporting that will survive an audit. Buyers reasonably assume that "
            "if a target runs it, the revenue must be well understood. Often that is true. It still does not answer "
            "the buyer's question, because correctly recognised revenue and durable revenue are two different claims "
            "about the same numbers."
        ),
        "objection": (
            "<h2>\"If the target's revenue is audit-clean, what is left to check?\"</h2>"
            "<p>Durability. Revenue recognition asks whether revenue was recorded in the right period under the "
            "right policy. It is a question about accounting correctness, and SaaSOptics answers it well.</p>"
            "<p>Diligence asks a different question: will this revenue still be here in eighteen months, and how "
            "concentrated is it? A revenue base can be recognised impeccably and still be 40% dependent on two "
            "customers, or composed largely of annual plans in their final term, or padded with accounts that pay "
            "but no longer log in. None of those are accounting errors. All of them change what the business is "
            "worth. An audit-clean set of books and a fragile revenue base coexist comfortably.</p>"
        ),
        "closing_caveat": (
            "If you need audit-ready revenue recognition — before or after a deal — SaaSOptics and Maxio are the "
            "right category and ChurnLens is not competing for that work."
        ),
        "faq_extra": (
            "The target already runs SaaSOptics. Do I still need to recompute churn?",
            "Yes, and their reports are useful evidence worth requesting. But a correct revenue-recognition schedule "
            "tells you the revenue was booked properly, not that it is concentrated, decaying or partly dormant. "
            "Those are the findings that move a price, and they come from the raw subscription rows.",
        ),
    },
    "capterra": {
        "frame": (
            "This comparison is really a question about which stage of a decision you are in, and it is worth "
            "answering directly rather than pretending the two tools compete. Capterra is a discovery surface: it "
            "holds user reviews of software products and helps you work out which tools exist in a category. "
            "ChurnLens is one of the products such a directory might list. If you arrived here from a directory "
            "while shortlisting diligence tools, the directory has already done its job, and the remaining question "
            "is what the tool itself does."
        ),
        "objection": (
            "<h2>\"Can't I just read reviews to evaluate a SaaS I'm buying?\"</h2>"
            "<p>This is the confusion worth clearing up, because the two senses of \"evaluate a SaaS\" are quite "
            "different. Reading reviews of a product tells you what customers think of it — genuinely useful "
            "qualitative signal, and relevant to a target's churn risk in a soft way.</p>"
            "<p>It tells you nothing about that company's revenue. Reviews cannot show you customer concentration, "
            "how annual cohorts renew, or whether a fifth of billed accounts have stopped logging in. Those live in "
            "the subscription data and nowhere else. A directory reviews products; diligence interrogates a "
            "company's numbers. Use reviews as one qualitative input and never as a substitute for the data.</p>"
        ),
        "closing_caveat": (
            "If you are still deciding which tools to shortlist, a review directory is the right place to be and "
            "this page is premature — come back once you have a target and an export."
        ),
        "faq_extra": (
            "Is ChurnLens listed on Capterra or G2?",
            "Directory listings are in progress rather than complete, so the most reliable way to evaluate ChurnLens "
            "today is the free tier: run it on a real export and judge the output directly, rather than relying on "
            "review volume that a newer product will not yet have.",
        ),
    },
}

CL_DOES_NOT = [
    "It does not connect to a live billing account, so it cannot be your ongoing metrics dashboard.",
    "It does not run dunning, win-back campaigns or any retention automation.",
    "It does not do revenue recognition, invoicing or anything an auditor would call accounting.",
    "It does not predict which individual customer will churn next month.",
]


def dimension_table(t: dict) -> str:
    return f"""<h2>Side by side, on the dimensions that decide it</h2>
<table>
<thead><tr><th>Dimension</th><th>{t['name']}</th><th>ChurnLens</th></tr></thead>
<tbody>
<tr><td>Primary user</td><td>Founders and operators running their own SaaS</td><td>Acquirers, PE and M&amp;A analysts, and searchers buying one</td></tr>
<tr><td>Core job</td><td>{t['category'].capitalize()}</td><td>One-off buyer-side acquisition risk report</td></tr>
<tr><td>Data it needs</td><td>{t['data_source']}</td><td>The target's raw subscription CSV export — no seller credentials</td></tr>
<tr><td>Whose definitions apply</td><td>The connected account's own configuration</td><td>Recomputed from raw rows, specifically to test the reported figure</td></tr>
<tr><td>Output</td><td>Dashboards, reports and trend charts</td><td>Benchmarked A&ndash;F revenue-quality grade plus a ranked red-flag report</td></tr>
<tr><td>Time to first answer</td><td>Continuous, once setup and integration are done</td><td>Minutes, from a single CSV upload</td></tr>
<tr><td>Commercial shape</td><td>{t['pricing_shape']}</td><td>Free tier; one-off analysis from $9; paid tiers to $1,999</td></tr>
<tr><td>Best for</td><td>Running a SaaS</td><td>Buying one</td></tr>
</tbody>
</table>"""


def faq_pairs(t: dict, kind: str) -> list[tuple[str, str]]:
    name = t["name"]
    if t["csv_import"]:
        can_use = (
            f"Partly, and more than most. {name} can ingest a target's CSV, so data access is not the blocker. "
            f"What it will not do is decide which cuts of that data matter for an acquisition, or hand you a "
            f"buyer-side grade — you supply the diligence judgement yourself."
        )
    else:
        can_use = (
            f"Only if the seller gives you live billing credentials, which is rare. {name} is built around a "
            f"connected account you control, and it reports using that account's own churn configuration — the very "
            f"thing a buyer needs to test rather than inherit."
        )
    return [
        (
            f"Is ChurnLens a {name} alternative?" if kind == "alt" else f"ChurnLens or {name} — which do I need?",
            f"They do different jobs, so it depends on which side of a transaction you are on. {name} is "
            f"{t['category']}; ChurnLens is buyer-side due diligence. Keep {name} if {t['verdict_keep']}. Use "
            f"ChurnLens if {t['verdict_switch']}.",
        ),
        (f"Can I use {name} for SaaS acquisition due diligence?", can_use),
        (
            "Does ChurnLens connect to Stripe?",
            "No, and that is deliberate. ChurnLens works from the raw subscription CSV a seller exports, so you can "
            "run diligence on a target without ever holding their live billing credentials — which is the situation "
            "buyers are actually in.",
        ),
        (
            "What does ChurnLens produce that a metrics dashboard does not?",
            "A benchmarked A–F revenue-quality grade and a ranked red-flag report tuned to acquisition risk: hidden "
            "churn, customer-concentration risk, annual-plan decay and zombie MRR — all recomputed from the raw rows "
            "rather than reported according to the seller's own configuration.",
        ),
    ]


def build_body(t: dict, kind: str, dirname: str, slug: str) -> tuple[str, str, str]:
    name = t["name"]
    if kind == "alt":
        h1 = f"{name} alternatives for SaaS acquisition due diligence"
        title = f"{name} Alternative for SaaS Due Diligence | ChurnLens"
        desc = (
            f"Looking for a {name} alternative for acquisition due diligence? {name} is {t['category']}; "
            f"ChurnLens recomputes a target's churn from raw CSVs and grades revenue quality."
        )
        tldr = (
            f"<strong>Short answer:</strong> {name} is {t['category']}, and it is good at that. It is not a "
            f"diligence tool. If you are testing whether a target's reported churn survives its own raw data, "
            f"that is a different job — and the one ChurnLens was built for."
        )
    else:
        h1 = f"ChurnLens vs {name}: buyer-side diligence or {t['category'].split(' for ')[0]}?"
        title = f"ChurnLens vs {name}: Which One Do You Need?"
        desc = (
            f"ChurnLens vs {name}, compared honestly. {name} is {t['category']}; ChurnLens is buyer-side SaaS "
            f"due diligence that recomputes churn from a target's raw CSV export."
        )
        tldr = (
            f"<strong>Short answer:</strong> these are not competitors. {name} is {t['category']}. ChurnLens is "
            f"buyer-side due diligence for a company you do not own yet. Most people arriving at this comparison "
            f"need one clearly more than the other."
        )

    does_well = "\n".join(f"<li>{x}</li>" for x in t["does_well"])
    cl_does = "\n".join(f"<li>{x}</li>" for x in CL_DOES)
    cl_not = "\n".join(f"<li>{x}</li>" for x in CL_DOES_NOT)

    pairs = faq_pairs(t, kind)
    faq_visible = "\n".join(
        f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in pairs
    )

    seen, related = set(), []
    for d, s, k in PAGES:
        if s == slug or d != dirname:
            continue
        if s in seen:
            continue
        seen.add(s)
        related.append((f"/{d}/{s}", TOOLS[s]["name"]))
    related_html = "\n".join(
        f'<li><a href="{BASE}{u}">ChurnLens vs {n}</a></li>' for u, n in related[:5]
    )

    body = f"""<h1>{h1}</h1>
<div class="tldr"><p>{tldr}</p></div>

<h2>The distinction that actually matters</h2>
<p>Nearly every tool in this category is <em>operator-side</em>: you connect your own billing account and watch
your own revenue. ChurnLens is <em>buyer-side</em>: you upload an export from a company you are considering
buying, and it tells you whether the story that export tells is the same story the seller told you. That single
difference — whose business is being measured, and who chose the definitions — decides which tool you want far
more than any feature list.</p>

<h2>What {name} is built for</h2>
<p>{t['who']}</p>
<ul>
{does_well}
</ul>
<p><strong>How it gets data:</strong> {t['data_source']} <strong>Commercially:</strong> {t['pricing_shape']}</p>

<h2>Where it stops being the right tool for a buyer</h2>
<p>{t['buyer_gap']}</p>

<h2>What ChurnLens is built for</h2>
<ul class="check">
{cl_does}
</ul>

{dimension_table(t)}

<h2>Where the two genuinely overlap</h2>
<p>{t['overlap']}</p>

<h2>A worked illustration</h2>
<div class="callout"><p>{t['example']}</p>
<p style="margin-bottom:0"><em>Illustrative scenario, not a measured result from a named company.</em></p></div>

<h2>Choosing between them</h2>
<p><strong>Stay with {name}</strong> if {t['verdict_keep']}. <strong>Use ChurnLens</strong> if {t['verdict_switch']}.
Plenty of people end up using both, at different moments: one before a deal closes, the other after.</p>

<h2>What ChurnLens deliberately does not do</h2>
<p>A comparison page that only lists strengths is not much use in diligence, so here is the other side.</p>
<ul class="cross">
{cl_not}
</ul>
<p>If any of those four are what you came for, {name} or a tool like it is the better purchase, and we would
rather say so here than after you have signed up.</p>

<div class="cta">
<h2>Test a target's numbers before you commit</h2>
<p>Upload the subscription CSV a seller gave you and get a revenue-quality grade plus a ranked red-flag report.</p>
<a href="{BASE}/">Try ChurnLens free →</a>
</div>

<h2>Frequently asked questions</h2>
{faq_visible}

<h2>Related comparisons</h2>
<ul>
{related_html}
<li><a href="{BASE}/5-risk-buyer-side-method">The 5-risk buyer-side method</a></li>
<li><a href="{BASE}/benchmarks">SaaS benchmarks for due diligence</a></li>
</ul>
"""
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)},
            }
            for q, a in pairs
        ],
    }
    return body, title, desc, json.dumps(faq_schema, ensure_ascii=False)


def rewrite(path: Path, dirname: str, slug: str, kind: str) -> str:
    t = TOOLS[slug]
    html = path.read_text(encoding="utf-8")
    body, title, desc, faq_json = build_body(t, kind, dirname, slug)
    canonical = f"{BASE}/{dirname}/{slug}"

    # ---- head: title / description / og ----
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.S)
    html = re.sub(
        r'(<meta name="description" content=")[^"]*(")',
        lambda m: m.group(1) + desc + m.group(2),
        html,
        count=1,
    )
    html = re.sub(
        r'(<meta property="og:title" content=")[^"]*(")',
        lambda m: m.group(1) + title + m.group(2),
        html,
        count=1,
    )
    html = re.sub(
        r'(<meta property="og:description" content=")[^"]*(")',
        lambda m: m.group(1) + desc + m.group(2),
        html,
        count=1,
    )

    # ---- canonical + hreflang pinned to the NON-slash URL in both twins ----
    html = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{canonical}">',
        html,
        count=1,
    )
    html = re.sub(
        r'(<link rel="alternate" hreflang="[^"]*" href=")[^"]*(">)',
        lambda m: m.group(1) + canonical + m.group(2),
        html,
    )
    html = re.sub(
        r'(<meta property="og:url" content=")[^"]*(")',
        lambda m: m.group(1) + canonical + m.group(2),
        html,
        count=1,
    )

    # ---- replace the FAQPage JSON-LD so schema cannot drift from the visible FAQ ----
    faq_block = f'<script type="application/ld+json">{faq_json}</script>'
    pattern = r'<script type="application/ld\+json">\s*\{[^<]*?"@type"\s*:\s*"FAQPage".*?</script>'
    if re.search(pattern, html, flags=re.S):
        html = re.sub(pattern, faq_block, html, count=1, flags=re.S)
    else:
        html = html.replace("</head>", faq_block + "\n</head>", 1)

    # ---- swap the body content between </nav> and <footer>, preserving both ----
    m_nav = re.search(r"</nav>", html)
    m_foot = re.search(r"<footer", html)
    if not (m_nav and m_foot):
        raise SystemExit(f"{path}: expected nav+footer landmarks, not found — aborting rather than guessing")
    html = html[: m_nav.end()] + "\n" + body + "\n" + html[m_foot.start() :]

    # ---- protection markers (round15 polarity only; never round16/18/19) ----
    for bad in ("isenberg-round16", "isenberg-round18", "isenberg-round19"):
        if bad in html:
            html = html.replace(f"<!-- {bad} -->", "")
    if MARKER not in html:
        html = html.replace("</head>", f"{MARKER}\n{GUARD_NOTE}\n</head>", 1)
    return html


def main() -> None:
    written = 0
    for dirname, slug, kind in PAGES:
        flat = REPO / dirname / f"{slug}.html"
        if not flat.exists():
            print(f"  SKIP (missing) {flat.relative_to(REPO)}")
            continue
        out = rewrite(flat, dirname, slug, kind)
        flat.write_text(out, encoding="utf-8")
        # the dir twin is what round15's skip-guard actually reads
        twin = REPO / dirname / slug / "index.html"
        twin.parent.mkdir(parents=True, exist_ok=True)
        twin.write_text(out, encoding="utf-8")
        written += 2
        print(f"  ✓ {dirname}/{slug}  (flat + dir twin)")
    print(f"\n{written} files written across {len(PAGES)} URLs")


if __name__ == "__main__":
    main()
