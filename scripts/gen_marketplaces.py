#!/usr/bin/env python3
"""/marketplaces/<slug> — churn due diligence by acquisition channel.

Strategic rationale (2026-07-25 traffic audit): acquirers congregate on
marketplaces and broker sites, not on search surfaces for "buyer-side SaaS due
diligence". These pages meet the ICP at the channel they are already using.

Accuracy policy — this family names third parties, so:
  * Marketplace characterisations are limited to structural, widely-understood
    positioning (open vs curated vs brokered) and are hedged.
  * No commission rates, listing counts, multiples, vetting guarantees or any
    other figure is asserted about any named company.
  * Every page carries an explicit unaffiliated / verify-current-terms notice.
  * The substance of each page is ChurnLens's own buyer-side analysis of that
    listing type and deal band, which is ours to state.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pseo_shell import BASE, esc, render, table, write  # noqa: E402

HUB = "/marketplaces"
HUB_NAME = "By Marketplace"

DISCLAIMER = (
    '<p class="pseo-note">ChurnLens is not affiliated with, endorsed by or a partner of any '
    'marketplace or broker named on this page. Listing formats, disclosure practices and '
    'terms change; treat the descriptions here as a starting point and verify current '
    'specifics with the marketplace itself. Nothing here is investment, legal or tax '
    'advice.</p>'
)

MARKETS = [
{
"slug": "flippa",
"name": "Flippa",
"url": "https://flippa.com/",
"kind": "Open, self-serve marketplace",
"band": "predominantly micro and small deals, with a wide quality range",
"title": "Flippa SaaS Due Diligence: Verifying Churn on a Listing | ChurnLens",
"description": "Flippa is open and self-serve, so listing quality varies more than anywhere else and the churn figure is whatever the seller typed. Here is the verification sequence for a Flippa SaaS listing.",
"h1": "Due diligence on a Flippa SaaS listing: verifying the churn number",
"lead": "Flippa's openness is its value and its risk. Anyone can list, which means genuine opportunities sit next to listings whose metrics have never been checked by anyone. The practical consequence for a buyer is that self-reported figures should be treated as the seller's opening position rather than as data.",
"you_get": "Listings typically carry seller-entered financials, a stated asking price, some traffic and revenue claims, and whatever verification or integration the seller chose to connect. Because participation is open and largely self-serve, what is disclosed varies enormously between listings, and the presence of a connected data source on one listing tells you nothing about the next.",
"missing": "Subscription-level detail is almost never present. A listing may show revenue and a churn percentage without any indication of how that percentage was computed, whether free accounts sat in the denominator, or whether cancelled subscriptions were even included in the underlying export. Renewal timing, customer concentration and the split between recurring and one-time revenue are typically absent entirely.",
"traps": [
("Screenshot metrics with no underlying file",
 "A dashboard screenshot establishes that a screen existed, not that the number is right. It cannot show you the definition behind a churn percentage, and it cannot show you the rows that were filtered out. Ask for the export, and treat a refusal as a finding rather than an inconvenience."),
("Revenue that is mostly one-time",
 "At the micro end, businesses described as SaaS frequently sell lifetime deals, one-off licences or setup work alongside subscriptions. Because that revenue arrives through the same billing account, it gets described as recurring. Classify line items before you apply any multiple."),
("A very young book presented as stable retention",
 "A business under eighteen months old has not been through enough renewal cycles for its retention figure to mean much, particularly if it has sold annual plans. Reported stability over a period when leaving was largely unavailable is a property of the calendar."),
("Traffic and revenue from a single channel that will not transfer",
 "Micro SaaS on open marketplaces is often built on one acquisition channel — a directory placement, a marketplace listing, a founder's audience. That channel is frequently the whole business, and it is the part least likely to survive the ownership change."),
],
"process": [
"Read the listing for what it does <em>not</em> say. Absent renewal timing, absent concentration and absent recurring-versus-one-time split are the three most common omissions and the three that most change a valuation.",
"Ask one question before anything else: can you send a subscription-level export including cancelled subscriptions, covering the full history. The answer, and how quickly it arrives, tells you most of what you need to know about the rest of the process.",
"Check the age of the business against its billing interval. If it is annual-heavy and under two years old, its retention record covers a period with few renewal opportunities.",
"Recompute churn yourself in both logo and revenue terms on a paying-only base. Compare against the listing figure and ask about any gap rather than assuming bad faith.",
"Classify revenue into committed recurring, usage, one-time fees and services. At this end of the market the recurring share is the single largest driver of a fair price.",
"Group customers by email domain and check concentration on parent entities rather than accounts.",
"Establish the acquisition channel and whether it depends on a person or a placement that conveys with the asset.",
],
"asks": [
"A subscription-level export including cancelled and past-due rows, full history, from the billing platform directly.",
"Read-only or screen-shared access to the billing dashboard, so the export can be seen being generated.",
"A written statement of how the listing's churn figure was computed.",
"A breakdown of revenue into recurring, one-time and services for the trailing twelve months.",
],
"faqs": [
("How do I verify churn on a Flippa listing?",
 "Ask for a subscription-level export from the billing platform, including cancelled subscriptions, covering the full history, then recompute churn yourself in both logo and revenue terms on a paying-only base. Listing figures are seller-entered and rarely come with a definition attached, so recomputation is the only way to know what you are comparing."),
("Are Flippa SaaS listings reliable?",
 "Reliability varies by listing rather than by marketplace, because Flippa is open and self-serve. Some sellers connect verified data sources and disclose thoroughly; others enter figures by hand. Judge each listing on what it discloses and on how readily the seller produces underlying data, and verify current verification options with Flippa directly."),
("What should I ask for before making an offer on a small SaaS?",
 "A complete subscription export including cancellations, a written statement of how any quoted churn figure was computed, and a split of revenue into recurring, one-time and services. Those three items resolve most of the uncertainty in a micro-SaaS deal, and how quickly they arrive is itself informative."),
],
"related": ["acquire-com", "microns", "tiny-acquisitions", "empire-flippers"],
},
{
"slug": "acquire-com",
"name": "Acquire.com",
"url": "https://acquire.com/",
"kind": "Startup marketplace, founder-to-buyer",
"band": "mostly small startup and SaaS deals",
"title": "Acquire.com Due Diligence: Verifying SaaS Churn | ChurnLens",
"description": "Acquire.com puts buyers in direct contact with founders, which makes diligence conversational rather than documentary. Here is what to ask for and the traps specific to founder-sold SaaS.",
"h1": "Due diligence on an Acquire.com SaaS listing: verifying the churn number",
"lead": "Acquire.com's defining feature for a buyer is direct founder contact. That is genuinely valuable, because you can ask questions no listing format anticipates. It also means diligence tends to happen in conversation, where claims are easy to accept and hard to reconstruct later.",
"you_get": "Listings are prepared by founders, typically with revenue and growth figures, a description of the product and the customer base, and whatever supporting material the founder chose to assemble. Because the marketplace is oriented around founder-to-buyer contact, much of the substantive information arrives in messages and calls rather than in the listing.",
"missing": "Because the process is conversational, there is often no single document that states the retention claim precisely. Renewal calendars, concentration analysis on parent entities, and the recurring-versus-one-time split are usually absent from the listing and only partially covered in conversation. Founder dependency, which at this end of the market is frequently the largest single risk, is almost never quantified.",
"traps": [
("Claims made in conversation rather than in writing",
 "A number given on a call is not a number you can go back to. Confirm every material claim in writing, in the founder's own words, and specifically ask for the formula behind any churn or retention figure. This is not adversarial; it is the only way to discover a definitional difference before it becomes a disagreement."),
("Founder dependency in acquisition and support",
 "Founder-sold startups frequently run on the founder's audience, network and accumulated product knowledge. Ask for acquisition source by month and check what share arrives through channels attributable to a person. Ask what the founder actually did in the last four weeks."),
("A growth narrative built on a short history",
 "Startup listings emphasise trajectory, and a strong recent trend over twelve months can rest on a handful of months. Rebuild the MRR series yourself and decompose it into new, expansion, contraction and churn, because a rising line constrains retention not at all."),
("Relationship-held revenue among the largest accounts",
 "In a founder-run business the biggest customers are often retained by a relationship rather than by a contract. Cross-check the top accounts against tenure and contract status, and ask to speak to them before close rather than after."),
],
"process": [
"Get the retention claim in writing with its formula attached, before you spend time on anything else.",
"Request the subscription-level export directly from the billing platform, including cancelled rows, and recompute churn in both logo and revenue terms.",
"Rebuild the MRR series and decompose it. A monotonic line with rising churn share is the most common finding at this end of the market.",
"Ask for acquisition source per new customer for twelve months, and compute the founder-attributable share.",
"Check the top ten accounts for tenure, contract status and notice period. Long-tenured, large and uncontracted means relationship-held.",
"Ask directly about the last four weeks of the founder's actual work, and about who else touches the business and at what cost.",
"Agree the transition explicitly: what the founder will do, for how long, and what documentation exists before close rather than after.",
],
"asks": [
"A subscription-level export including cancelled and past-due rows, generated in front of you if possible.",
"The formula behind any quoted churn, retention or LTV figure, in writing.",
"Acquisition source per new customer for at least twelve months.",
"Contract status and tenure for the top ten accounts, and a list of everyone who works on the business with their cost.",
],
"faqs": [
("What should I verify on an Acquire.com listing?",
 "The retention claim and its formula in writing, a complete subscription export including cancellations, the MRR decomposition into new, expansion, contraction and churn, and the founder-attributable share of customer acquisition. The last of those is usually the biggest gap between the business the founder runs and the business you would receive."),
("How do I assess founder dependency when buying a small SaaS?",
 "Look for the founder in the data rather than in their stated hours. Acquisition source by month shows whether customers arrive through a system or a person. Tenure and contract status on the largest accounts show whether revenue is held by the product or by a relationship. Support volume against documented process shows whether low hours mean systematised or absorbed."),
("Should I talk to the customers before buying a SaaS business?",
 "Where revenue is concentrated or relationships are long-standing, yes, and before close rather than after. It is a normal request in a deal of any size, usually handled late in the process under confidentiality. A seller's willingness to arrange it is informative in itself."),
],
"related": ["flippa", "microns", "tiny-acquisitions", "off-market"],
},
{
"slug": "empire-flippers",
"name": "Empire Flippers",
"url": "https://empireflippers.com/",
"kind": "Curated marketplace with pre-listing review",
"band": "small to lower mid-market",
"title": "Empire Flippers SaaS Due Diligence: What Vetting Does Not Cover | ChurnLens",
"description": "Curated marketplaces verify that reported figures reconcile to source data. That is not the same as verifying that churn was defined correctly. Here is the gap and how to close it.",
"h1": "Due diligence on an Empire Flippers listing: what the vetting does and does not cover",
"lead": "Curated marketplaces do meaningful work before a listing goes live, and a buyer should give that credit. The distinction worth understanding is between <em>verification</em> and <em>analysis</em>: confirming that a reported figure reconciles to its source is a different exercise from confirming that the figure was the right one to compute.",
"you_get": "Curated listings typically arrive with financials that have been reconciled against source systems, a structured profit-and-loss presentation, and a consistent disclosure format across listings. The consistency is genuinely useful, because it makes listings comparable in a way open marketplaces cannot.",
"missing": "Reconciliation confirms that the numbers tie out. It does not decide whether churn should have been measured on customers or dollars, whether free accounts belonged in the denominator, whether annual plans were treated as unable to churn in non-renewal months, or when the renewal cliff falls. Those are analytical choices, and a verified figure computed under an unfavourable definition is still a figure you need to recompute.",
"traps": [
("Treating verified as analysed",
 "This is the central risk on a curated marketplace and it works in the buyer's blind spot. A reconciled churn figure carries real credibility, which makes it less likely to be recomputed. Recompute it anyway, under your own definition, and expect the number to move even when nothing is wrong with the underlying data."),
("Presentation-layer normalisation",
 "Consistent listing formats require normalising different businesses into one template, and normalisation makes choices. Ask specifically how annual contracts, deferred revenue and one-time fees were treated in the presented figures, because the template had to decide something."),
("Seller discretionary earnings framing",
 "Marketplace P&L presentations often centre on an adjusted earnings figure. Those adjustments are usually reasonable and they are still adjustments. Ask for the unadjusted figures alongside them and form your own view of which add-backs survive under your ownership."),
("Renewal timing still absent",
 "Verification is about amounts, not about schedule. The renewal calendar is almost never part of a listing package at any marketplace, and it is the artifact that determines your first year. Build it yourself from the subscription export."),
],
"process": [
"Read the listing package thoroughly and give the reconciliation the credit it deserves. Then list which of your questions it does not answer, which is usually renewal timing, parent-entity concentration and the recurring-versus-one-time split.",
"Ask what specifically was verified and by what method. The answer is usually more limited and more precise than a buyer assumes, and knowing the boundary is what lets you spend your own effort in the right place.",
"Request the subscription-level export in addition to the listing financials, and recompute churn under your own definition.",
"Build the renewal calendar. It will not be in the package.",
"Recompute concentration on parent entities, grouping by email domain first.",
"Ask for unadjusted financials alongside any adjusted earnings figure, and form your own view on each add-back.",
"Reconcile your recomputed MRR to the presented figures and resolve any gap explicitly rather than splitting the difference.",
],
"asks": [
"A written statement of what was verified pre-listing and by what method.",
"The subscription-level export including cancelled rows, in addition to the summarised financials.",
"Unadjusted financials alongside any adjusted or discretionary-earnings presentation.",
"The treatment applied to annual contracts, deferred revenue and one-time fees in the presented figures.",
],
"faqs": [
("Does a curated marketplace verify SaaS churn?",
 "Curation typically verifies that reported figures reconcile to source systems, which is real and useful work. It does not usually decide whether the churn figure was defined the way a buyer would define it — customers versus dollars, whether free accounts sat in the denominator, how annual plans were handled. Verification and analysis are different exercises, and only the first is normally done for you."),
("Is due diligence still necessary on a vetted listing?",
 "Yes, and it should be aimed differently. Vetting reduces the risk of figures that do not tie out, so your effort is better spent on the analytical questions no listing package answers: renewal timing, concentration on parent entities, the recurring share of revenue, and recomputing retention under your own definition."),
("What is missing from most marketplace listing packages?",
 "The renewal calendar, almost always. Listings present amounts, and a renewal calendar is a schedule — which month each annual contract comes up, and therefore how much revenue is decided in a single month. It is the artifact that most shapes a buyer's first year and it is rarely included anywhere."),
],
"related": ["fe-international", "quiet-light", "investors-club", "flippa"],
},
{
"slug": "fe-international",
"name": "FE International",
"url": "https://feinternational.com/",
"kind": "Sell-side M&A advisory",
"band": "small to mid-market SaaS",
"title": "FE International SaaS Due Diligence: Buying Through a Sell-Side Broker | ChurnLens",
"description": "A sell-side advisor represents the seller, and a professionally prepared package is designed to answer the questions it chose to raise. Here is how to run buyer-side churn diligence through a broker process.",
"h1": "Due diligence on an FE International listing: buying through a sell-side advisor",
"lead": "The single most useful thing to hold in mind in a brokered process is whose interests the advisor represents. A sell-side advisor works for the seller, and a professionally prepared information package is genuinely informative and also constructed. Your job is to ask the questions the package did not choose to answer.",
"you_get": "Brokered processes typically produce a substantial information memorandum with structured financials, a product and market description, customer information at an aggregate level, and a managed question-and-answer process. The quality of preparation is usually high, and it makes the business easier to understand quickly.",
"missing": "What a prepared package rarely contains is the raw material for an independent recomputation. Aggregate customer information is not a subscription export. Cohort retention curves, the renewal calendar, parent-entity concentration and the decomposition of MRR growth into its four components are typically absent, and they are the analyses that produce a different answer from the one presented.",
"traps": [
("A managed process discourages the awkward request",
 "Brokered processes run on timelines and structured question rounds, which creates real pressure to work from what has been provided. The subscription-level export is the request most likely to be deferred and the most important one to make. Make it early and in writing, and treat repeated deferral as information."),
("Aggregate cohort data instead of rows",
 "A cohort retention table prepared by the seller's advisor has already made every definitional choice. Ask for the underlying subscription rows so the table can be reproduced. If only the table is available, note in your memo that retention is unverified rather than treating the table as verification."),
("Competitive tension as a substitute for diligence",
 "A well-run process creates urgency, and urgency is where diligence gets shortened. Decide before the process starts which analyses you will not proceed without, and hold that line independently of how many other bidders you are told about."),
("Adjusted figures throughout",
 "Prepared packages present normalised and adjusted figures for good reasons. Every adjustment is a judgment, and add-backs that are reasonable for the seller may not survive your ownership. Ask for unadjusted figures and rebuild the adjustments yourself."),
],
"process": [
"Before engaging, write down the analyses you will not proceed without. In our view that is: recomputed churn from subscription rows, the renewal calendar, parent-entity concentration, and the recurring share of revenue.",
"Request the subscription-level export in your first written question round. Early and in writing matters, because a late request looks like a delay tactic within a managed timeline.",
"Recompute churn in both logo and revenue terms rather than accepting the prepared cohort table, and reconcile your figure to theirs.",
"Build the renewal calendar from the rows. It will not be in the memorandum.",
"Recompute concentration on parent entities, and ask explicitly which of the largest accounts share a parent or a buying decision.",
"Rebuild the adjusted earnings figure from unadjusted financials and form your own view on each add-back.",
"Ask for customer calls or references before exclusivity, not after. Where revenue is concentrated this is a reasonable and normal request.",
],
"asks": [
"A subscription-level export including cancelled and past-due rows, in the first question round.",
"Unadjusted financials alongside the adjusted presentation, with each add-back itemised.",
"Cohort retention with the underlying rows, not only the summary table.",
"Contract terms, renewal dates and parent-entity relationships for every account above 2% of revenue.",
],
"faqs": [
("Does a sell-side broker work for the buyer?",
 "No. A sell-side advisor is engaged by and paid by the seller, and their duty is to the seller. That does not make the information they prepare unreliable, but it does mean the package is designed to answer the questions the seller's side chose to raise. Buyer-side analysis remains the buyer's job."),
("What should I request first in a brokered SaaS process?",
 "The subscription-level export including cancelled subscriptions, in writing, in your first question round. It is the request most likely to be deferred and the one everything else depends on, and asking early avoids it looking like a delay tactic inside a managed timeline."),
("Can I trust a cohort retention table prepared by the seller's advisor?",
 "Treat it as a claim rather than as evidence. The table has already made every definitional choice — the denominator, customers versus dollars, the handling of annual plans — and those choices are exactly what a buyer needs to set independently. Ask for the underlying rows; if only the table is available, record retention as unverified."),
],
"related": ["quiet-light", "website-closers", "empire-flippers", "latonas"],
},
{
"slug": "quiet-light",
"name": "Quiet Light",
"url": "https://quietlight.com/",
"kind": "Brokerage with operator-advisors",
"band": "small to lower mid-market",
"title": "Quiet Light SaaS Due Diligence: Verifying Churn in a Brokered Deal | ChurnLens",
"description": "Advisors who have operated businesses themselves give better context and are still sell-side. Here is how to use that context well while running your own churn verification.",
"h1": "Due diligence on a Quiet Light listing: using operator context without outsourcing judgment",
"lead": "Brokerages staffed by people who have run and sold businesses themselves tend to produce better qualitative context than a purely transactional process does. That context is worth a lot and it does not substitute for recomputation, because the advisor's duty still runs to the seller.",
"you_get": "Typically a prepared listing with financials, a narrative explanation of how the business operates, and access to an advisor who can usually answer operational questions with genuine understanding rather than by relaying them. That operational fluency is the real asset in this kind of process and it is worth using heavily.",
"missing": "Qualitative depth does not produce a subscription export. The analyses that most often change a price — recomputed churn under a buyer's definition, the renewal calendar, parent-entity concentration, the recurring share of revenue, and the founder-attributable share of acquisition — are not usually in the listing and are not what an advisor's narrative is for.",
"traps": [
("Good rapport substituting for verification",
 "An advisor who explains the business well and answers candidly is genuinely useful and is not a source of independent verification. The better the qualitative process, the easier it is to skip the arithmetic. Run it anyway."),
("Operational explanations that resolve too neatly",
 "Experienced advisors are good at explaining anomalies, and most explanations are true. The ones worth testing are those where the explanation is unfalsifiable from the data you have — a churn spike attributed to seasonality with only eighteen months of history, for instance. Ask for the data that would settle it."),
("Owner-operator dependency framed as owner involvement",
 "In owner-operated businesses the line between the owner's effort and the business's systems is genuinely blurry, and a narrative naturally describes it favourably. Quantify it: acquisition source by month, contract status on the largest accounts, documented process against support volume."),
("Trailing figures that end at the best month",
 "Any trailing-twelve-month presentation ends somewhere. Ask for the series rather than the total, and look at the most recent two quarters on their own."),
],
"process": [
"Use the advisor heavily for operational understanding. This is where a broker with operating experience adds the most value, and questions about how the business actually runs are worth asking at length.",
"Separately and in parallel, request the subscription-level export and recompute churn yourself in both logo and revenue terms.",
"For every anomaly the advisor explains, ask what data would confirm the explanation, then ask for that data. Most explanations survive; the ones that cannot be tested should be recorded as untested.",
"Build the renewal calendar and check the largest single renewal month.",
"Quantify owner dependency: founder-attributable acquisition share, contract status on the top accounts, documentation against support volume.",
"Ask for the monthly series behind every trailing-twelve-month figure, and read the last two quarters separately.",
"Recompute concentration on parent entities rather than accounts.",
],
"asks": [
"The subscription-level export including cancelled rows, full history.",
"Monthly series behind every trailing-twelve-month figure presented.",
"Acquisition source per new customer for twelve months.",
"Whatever data would confirm each anomaly explanation given verbally, requested explicitly.",
],
"faqs": [
("Is a broker with operating experience better for a buyer?",
 "Usually better to work with, because operational questions get substantive answers rather than being relayed. It does not change whose interests they represent: a sell-side advisor is engaged by the seller regardless of their background. Use the context heavily and keep the verification yours."),
("How do I test a verbal explanation for a churn anomaly?",
 "Ask what data would confirm it, then ask for that data. A seasonality claim needs the same month across multiple years. A price-increase explanation needs the pricing history with dates. A one-off incident needs the incident log. Most explanations survive this; the ones that cannot be tested belong in the memo as untested rather than as resolved."),
("What does owner dependency look like in the numbers?",
 "Acquisition source concentrated in channels attributable to a person, largest accounts that are long-tenured and uncontracted, and low support hours with no documentation or second person. Each is measurable from data a seller can produce, which turns a narrative question into an evidential one."),
],
"related": ["fe-international", "website-closers", "empire-flippers", "off-market"],
},
{
"slug": "website-closers",
"name": "Website Closers",
"url": "https://websiteclosers.com/",
"kind": "Broad-mandate brokerage",
"band": "wide range across ecommerce, content and SaaS",
"title": "Website Closers SaaS Due Diligence: Churn Checks in a Broad-Mandate Brokerage | ChurnLens",
"description": "Brokerages that cover ecommerce, content and SaaS together apply frameworks built for other business models. Here is which SaaS-specific analyses fall through the gap.",
"h1": "Due diligence on a Website Closers SaaS listing: what a broad mandate misses",
"lead": "Brokerages with a wide mandate across ecommerce, content and software see far more deals, which is useful. The consequence for a SaaS buyer is that presentation frameworks are necessarily general, and the analyses that matter most in subscription businesses are the ones a general framework does not have a slot for.",
"you_get": "Typically a prepared listing with financials, growth history and an operational description, formatted consistently across a range of business models. The breadth means comparability across categories and a large pipeline, and it usually means solid coverage of the things all businesses share: revenue, margin, expenses, growth.",
"missing": "Subscription-specific analysis. Ecommerce and content frameworks centre on revenue, margin and traffic, none of which capture retention mechanics. Cohort retention, the renewal calendar, the split between committed recurring and usage revenue, contraction as distinct from churn, and concentration on parent entities are typically absent because the framework was not built to ask for them.",
"traps": [
("Traffic and revenue growth presented as the core story",
 "In content and ecommerce that framing is correct. In SaaS it omits retention entirely, and a rising revenue line is fully compatible with deteriorating retention. Ask for the MRR decomposition into new, expansion, contraction and churn."),
("Recurring revenue asserted rather than classified",
 "Where a framework has one revenue line, setup fees, usage overage, services and subscriptions all land in it. Classify line items and apply the multiple bucket by bucket, because a business that is 75% committed recurring is priced differently from one that is 95%."),
("Contraction invisible entirely",
 "General frameworks have no concept of a customer who stays and shrinks. Downgrades take revenue without appearing in any customer-count measure, and on some books contraction exceeds outright churn. Measure it separately."),
("Churn quoted as a single blended percentage",
 "A single figure with no definition attached, no logo-versus-revenue split and no cohort structure is the default output of a general framework. Recompute all of it; there is usually no underlying analysis to reconcile against, which makes the job simpler rather than harder."),
],
"process": [
"Assume the SaaS-specific analyses have not been done, and plan to do all of them yourself. This is a scoping decision, not a criticism of the process.",
"Request the subscription-level export first, since almost everything you need is downstream of it.",
"Recompute churn in both logo and revenue terms, and take the ratio between them.",
"Measure contraction separately: revenue lost from accounts that shrank but stayed.",
"Classify revenue into committed recurring, usage, one-time and services, and value each bucket appropriately.",
"Build the renewal calendar and identify the largest renewal month.",
"Recompute concentration on parent entities, and check renewal-month clustering as a second form of concentration.",
],
"asks": [
"A subscription-level export including cancelled and past-due rows, full history.",
"A line-item or charge-level revenue export so recurring, usage, one-time and services can be separated.",
"Plan-change history, so downgrades can be distinguished from cancellations.",
"Email domain and company name per account, so concentration can be computed on parent entities.",
],
"faqs": [
("What is different about SaaS due diligence versus ecommerce?",
 "Retention mechanics. Ecommerce diligence centres on revenue, margin, traffic and supply; SaaS diligence centres on whether revenue persists, which requires cohort analysis, a renewal calendar, contraction measured separately from churn, and a split between committed recurring and usage revenue. A framework built for one does not naturally ask for the other."),
("Why does contraction matter as much as churn?",
 "Because a customer who downgrades from $500 to $50 has taken 90% of their revenue away without appearing in any customer-count measure. On books with expansion mechanics, contraction is frequently larger than outright churn, and it is invisible unless measured deliberately as revenue lost from accounts that shrank but stayed."),
("Should I expect a broker to have done cohort analysis?",
 "Not usually, particularly where the mandate spans several business models. Plan to do it yourself and scope your diligence accordingly. The advantage is that with no prepared analysis to reconcile against, you are free to define every measure the way a buyer should."),
],
"related": ["fe-international", "quiet-light", "latonas", "flippa"],
},
{
"slug": "microns",
"name": "Microns",
"url": "https://microns.io/",
"kind": "Micro-SaaS marketplace",
"band": "micro deals, often single-founder products",
"title": "Microns Due Diligence: Verifying Churn on a Micro-SaaS Listing | ChurnLens",
"description": "At micro scale, small absolute numbers make every rate statistically noisy and founder dependency is usually the whole risk. Here is how to run diligence when the sample size is tiny.",
"h1": "Due diligence on a Microns micro-SaaS listing: diligence at small sample sizes",
"lead": "Micro-SaaS diligence has a distinct statistical problem: with fifty or a hundred customers, a churn rate computed over one month is dominated by noise. Two cancellations instead of one doubles the rate. The methods that work at scale mislead here, and the analysis has to change accordingly.",
"you_get": "Listings typically carry revenue, customer count, a product description and the founder's account of how the business runs. At this scale the founder usually knows every customer, so qualitative information about the customer base is often unusually good and worth asking for at length.",
"missing": "Statistical reliability, mostly. With small customer counts there is no stable monthly churn rate to report, and cohort analysis has cohorts of five. Renewal timing, concentration and founder dependency all matter more than at scale and are rarely quantified. The recurring-versus-one-time split is frequently unclear because micro products often sell lifetime deals.",
"traps": [
("Monthly rates that are statistically meaningless",
 "With a hundred customers, monthly churn moves by a full percentage point on a single cancellation. Do not compute monthly rates. Use twelve-month windows, absolute counts alongside percentages, and survival analysis on the customer base as a whole rather than cohort-by-cohort."),
("Concentration that is structural at this scale",
 "With fifty customers, the largest is likely to be several percent of revenue by arithmetic alone. The right question is not whether concentration exists but whether the top few accounts are contractually secured and whether you could survive losing the largest one in month two."),
("Lifetime deals in the revenue base",
 "Micro-SaaS is where lifetime deals are most common, and they are one-time revenue with a permanent support obligation. A business with a large lifetime cohort has both less recurring revenue and more ongoing cost than its headline suggests."),
("The founder is the business",
 "At this scale founder dependency is usually the dominant risk rather than one risk among several. Acquisition is often entirely the founder's audience or a single directory placement, and support is entirely the founder. Assume it unless the data shows otherwise."),
],
"process": [
"Work in absolute numbers alongside percentages throughout. \"Three customers left last quarter\" is more informative than \"6% quarterly churn\" when the base is fifty.",
"Use twelve-month windows rather than monthly rates, and look at the survival of the whole base rather than at cohorts too small to mean anything.",
"Ask for the full customer list with tenure, plan and revenue. At this scale you can genuinely review every account individually, which is a luxury that disappears at scale.",
"Identify lifetime deals and any non-recurring revenue explicitly, and value them separately.",
"Assume founder dependency and try to disprove it: acquisition source, support process, documentation, who else touches the business.",
"Establish what happens to the single largest customer if you change anything, and whether there is a contract.",
"Check the technical situation directly — deployment, dependencies, single points of failure — because at this scale deferred maintenance becomes your first month's work.",
],
"asks": [
"The full customer list with tenure, plan, revenue and status. At this size, all of it.",
"An explicit list of lifetime or one-time purchases within the customer base.",
"Acquisition source for every customer acquired in the last twelve months.",
"The deployment process, dependency status and anything only the founder can do.",
],
"faqs": [
("How do you measure churn for a SaaS with under 100 customers?",
 "Not with monthly rates, which move a full point on a single cancellation. Use twelve-month windows, report absolute counts alongside percentages, and look at survival across the whole customer base rather than cohort-by-cohort. At this size you can also simply review every account individually, which beats any rate."),
("Are lifetime deals a problem when buying a micro-SaaS?",
 "They are one-time revenue with a permanent support and hosting obligation, so they should sit outside MRR and outside the subscription multiple, with their ongoing cost treated as a going-forward expense. A large lifetime cohort means less recurring revenue and more cost than the headline figures suggest."),
("What matters most in micro-SaaS due diligence?",
 "Founder dependency, in most cases. At this scale acquisition is often entirely the founder's audience or one placement, and support is entirely the founder. The retention arithmetic still matters, but the question of what actually transfers usually determines the outcome."),
],
"related": ["tiny-acquisitions", "sideprojectors", "acquire-com", "flippa"],
},
{
"slug": "tiny-acquisitions",
"name": "Tiny Acquisitions",
"url": "https://tinyacquisitions.com/",
"kind": "Micro-startup marketplace",
"band": "very small deals, often pre-revenue or early-revenue",
"title": "Tiny Acquisitions Due Diligence: Buying Very Small SaaS | ChurnLens",
"description": "At very small scale the question shifts from retention analysis to whether there is enough history to analyse at all. Here is how to run proportionate diligence and what to skip.",
"h1": "Due diligence on a Tiny Acquisitions listing: proportionate diligence at very small scale",
"lead": "At the smallest end of the market, elaborate diligence costs more than the asset. The useful discipline is proportionality: identify the two or three things that could make this a bad purchase, check those properly, and consciously skip the rest rather than performing a scaled-down version of a large-deal process.",
"you_get": "Listings are typically brief, with revenue if any, a product description, and the builder's account of traction. Many listings at this end are early-revenue or pre-revenue, which means there is often genuinely no retention history to examine.",
"missing": "Usually, sufficient history. A product with six months of revenue and twenty customers cannot produce a meaningful churn rate, and pretending otherwise wastes effort. What is also typically missing is clarity about what is actually being transferred: code, customers, domain, accounts, or some subset.",
"traps": [
("Analysing a rate when there is no sample",
 "Twenty customers over six months does not support a churn rate. Say so in your own notes rather than computing one. The honest position is that retention is unknown, and the purchase decision has to rest on something else — the code, the domain, the customer list as a list."),
("Unclear asset boundaries",
 "At this scale the most common problem is not a bad number, it is ambiguity about what conveys: the domain, the code, the customer relationships, the billing account, the analytics history, third-party accounts and API keys. Get an explicit written asset list, because it is cheap to get and expensive to discover afterwards."),
("Revenue that is a handful of friendly accounts",
 "Very early revenue is frequently friends, colleagues or the builder's own audience buying to be supportive. Those accounts behave nothing like arm's-length customers. Ask directly, and ask how many customers the builder had never met before purchase."),
("Transfer mechanics on third-party dependencies",
 "Small products often depend on API keys, app-store accounts, OAuth apps and platform listings that may not be transferable at all. This is a practical blocker rather than a valuation question, and it is worth checking before the money moves rather than after."),
],
"process": [
"Decide up front what could make this a bad purchase at this price. Usually it is not the churn rate; it is whether the asset transfers cleanly and whether the revenue is arm's-length.",
"Get an explicit written list of everything that conveys: domain, code repository, billing account, customer records, third-party accounts, API keys, app-store or marketplace listings.",
"Check every third-party dependency for transferability before agreeing terms. Some genuinely cannot move.",
"Ask how many customers are arm's-length, and how many the builder knew before they bought.",
"If there is enough history to look at, use absolute numbers over twelve months. If there is not, record retention as unknown rather than estimating it.",
"Verify the revenue exists at all by seeing the billing account, ideally live rather than as a screenshot.",
"Skip the analyses that cannot pay for themselves at this deal size, deliberately and in writing, so you know what you chose not to check.",
],
"asks": [
"A written list of every asset that conveys, and every third-party account or key required to operate the product.",
"Live or screen-shared view of the billing account showing actual revenue.",
"A statement of how many customers are arm's-length versus known to the seller.",
"Confirmation of transferability for each third-party dependency, ideally checked against the provider's own terms.",
],
"faqs": [
("How much due diligence is proportionate for a very small SaaS purchase?",
 "Enough to answer the two or three questions that could make it a bad purchase at that price, and no more. Usually that means verifying the revenue exists, confirming what actually transfers, and establishing whether the customers are arm's-length. Retention analysis often cannot be done at all, and saying so is better than estimating it."),
("What is most often overlooked when buying a very small SaaS?",
 "Asset boundaries. Which of the domain, code, billing account, customer records, third-party accounts, API keys and marketplace listings actually convey, and whether each can be transferred at all under the provider's terms. It costs almost nothing to establish in writing beforehand and is expensive to discover after."),
("Can you calculate churn on six months of data?",
 "Not meaningfully, especially with a small customer count. The right output is that retention is unknown, which is a legitimate finding and better than a number with no support behind it. The purchase decision then has to rest on something you can actually assess."),
],
"related": ["microns", "sideprojectors", "acquire-com", "flippa"],
},
{
"slug": "sideprojectors",
"name": "SideProjectors",
"url": "https://www.sideprojectors.com/",
"kind": "Side-project marketplace",
"band": "very small, frequently pre-revenue",
"title": "SideProjectors Due Diligence: Buying a Side Project With Revenue | ChurnLens",
"description": "Side projects are usually bought for the code, audience or domain rather than for retained revenue. Here is how to tell which you are buying and what to check for each.",
"h1": "Due diligence on a SideProjectors listing: what you are actually buying",
"lead": "Most side-project purchases are not really revenue acquisitions. They are purchases of code, a domain, an audience, a user base or a head start, and any revenue is incidental. Working out which of those you are buying changes the entire diligence exercise, and it is worth deciding explicitly before you start.",
"you_get": "Listings are typically short, describing the project, its stage, whatever traction exists and the builder's reason for selling. Revenue, where present, is usually small and recent. The most useful information is often about the technology and the user base rather than the financials.",
"missing": "Almost all financial diligence material, usually because there is not much to document. What matters more here and is equally often missing: the state of the code, the transferability of accounts and dependencies, whether users are active, and whether the domain or audience has any real standing.",
"traps": [
("Buying revenue when you are actually buying code",
 "If the revenue is small and young, you are buying an asset rather than a cash flow, and it should be valued that way. Decide which thesis you are underwriting and apply the matching diligence: for code, that is a technical review; for an audience, engagement data; for revenue, the retention analysis."),
("Users who are registered but inactive",
 "A user count is not a user base. Ask for active users on a stated definition — logged in within thirty days is a reasonable one — and treat registration totals as a vanity figure. This is the most common overstatement at this end of the market and it is not usually intended as one."),
("Code that cannot be maintained by anyone else",
 "Side projects are built for one person's convenience. Unusual stacks, absent documentation, no tests and hard-coded configuration are normal rather than exceptional. Have someone read the code before you agree a price, since the cost of taking it over is the real cost of the purchase."),
("Non-transferable platform dependencies",
 "OAuth applications, app-store accounts, API keys with individual terms, free-tier services tied to a personal account: any of these can block a transfer outright. Check them against the provider's own terms rather than the seller's assurance."),
],
"process": [
"Write down which thesis you are buying: code, audience, domain, users or revenue. Then run the diligence that matches it, and skip the rest.",
"If revenue is part of the thesis, verify it exists in the billing account directly and check whether it is arm's-length.",
"Ask for active users on a stated definition, not registrations. Ask for the definition in writing.",
"Have the code reviewed by someone who will have to maintain it, before agreeing a price.",
"Check every third-party dependency for transferability against the provider's terms.",
"Get an explicit written asset list covering domain, repository, accounts, keys, data and any user records.",
"Confirm the data-protection position on any user records that transfer, since that obligation moves with them.",
],
"asks": [
"A written statement of what conveys, including all accounts, keys and third-party services.",
"Active users on a stated definition, alongside total registrations.",
"Repository access for a technical review before price agreement.",
"Live view of any billing account, and confirmation of which customers are arm's-length.",
],
"faqs": [
("What should I check before buying a side project?",
 "First decide what you are actually buying — code, audience, domain, users or revenue — because that determines everything else. Then check what conveys, whether third-party dependencies can transfer at all, and whether the user or revenue figures mean what they appear to. A technical review before price agreement is usually the highest-value step."),
("Are registered users worth anything?",
 "Much less than active users, and the gap is usually large. Ask for actives on a stated definition, such as logged in within the last thirty days, and treat total registrations as a vanity figure. This is rarely intended as an overstatement; it is simply the number most builders have to hand."),
("Can a side project's accounts and API keys be transferred?",
 "Sometimes, and sometimes not at all. OAuth applications, app-store developer accounts, individually-termed API keys and free-tier services tied to a personal account can each block a transfer outright. Check each against the provider's own terms rather than relying on the seller's assurance, and do it before agreeing terms."),
],
"related": ["tiny-acquisitions", "microns", "acquire-com", "off-market"],
},
{
"slug": "investors-club",
"name": "Investors Club",
"url": "https://investors.club/",
"kind": "Curated marketplace with membership access",
"band": "small online businesses including SaaS",
"title": "Investors Club Due Diligence: Verifying Churn on a Curated Listing | ChurnLens",
"description": "Membership-gated curated marketplaces reduce noise and can create a sense that diligence is already handled. Here is what curation covers and the subscription-specific gap it leaves.",
"h1": "Due diligence on an Investors Club listing: curation is a filter, not an analysis",
"lead": "Membership-gated curated marketplaces genuinely reduce the volume of unserious listings, which saves a buyer real time. The failure mode is subtle: a smaller, better-presented pipeline makes each listing feel pre-cleared, and pre-clearing a listing is not the same as analysing a subscription book.",
"you_get": "Typically a structured listing with reviewed financials, a consistent presentation format, and a pipeline filtered for seriousness before it reaches members. The consistency and the filtering are the product, and both are useful.",
"missing": "The subscription-specific analyses, as with every curated channel. Cohort retention under a buyer's definition, the renewal calendar, parent-entity concentration, contraction measured separately from churn, and the classification of revenue into recurring, usage, one-time and services are not usually part of a curation process because curation is a filter rather than an analysis.",
"traps": [
("Curation read as clearance",
 "This is the specific risk of a well-curated pipeline. Fewer, better listings feel vetted in a stronger sense than they are. Ask precisely what the curation process checks, and treat everything outside that boundary as your own work."),
("A smaller pipeline creating urgency",
 "Curated marketplaces list less, which makes each listing feel scarcer and shortens deliberation. Decide your minimum diligence set before you see a listing you like, and keep it independent of how scarce the opportunity feels."),
("Consistent formatting hiding model differences",
 "A single presentation template applied across content sites, ecommerce and SaaS necessarily normalises. Ask how recurring revenue, deferred revenue and one-time fees were treated in the presented figures, because the template had to make a choice."),
("Aggregate customer metrics only",
 "Curated listings typically present customer counts and averages rather than rows. Averages cannot reveal concentration, renewal clustering or the divergence between logo and revenue churn. Ask for the subscription-level export separately."),
],
"process": [
"Ask what the curation process actually checks, in specific terms, and write down the boundary. Everything outside it is yours.",
"Fix your minimum diligence set before evaluating any specific listing, so scarcity does not shorten it.",
"Request the subscription-level export in addition to the listing package, and recompute churn in both logo and revenue terms.",
"Build the renewal calendar and find the largest single renewal month.",
"Recompute concentration on parent entities by grouping on email domain, then on normalised company name.",
"Measure contraction separately from churn.",
"Ask how recurring, deferred and one-time revenue were treated in the presented figures, and reconcile to your own classification.",
],
"asks": [
"A specific written description of what the curation process verifies.",
"The subscription-level export including cancelled rows, in addition to summarised figures.",
"Account-level revenue with email domain, rather than aggregate customer metrics.",
"The treatment of recurring, deferred and one-time revenue in the presented financials.",
],
"faqs": [
("Does a curated marketplace remove the need for due diligence?",
 "No. Curation is a filter on which listings appear, and sometimes a check that figures reconcile. Neither decides whether churn was defined the way a buyer would define it, when the renewal cliff falls, or how concentrated revenue is at parent-entity level. Ask what the process checks and treat the rest as your own work."),
("Why do curated listings still need churn recomputation?",
 "Because a reconciled figure can still be the wrong figure. Whether free accounts sat in the denominator, whether the rate counts customers or dollars, and how annual plans were treated in non-renewal months are analytical choices, not reconciliation questions, and each moves the answer materially."),
("What should I ask a curated marketplace about its process?",
 "Specifically what is verified and by what method — which figures are traced to source systems, whether subscription-level data is examined, whether any retention analysis is performed, and what is taken from the seller as given. Knowing the boundary is what lets you spend your own effort where it counts."),
],
"related": ["empire-flippers", "latonas", "fe-international", "flippa"],
},
{
"slug": "latonas",
"name": "Latona's",
"url": "https://latonas.com/",
"kind": "Established brokerage",
"band": "small to mid-market online businesses",
"title": "Latona's Due Diligence: Churn Verification in a Brokered SaaS Deal | ChurnLens",
"description": "Long-established brokerages bring process discipline and sell-side representation. Here is how to run buyer-side subscription analysis inside a structured broker process.",
"h1": "Due diligence on a Latona's listing: buyer-side analysis inside a broker process",
"lead": "Long-established brokerages tend to run disciplined, well-documented processes, which makes a deal easier to move through and does not change who the advisor represents. The practical question for a buyer is how to fit independent subscription analysis into a structured process without appearing to obstruct it.",
"you_get": "Typically a prepared information package with financials and operational detail, a defined process with stages and timelines, and an intermediary managing information flow. Process discipline is the real benefit and it is worth working with rather than against.",
"missing": "The subscription-level analyses. A prepared package presents amounts and history; it does not usually contain cohort retention under a buyer's definition, the renewal calendar, parent-entity concentration or the decomposition of MRR movement. Those need the underlying rows, and rows are not usually what a package contains.",
"traps": [
("Requests arriving too late in the process",
 "A structured process has stages, and a request for subscription-level rows in a late stage reads as a delay or a retrade. Make the request in the first written round, when it is simply a normal information request, and repeat it in writing if it is deferred."),
("Information flowing only through the intermediary",
 "Managed information flow is efficient and it adds a translation layer, which is where definitional detail is most often lost. Where a formula or a data-model question matters, ask for it in writing so the answer comes back in the seller's own words rather than paraphrased."),
("Process momentum compressing analysis",
 "Well-run processes move. Decide your minimum analysis set in advance and treat it as fixed, because the point at which you are most inclined to shorten it is the point at which shortening it is most expensive."),
("Adjusted earnings presented as the headline",
 "Standard practice, reasonable, and still a set of judgments. Ask for unadjusted figures with each add-back itemised, and decide for yourself which survive under your ownership rather than under the seller's."),
],
"process": [
"Submit the subscription-level export request in the first written information round, framed as routine.",
"Fix your minimum analysis set before the process gains momentum, and record it.",
"Where a definition matters, ask for it in writing and ask for the seller's own wording rather than a summary.",
"Recompute churn in both logo and revenue terms and reconcile explicitly to the presented figures.",
"Build the renewal calendar; it will not be in the package.",
"Rebuild adjusted earnings from unadjusted figures, itemising each add-back and forming your own view.",
"Ask for customer references or calls before exclusivity where revenue is concentrated.",
],
"asks": [
"The subscription-level export including cancelled rows, requested in the first information round.",
"Unadjusted financials with every add-back itemised.",
"Written answers in the seller's own words for any question about formulas or data definitions.",
"Contract terms, renewal dates and parent-entity relationships for accounts above 2% of revenue.",
],
"faqs": [
("When should I ask for subscription-level data in a brokered process?",
 "In the first written information round. It is the request most likely to be deferred and everything else depends on it, and asking early means it reads as a routine information request rather than as a delay or a retrade in a later stage."),
("Why ask for written answers rather than accepting the broker's summary?",
 "Because managed information flow adds a translation layer, and definitional detail is exactly what gets lost in paraphrase. When you need to know how a churn figure was computed or how annual plans were treated, the seller's own wording is the answer; a summary of it is not."),
("What is the risk of process momentum in a broker-led deal?",
 "That analysis gets compressed precisely when it matters most. Well-run processes move quickly and create real pressure to work from what has been provided. Deciding your minimum analysis set in advance, and recording it, is what keeps that decision from being made under time pressure."),
],
"related": ["fe-international", "quiet-light", "website-closers", "investors-club"],
},
{
"slug": "off-market",
"name": "Off-market and direct deals",
"url": "",
"kind": "Direct approach, no intermediary",
"band": "any size, most common at the smaller end",
"title": "Off-Market SaaS Acquisitions: Due Diligence Without a Listing | ChurnLens",
"description": "In a direct deal there is no listing, no prepared package and no process, which means better prices and no structure at all. Here is how to run churn diligence from a cold start.",
"h1": "Off-market SaaS acquisitions: due diligence when there is no listing",
"lead": "Approaching an owner directly usually means less competition and a better price, and it also means nothing has been prepared. There is no information package, no verified figures, no process and often no seller who has thought about selling. Every structure has to come from you, which is an advantage as well as a burden: you get to define what gets measured.",
"you_get": "Whatever the owner is willing to assemble, which early on is usually nothing formal. What you do get is direct access, time, and the ability to shape the process — including which analyses get run and how retention is defined, which in a brokered deal has already been decided for you.",
"missing": "Everything documentary. There is no P&L presentation, no cohort table, no verified revenue figure and frequently no clear sense from the owner of what their own churn rate is. There is also no confidentiality framework and no agreed process, both of which need establishing before substantive information moves.",
"traps": [
("No confidentiality framework in place",
 "In a direct approach nothing protects either side initially. Put a mutual confidentiality agreement in place before substantive data moves, both because it is the right thing to do and because an owner who has not sold before will be reasonably cautious about handing over customer data."),
("An owner who does not know their own numbers",
 "This is common and it is not a bad sign. Many profitable small SaaS owners have never computed churn, and the figure they offer is a guess. Rather than testing their number, help them produce the export and compute it yourself — then share the result, since a seller who trusts your arithmetic is easier to transact with."),
("An unanchored price expectation",
 "With no listing and no comparable process, price expectations can start anywhere. Ground the conversation in the analysis rather than in a multiple: an agreed view of retention, revenue quality and concentration gives both sides something to negotiate from."),
("Diligence drifting because nothing forces a stage",
 "Without a broker's timeline, a direct process can run for months and never quite finish. Set your own stages and your own information requests explicitly, in writing, so that both sides know what completion looks like."),
],
"process": [
"Put a mutual confidentiality agreement in place before requesting any customer data.",
"Set out your own process in writing: what you want to see, in what order, and what each stage leads to. Nobody else will.",
"Expect to help the owner generate the export. Point them at the platform-specific request wording rather than asking for a churn figure.",
"Recompute everything yourself from rows: churn in logo and revenue terms, the renewal calendar, parent-entity concentration, the recurring share of revenue.",
"Share your analysis with the owner. In a direct deal this builds the trust the process is otherwise missing, and it usually surfaces context that changes your reading.",
"Quantify owner dependency early, because in off-market deals the owner is often more involved than in a business that was prepared for sale.",
"Agree the transition explicitly, since there is no standard process to fall back on.",
],
"asks": [
"A mutual confidentiality agreement, before any customer data.",
"The subscription-level export, generated together if that is easier than requesting it.",
"Read-only or screen-shared access to the billing platform.",
"An honest account of what the owner actually does each week, and who else is involved.",
],
"faqs": [
("How do you do due diligence on an off-market SaaS deal?",
 "You supply the structure that a listing and a broker would otherwise provide: a confidentiality agreement first, then a written process with stages and information requests, then recomputing everything yourself from the subscription rows. Expect to help the owner produce the export, since many have never generated one."),
("What if the seller does not know their own churn rate?",
 "It is common among profitable small SaaS businesses and is not a warning sign. Help them generate the export rather than pressing for a number, compute the rate yourself, and share the result. In a direct deal that transparency does more for the transaction than a negotiating advantage would."),
("Is buying off-market cheaper than through a marketplace?",
 "Often, because there is no competitive process and no intermediary fee, and the tradeoff is that you absorb the work a prepared process would have done. Whether that is worth it depends on how much diligence capacity you have and how well you can structure a process from scratch."),
],
"related": ["acquire-com", "microns", "quiet-light", "sideprojectors"],
},
]

BY_SLUG = {m["slug"]: m for m in MARKETS}

# ---------------------------------------------------------------------------


def build_body(m: dict) -> str:
    o = []
    o.append(f'<p><strong>TL;DR:</strong> {m["description"]}</p>')

    o.append("<h2>What kind of channel this is</h2>")
    o.append(f'<p><strong>{esc(m["kind"])}</strong>, {m["band"]}. That shape determines what a '
             f'buyer can expect to be given and what has to be requested, which is most of '
             f'what changes between one acquisition channel and another.</p>')

    o.append("<h2>What you typically get</h2>")
    o.append(f"<p>{m['you_get']}</p>")

    o.append("<h2>What is typically not there</h2>")
    o.append(f"<p>{m['missing']}</p>")

    o.append("<h2>The churn traps specific to this channel</h2>")
    for i, (name, expl) in enumerate(m["traps"], 1):
        o.append(f"<h3>{i}. {name}</h3><p>{expl}</p>")

    o.append("<h2>A first-pass sequence</h2>")
    o.append("<p>In order, and stopping early if any step produces a blocker:</p>")
    o.append("<ol>" + "".join(f"<li>{s}</li>" for s in m["process"]) + "</ol>")

    o.append("<h2>What to request</h2>")
    o.append("<ul>" + "".join(f"<li>{s}</li>" for s in m["asks"]) + "</ul>")
    o.append(f'<p>Getting a usable export is its own problem, and the request wording that '
             f'works differs by billing platform. The '
             f'<a href="{BASE}/export">export guides</a> cover eighteen platforms with the '
             f'exact wording to send and the status values that mislead on each. Once you have '
             f'the file, the <a href="{BASE}/seller-claims">seller-claims pages</a> give the '
             f'arithmetic for each specific claim, and the '
             f'<a href="{BASE}/saas-due-diligence-checklist">23-point checklist</a> is the '
             f'short version of the whole process.</p>')

    if m["url"]:
        o.append(f'<p>{esc(m["name"])}: <a href="{m["url"]}" rel="nofollow noopener" '
                 f'target="_blank">{m["url"]}</a></p>')
    o.append(DISCLAIMER)

    o.append("<h2>Other acquisition channels</h2>")
    o.append("<ul>" + "".join(
        f'<li><a href="{BASE}{HUB}/{r}">{esc(BY_SLUG[r]["name"])}</a> &mdash; '
        f'{esc(BY_SLUG[r]["kind"]).lower()}</li>'
        for r in m["related"] if r in BY_SLUG) + "</ul>")
    o.append(f'<p><a href="{BASE}{HUB}"><strong>All acquisition channels &rarr;</strong></a></p>')

    return "\n".join(o)


def main() -> None:
    for m in MARKETS:
        page = render(
            url_path=f"{HUB}/{m['slug']}",
            title=m["title"],
            description=m["description"],
            h1=m["h1"],
            lead=m["lead"],
            body=build_body(m),
            faqs=m["faqs"],
            hub_name=HUB_NAME,
            hub_path=HUB,
            breadcrumb_name=m["name"],
        )
        write(f"marketplaces/{m['slug']}", page)

    rows = [[f'<a href="{BASE}{HUB}/{m["slug"]}">{esc(m["name"])}</a>',
             esc(m["kind"]), m["traps"][0][0]] for m in MARKETS]
    hub_body = "\n".join([
        '<p><strong>TL;DR:</strong> Twelve acquisition channels, what each typically discloses '
        'about a SaaS target, and the churn trap specific to each. The pattern across all of '
        'them: listings present amounts, and none of them present the renewal calendar.</p>',
        "<h2>The thing every channel leaves out</h2>",
        "<p>Across open marketplaces, curated marketplaces, brokered processes and direct "
        "deals, one artifact is almost never provided: <strong>the renewal calendar</strong>. "
        "Listings and information packages present amounts, because amounts are what "
        "financial presentation is for. A renewal calendar is a schedule &mdash; which month "
        "each annual contract comes up, and therefore how much of your revenue is decided in "
        "a single month. It takes about ten minutes to build from a subscription export and "
        "it shapes your entire first year of ownership.</p>",
        "<p>The second near-universal gap is <strong>concentration measured on parent "
        "entities</strong> rather than on billing accounts. Six accounts at 4% each that "
        "share a corporate domain are a 22% exposure behind one procurement decision, and no "
        "billing system groups rows that way because billing systems do not know about "
        "parent companies.</p>",
        "<h2>By channel</h2>",
        table(["Channel", "Type", "The trap specific to it"], rows),
        "<h2>How the channel changes the work</h2>",
        "<p>The analysis a buyer runs barely changes between channels. What changes is how "
        "much of it has already been done and how the request has to be made.</p>",
        "<ul>"
        "<li><strong>Open marketplaces.</strong> Nothing is verified, so everything is yours. "
        "The advantage is that no definitional choices have been made for you.</li>"
        "<li><strong>Curated marketplaces.</strong> Figures typically reconcile to source, "
        "which is real work. Verification is not analysis, so recompute retention under your "
        "own definition anyway and spend your effort on what curation does not cover.</li>"
        "<li><strong>Brokered processes.</strong> Well-prepared and sell-side. Request "
        "subscription-level rows in the first written round, because late requests read as "
        "retrades inside a managed timeline.</li>"
        "<li><strong>Micro and side-project marketplaces.</strong> Sample sizes are too small "
        "for monthly rates to mean anything. Work in absolute numbers, review every account "
        "individually, and focus on what actually transfers.</li>"
        "<li><strong>Direct and off-market.</strong> No structure at all, which means you "
        "define it. Expect to help the owner produce the export, and share your analysis with "
        "them.</li>"
        "</ul>",
        f'<p>Related: <a href="{BASE}/export">getting a usable export from any billing '
        f'platform</a>, <a href="{BASE}/seller-claims">what sellers say and how to verify '
        f'it</a>, <a href="{BASE}/saas-due-diligence-checklist">the 23-point checklist</a>, '
        f'and <a href="{BASE}/how-to-evaluate-a-saas-before-buying">how to evaluate a SaaS '
        f'before buying</a>.</p>',
        DISCLAIMER,
    ])
    hub = render(
        url_path=HUB,
        title="SaaS Due Diligence by Marketplace: 12 Acquisition Channels | ChurnLens",
        description="What Flippa, Acquire.com, Empire Flippers, FE International and eight other acquisition channels do and do not tell you about a SaaS target's churn — and the verification each one needs.",
        h1="SaaS churn due diligence, by acquisition channel",
        lead="Twelve places SaaS businesses change hands, what each typically discloses, and the churn trap specific to each. One artifact is missing from all of them: the renewal calendar.",
        body=hub_body,
        faqs=[
            ("Which SaaS marketplace is best for buyers?",
             "It depends on deal size and how much diligence capacity you have. Open marketplaces offer the widest choice and the least verification; curated marketplaces and brokers do more preparation and run competitive processes; direct approaches usually mean better prices and no structure at all. The analysis you need to run is much the same across all of them."),
            ("Do marketplaces verify a SaaS target's churn rate?",
             "Some verify that reported figures reconcile to source systems, which is genuine work. None of them, as a rule, decide whether churn was defined the way a buyer would define it — whether free accounts sat in the denominator, whether the rate counts customers or dollars, how annual plans were handled. Verification and analysis are different things."),
            ("What is the single most overlooked item in SaaS acquisition diligence?",
             "The renewal calendar. It shows which month each annual contract comes up and therefore how much revenue is decided in a single month, and it is almost never included in any listing or information package because it is a schedule rather than a metric. It takes about ten minutes to build from a subscription export."),
        ],
        hub_name="Home",
        hub_path="/",
        breadcrumb_name="By Marketplace",
    )
    write("marketplaces", hub)
    print(f"marketplaces: wrote {len(MARKETS)} pages + hub")


if __name__ == "__main__":
    main()
