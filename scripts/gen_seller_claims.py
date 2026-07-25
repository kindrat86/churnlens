#!/usr/bin/env python3
"""/seller-claims/<slug> — the twelve things a SaaS seller says, and how a buyer tests each.

Every threshold on these pages is presented as ChurnLens's own working threshold,
not as an industry statistic. The only external figures used anywhere are the two
already carried sitewide with attribution (SaaS Capital 2023 revenue churn median,
Benchmarkit/Pavilion FY2024 gross revenue retention median). Worked examples are
labelled as illustrative. Nothing here asserts a fact about a named third party.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pseo_shell import BASE, CTA, esc, render, table, write  # noqa: E402

HUB = "/seller-claims"
HUB_NAME = "Seller Claims"

# ---------------------------------------------------------------------------

CLAIMS = [
{
"slug": "2-percent-monthly-churn",
"claim": "Churn is about 2% a month.",
"title": "Seller Says Churn Is 2% a Month — How to Verify It | ChurnLens",
"description": "A 2% monthly churn claim is the most common number in a SaaS sale and the easiest to compute three different ways. Here is how to reproduce it from the raw subscription export, and the four definitional choices that turn 9% into 2%.",
"h1": "The seller says: &ldquo;churn is about 2% a month&rdquo;",
"lead": "This is the single most quoted number in a small SaaS sale, and it is almost never wrong on purpose. It is wrong because &ldquo;2%&rdquo; is the answer to a question nobody agreed on. Change four definitional choices and the same subscription table yields anything from 1.8% to 9.4%.",
"why": "Nearly every operator computes churn from whatever their billing dashboard displays by default, and every dashboard makes a different set of assumptions. A seller quoting 2% is usually quoting a figure they have genuinely seen on a screen for years. The number is real; the definition behind it is undisclosed. Your job is not to catch a liar, it is to recompute the same quantity under your own definition and see how far it moves.",
"hides": [
("Logo churn quoted as revenue churn",
 "If the departing accounts are systematically larger than the surviving ones, counting customers instead of dollars understates the damage. A business losing 2% of its logos can be losing 6% of its MRR in the same month. Ask which one the number is, and if the answer is &ldquo;both are about the same&rdquo;, that itself is a testable claim."),
("A denominator that includes free or trialling accounts",
 "Dividing cancellations by all accounts rather than by paying accounts at the start of the period dilutes the rate directly. A base padded with free-tier rows is the most common single source of a flattering churn figure."),
("Annual subscriptions counted as never churning",
 "An annual plan cannot cancel in eleven of twelve months. If annual customers sit in the denominator every month but can only leave in their renewal month, the monthly average is mechanically suppressed. This is why annual-heavy books look calm right up to the renewal cliff."),
("Reactivations netted off silently",
 "Some dashboards subtract returning customers from the cancellation count in the same period. That is a legitimate way to report net movement, but it is not gross churn, and it hides how leaky the base actually is."),
],
"verify": [
"Restrict to <em>paying</em> subscriptions only. Filter out anything with a zero amount, a trial status, or a 100% discount coupon. This alone frequently moves the answer by a point or more.",
"Pick one calendar month with complete data on both ends — not the most recent one, which is usually partial.",
"Count the paying subscriptions active on the first day of that month. That is your denominator, <em>D</em>.",
"Count the subscriptions with a cancellation date inside that month that were in <em>D</em>. That is <em>C</em>. Do not subtract anyone who signed up and left inside the same month; count them separately, because a high same-month figure means the acquisition is buying churn.",
"Gross logo churn is <em>C / D</em>. Now do it again in dollars: sum the normalised monthly amount of the rows in <em>C</em>, divide by the summed monthly amount of <em>D</em>. That is gross revenue churn.",
"Normalise annual plans to a monthly amount (annual price divided by twelve) before you sum anything, or your dollar figure will swing wildly with renewal timing.",
"Repeat for twelve consecutive months and look at the series, not the mean. One month is an anecdote; the shape of twelve is the finding.",
],
"thresholds": [
["Revenue churn recomputes within 1 point of the claim", "Green", "The seller understands their own book. Move on to concentration and annual-plan decay."],
["Recomputes 1&ndash;3 points higher", "Investigate", "Usually a denominator or definitional difference. Ask them to walk you through their formula; the gap normally explains itself in one call."],
["Recomputes more than 3 points higher", "Price it in", "The number the business was marketed on is not the number the business produces. This is a valuation conversation, not a diligence footnote."],
["Logo and revenue churn diverge by more than 2&times;", "Investigate", "Departing accounts are much larger or much smaller than average. Either way, the mix matters more than the rate."],
["You cannot reproduce it at all", "Red", "Either the export is incomplete or the figure came from somewhere other than the billing data. Both are reasons to slow down."],
],
"dataroom": [
"The raw subscription-level export, one row per subscription, including cancelled ones. Aggregates are not a substitute.",
"A written statement of the formula behind the quoted figure: numerator, denominator, treatment of annual plans, treatment of reactivations.",
"The same export as of a date at least six months earlier, so you can check whether history has been restated.",
"A list of any accounts that are internal, comped, or otherwise not arm's-length paying customers.",
],
"worked": "Illustrative, to show the mechanism rather than to describe any real target. Take 1,000 rows, of which 250 are free-tier and 300 are annual. The dashboard divides 20 monthly cancellations by all 1,000 rows and reports 2.0%. Restrict to paying accounts and the denominator falls to 750, giving 2.7%. Exclude the 300 annual plans that cannot cancel this month and it is 4.4% on the monthly book. Weight by dollars, where the departing accounts happen to be above average size, and the revenue figure lands higher again. No step in that chain is dishonest. The 2.0% and the higher figure are both arithmetically correct answers to different questions, and only one of them describes what happens to your revenue after close.",
"consequence": "Churn feeds valuation through the multiple, not through the headline revenue, which is why a two-point error compounds. If you are pricing off a multiple that assumed the reported retention, and retention is materially worse, the correct response is either a lower multiple or an earn-out that pays on retained revenue rather than on revenue at close. Do the recomputation before the LOI, because after the LOI you are renegotiating rather than negotiating.",
"faqs": [
("Is 2% monthly churn good for a SaaS business?",
 "It is a strong figure if it is gross revenue churn on a paying, monthly-normalised base — that is roughly 22% annualised. The problem is that most quoted 2% figures are logo churn on a padded denominator, which is a materially different and much weaker claim. Establish which quantity you are being given before you judge it."),
("What is the difference between the seller's churn number and mine?",
 "Almost always one of four things: whether free and trialling accounts sit in the denominator, whether the figure counts customers or dollars, whether annual plans are treated as unable to churn in non-renewal months, and whether reactivations are netted off. Each is worth between half a point and several points on its own."),
("Can I check a 2% churn claim without the raw export?",
 "Not reliably. You can sanity-check it against reported MRR movement — if MRR is flat while the seller claims 2% churn and strong new sales, the numbers have to reconcile somewhere — but a monthly summary cannot tell you whether the denominator was padded. Ask for subscription-level rows; a seller who will not provide them has told you something."),
],
"tool": ("/free/churn-calculator", "free churn calculator"),
"related": ["net-negative-churn", "logo-churn-is-low", "no-one-has-churned-recently", "mrr-has-grown-every-month"],
},
{
"slug": "net-negative-churn",
"claim": "We have net negative churn.",
"title": "Seller Says They Have Net Negative Churn — How to Verify It | ChurnLens",
"description": "Net negative churn is a real and valuable property, and also the claim most easily manufactured by a single expanding account or a mid-period price rise. Here is how to decompose it from the raw export.",
"h1": "The seller says: &ldquo;we have net negative churn&rdquo;",
"lead": "Net negative churn means expansion from existing customers exceeds everything lost from them. When it is broad-based it is the most valuable property a subscription business can have. When it comes from one account, or from a price increase, it is a temporary accounting outcome wearing the costume of a structural advantage.",
"why": "Net revenue retention above 100% is the headline metric of modern SaaS benchmarking, so sellers are right to lead with it when they have it. The claim is also unusually forgiving: because expansion and contraction are netted, a single large upgrade can carry an otherwise leaky book above the line for several months. Sellers rarely decompose the figure because their dashboard does not, not because they are hiding the composition.",
"hides": [
("One account doing all the work",
 "Compute the contribution of the single largest expanding account to total expansion. If removing it drops net retention below 100%, the business does not have net negative churn; one customer does, and that customer is now also your concentration risk."),
("A price increase counted as expansion",
 "A sitewide price rise shows up in the data as every account expanding at once. It is genuine revenue, but it is non-repeatable and it usually raises churn over the following two or three renewal cycles. Expansion that all lands in the same month is a pricing event, not a land-and-expand motion."),
("Seat growth that tracks the customer's headcount, not your product",
 "If expansion is seats-per-account rising in step with the customers' own hiring, you have bought exposure to their growth rate. That is fine if you understand it, and dangerous if you have modelled it as a product-led expansion engine."),
("Gross churn hidden behind the netting",
 "Net retention can be above 100% while gross revenue retention is poor. The netted figure tells you about this year's revenue; gross retention tells you how leaky the base is, and therefore how much expansion you must keep manufacturing forever."),
],
"verify": [
"Pick two dates twelve months apart. Take the cohort of accounts paying on the earlier date, and ignore everyone acquired after it. Net revenue retention is only meaningful on a fixed cohort.",
"Sum that cohort's normalised monthly revenue on the earlier date. Call it <em>S</em>.",
"Sum the same accounts' revenue on the later date, counting departed accounts as zero. Call it <em>E</em>. Net revenue retention is <em>E / S</em>.",
"Decompose the movement into four buckets: expansion (accounts that grew), contraction (accounts that shrank but stayed), churn (accounts that went to zero), and unchanged. The four must sum back to <em>E &minus; S</em>.",
"Compute gross revenue retention on the same cohort: <em>(S &minus; churn &minus; contraction) / S</em>, with expansion excluded entirely. Both numbers, always, side by side.",
"Rank the expansion bucket by size and ask what happens to net retention with the top account removed, then the top three.",
"Plot expansion by month. Broad-based expansion is spread across the year; a pricing event is a spike in one month affecting most accounts by a similar percentage.",
],
"thresholds": [
["Net retention above 100% and gross above 90%", "Green", "Genuine expansion on a base that also holds. This is the case worth paying for."],
["Net above 100%, gross below 85%", "Investigate", "Expansion is masking a leaky base. Model what happens when expansion normalises, because gross retention is the floor."],
["Removing the top expanding account drops net below 100%", "Price it in", "The claim belongs to one customer. Re-read it as a concentration finding and check that account's contract term and renewal date."],
["Expansion concentrated in a single month", "Investigate", "Likely a price increase. Ask for the pricing-change history and look at churn in the two renewal cycles that followed."],
["Cohort cannot be reconstructed from the export", "Red", "Net retention cannot be verified without account-level history. Treat the claim as unevidenced until it can be."],
],
"dataroom": [
"Account-level revenue at two dates twelve months apart, on a consistent account identifier.",
"The complete pricing-change history, including grandfathering rules and any account-specific discounts.",
"A breakdown of expansion by mechanism: seats, tier upgrades, usage, price increases.",
"Contract terms and renewal dates for the ten largest accounts.",
],
"worked": "Illustrative. A book of 200 accounts at $100,000 monthly. Over twelve months it loses $9,000 to churn and $3,000 to contraction, and gains $14,000 of expansion. Net retention is 102%, and the seller's claim is true. But $11,000 of the $14,000 came from one account tripling its seat count. Remove it and net retention is 91%. Gross retention was 88% the whole time — coincidentally in line with the Benchmarkit/Pavilion FY2024 median of 88%, which is the figure worth anchoring on, because gross retention is what the business does without heroics. You are not buying a net-negative-churn business. You are buying an 88% gross retention business with one very good customer, and the two are priced differently.",
"consequence": "Net revenue retention drives the multiple more than almost any other operating metric, so a claim that rests on one account or one price rise is the most expensive kind of misunderstanding available in a SaaS deal. The structural fix is to underwrite on gross retention and treat expansion as upside rather than as the base case. If the seller believes the expansion motion is real and repeatable, that belief is exactly what an earn-out is for.",
"faqs": [
("What is the difference between net and gross revenue retention?",
 "Gross revenue retention counts only losses — churn and contraction — and is capped at 100%. Net revenue retention adds expansion back in and can exceed 100%. Gross retention tells you how well the base holds; net retention tells you what happened to revenue overall. A buyer needs both, because gross retention is the floor if expansion stops."),
("Is net negative churn always a good sign?",
 "It is a genuinely strong property when it is broad-based. It is misleading when it comes from one expanding account, from a one-off price increase, or from usage growth that tracks the customers' own headcount rather than anything the product does. In each of those cases the mechanism does not repeat, so it should not be underwritten as if it does."),
("How do I check net negative churn from a subscription CSV?",
 "Fix a cohort of accounts paying on a date twelve months back, sum their revenue then and now with departures counted as zero, and divide. Then decompose the change into expansion, contraction and churn, and recompute with the largest expanding account removed. If the second number is below 100%, the claim is about one customer."),
],
"tool": ("/free/nrr-calculator", "free NRR calculator"),
"related": ["2-percent-monthly-churn", "no-customer-concentration", "revenue-is-fully-recurring", "ltv-is-3000"],
},
{
"slug": "no-customer-concentration",
"claim": "No single customer is more than 5% of revenue.",
"title": "Seller Says There Is No Customer Concentration — How to Verify It | ChurnLens",
"description": "The 5% concentration claim is usually true at the account level and false at the level that matters. Here is how to test it across parent entities, cohorts, contract dates and payment methods.",
"h1": "The seller says: &ldquo;no single customer is more than 5% of revenue&rdquo;",
"lead": "This claim is normally accurate as stated and still misses the risk. Concentration is not only about one large logo. It is about correlated exposure: accounts that share a parent company, a renewal date, an industry, a referral source or a single champion, and that therefore leave together.",
"why": "Sellers test concentration the way an accountant would, by sorting accounts by revenue and looking at the top row. That check catches the obvious case and nothing else. The failure mode a buyer cares about is a group of nominally independent accounts that turn out to be one decision, and no billing dashboard groups rows that way because billing systems do not know about parent companies or shared champions.",
"hides": [
("Subsidiaries billed separately",
 "Six accounts at 4% each that all roll up to the same parent company are a 24% exposure with one decision-maker. Billing sees six customers. Group by email domain first, then by company name similarity, then ask the seller directly."),
("A shared renewal date",
 "If a third of revenue renews in the same month, that month is a single event regardless of how many logos are involved. Concentration in time is concentration."),
("One acquisition channel",
 "Accounts that all arrived from one integration listing, one affiliate or one conference are correlated in a way the revenue table cannot show. If that channel closes, the whole group stops replenishing at once."),
("A single internal champion across accounts",
 "In agency, consultancy and franchise books it is common for one person to have specified the product for many nominally separate customers. That relationship is not on the balance sheet and does not transfer with the asset."),
],
"verify": [
"Compute the straightforward version first: each account's share of normalised monthly revenue, sorted descending. Note the top 1, top 5 and top 10 shares.",
"Group by email domain and recompute. Then normalise obvious company-name variants and recompute again. The number usually moves.",
"Compute the Herfindahl-style sum of squared revenue shares across the whole book. It is a single figure that responds to the shape of the distribution rather than to the top row alone, which makes it comparable across targets.",
"Group revenue by renewal month and find the largest month's share. Anything above 20% is a scheduling risk you need to know about before you plan the transition.",
"Group by industry or customer type if the export carries it. If not, ask; a book that is 60% one vertical is exposed to that vertical's budget cycle.",
"For the top ten accounts, check tenure, contract term, notice period and whether payment is by card or invoice. Long-tenure invoiced accounts on annual terms behave very differently from month-to-month card accounts.",
"Ask explicitly: which of the top twenty accounts share a parent, a group buying decision, or a single point of contact.",
],
"thresholds": [
["Top account under 5% and top ten under 25%", "Green", "Genuinely diversified. Check renewal-month clustering and move on."],
["Top account 5&ndash;10%", "Investigate", "Normal for a small SaaS. Confirm the contract term and get comfortable with the relationship transferring."],
["Top account above 15%, or top ten above 50%", "Price it in", "One conversation can reset the economics of the deal. This belongs in the structure, not just the memo."],
["Domain grouping moves the top share by more than 5 points", "Investigate", "The seller's concentration answer was measured on the wrong unit. Redo the whole analysis on parent entities."],
["More than 25% of revenue renews in one month", "Investigate", "Time concentration. Make sure that month is not also the month you plan to migrate billing or change pricing."],
],
"dataroom": [
"Account-level revenue with email domain and company name, not just an opaque customer ID.",
"A parent-company mapping for the top twenty accounts, produced by the seller in writing.",
"Contract term, renewal date and notice period for every account above 2% of revenue.",
"The acquisition source for the top twenty accounts, if it is tracked at all.",
],
"worked": "Illustrative. A $60,000 monthly book where the largest account is $2,700, or 4.5%, so the claim holds. Grouping by email domain reveals that five accounts totalling $13,000 share one corporate domain: 22% of revenue behind a single procurement decision. Separately, 31% of revenue renews in January because an early partnership pushed a cohort in together. Neither fact is visible in the sorted revenue table, both are visible in ten minutes of grouping, and both change how you would structure the purchase.",
"consequence": "Concentration is the risk most often discovered after close, because it is invisible in exactly the report sellers use to check for it. It matters most in the first two quarters of ownership, when the relationships are least transferred and any change you make to pricing, packaging or support is most likely to trigger a review. If concentration is real, the mitigations are structural: hold-backs tied to named accounts, direct conversations with the top customers before close, and a transition plan that leaves the largest renewal month alone.",
"faqs": [
("What counts as too much customer concentration in a SaaS acquisition?",
 "As a working rule we treat a single account above 10% of revenue, or a top-ten above 50%, as something that has to be reflected in deal structure rather than noted in the memo. Those are our thresholds, not an industry standard, and the right line depends on contract length, tenure and how transferable the relationship is."),
("How do I find hidden customer concentration in a subscription export?",
 "Group before you sort. Group by email domain, then by normalised company name, then by renewal month, and recompute the top shares after each grouping. Concentration that is invisible per-account is usually obvious per-parent, and a Herfindahl-style sum of squared shares gives you one comparable number for the whole distribution."),
("Why does concentration matter more for a buyer than for the current owner?",
 "Because the relationship has not transferred yet. The current owner has years of goodwill with those accounts; on day one you have none, and any change you make is the natural trigger for a re-evaluation. Concentration risk is highest precisely in the period right after the money moves."),
],
"tool": ("/free/revenue-concentration-analyzer", "free revenue concentration analyzer"),
"related": ["net-negative-churn", "all-customers-are-on-annual-contracts", "the-churn-spike-was-seasonal", "logo-churn-is-low"],
},
{
"slug": "all-customers-are-on-annual-contracts",
"claim": "Most customers are on annual contracts.",
"title": "Seller Says Customers Are on Annual Contracts — How to Verify It | ChurnLens",
"description": "Annual contracts genuinely improve retention and also defer churn out of the reporting window. Here is how to build the renewal cliff from the raw export before you own it.",
"h1": "The seller says: &ldquo;most customers are on annual contracts&rdquo;",
"lead": "Annual contracts are a real quality signal. They also mean that eleven months out of twelve, an annual customer mathematically cannot churn, which makes monthly churn look calm and pushes every actual decision into a renewal month you may not have looked at. The question is never whether the contracts are annual. It is when they renew and what happened the last time they did.",
"why": "Sellers lead with contract length because it is a legitimate strength and because it is one of the few retention facts that is unambiguous. What they rarely produce is the renewal calendar, partly because billing dashboards present churn as a monthly rate rather than as a schedule of events, and partly because a business with a young annual book has genuinely never seen a full renewal cycle and so has nothing to report.",
"hides": [
("Renewals that have not happened yet",
 "A book converted to annual terms eighteen months ago has been through at most one renewal cycle, and the cohort that converted most recently has been through none. Reported retention describes a period in which leaving was not an available option."),
("A renewal cliff concentrated in one or two months",
 "Annual plans sold during a launch or a promotion all come up for renewal together. Build the calendar: revenue at risk by month for the next twelve months. If any month exceeds 15% of revenue, that is the single most important date in your ownership plan."),
("Auto-renewal without an active decision",
 "Auto-renewing card payments produce renewals that were never affirmatively chosen. Those accounts can look loyal for years and then leave the moment anything prompts a review — a price change, a card expiry, a new owner's email."),
("Deferred revenue that is someone else's cash",
 "Cash collected up front for service not yet delivered is a liability you inherit. If a meaningful share of annual revenue was collected before close, you are obliged to deliver it without receiving it, and that needs to be in the working-capital adjustment."),
],
"verify": [
"Split the book by billing interval and compute each interval's share of normalised monthly revenue. Establish what &ldquo;most&rdquo; actually means: 55% and 90% are different businesses.",
"For every annual subscription, compute the next renewal date from its start date and term. Build a twelve-month calendar of revenue at risk by month.",
"Find the largest single renewal month's share of total revenue. That is your cliff.",
"Identify annual cohorts that have never renewed — subscriptions whose start date is less than one term ago. Their contribution to reported retention is structurally zero risk so far.",
"For cohorts that <em>have</em> renewed, compute the actual renewal rate: of the annual subscriptions that reached a renewal date, what share continued. This is the only number in the whole exercise that is evidence rather than inference.",
"Check how much annual cash was collected in the ninety days before the transaction date, and confirm it is treated as deferred revenue in the working-capital calculation.",
"Compare annual and monthly cohorts on the same footing by annualising both. If annual retention is not clearly better, the contracts are deferring churn rather than reducing it.",
],
"thresholds": [
["Annual cohorts have completed at least one full renewal cycle at above 85%", "Green", "Evidence, not inference. The contract-length claim is doing real work."],
["Largest renewal month is 15&ndash;25% of revenue", "Investigate", "Manageable, but plan the transition around it and do not touch pricing that quarter."],
["Largest renewal month above 25% of revenue", "Price it in", "A single month decides a quarter of your revenue. Talk to those accounts before close, not after."],
["Most annual subscriptions have never reached a renewal", "Investigate", "Reported retention describes a period when churn was not possible. Underwrite on the monthly cohort instead."],
["Observed annual renewal rate below 80%", "Price it in", "Annual terms are deferring churn into a cliff rather than preventing it. Model the cliff explicitly."],
],
"dataroom": [
"Billing interval, term length, start date and next renewal date for every subscription.",
"Renewal outcomes for every annual subscription that has reached a renewal date, including the ones that did not continue.",
"The deferred revenue balance as of the most recent close, reconciled to the subscription table.",
"Any auto-renewal terms, notice periods, and the cancellation mechanics customers actually face.",
],
"worked": "Illustrative. 70% of revenue is annual and reported monthly churn is 1.4%, which looks excellent. Building the renewal calendar shows 28% of total revenue renewing in March, because a Product Hunt launch two years ago converted a cohort together. Of the annual subscriptions that have reached a renewal date, 79% continued. Annualised, the annual book is therefore losing roughly a fifth of its revenue per cycle, concentrated in one month, while the monthly reported rate says 1.4%. Both figures come from the same file. Only one of them tells you what March looks like.",
"consequence": "The renewal calendar is the most useful single artifact you can build from a subscription export, and it is almost never in the data room because it is not a metric, it is a schedule. It determines when you can safely change pricing, when you should not migrate billing, and how much cash you need in reserve. If a cliff month is large, the mitigations are direct customer conversations before close and a hold-back that releases after the cliff has passed.",
"faqs": [
("Do annual contracts really reduce SaaS churn?",
 "They reduce churn opportunities, and often genuinely reduce churn as well, because the customer has made a larger commitment. But they also defer every decision to a renewal date, so a book that has not been through a full renewal cycle has no evidence either way. Judge annual retention only on cohorts that have actually reached a renewal."),
("What is a renewal cliff?",
 "A month in which an outsized share of annual revenue comes up for renewal at once, usually because those contracts were sold together during a launch or promotion. If a single month carries more than about 15% of revenue, it dominates your first year of ownership and should shape both the transition plan and the deal structure."),
("How do I find the renewal cliff in a subscription CSV?",
 "For each annual subscription, add the term length to the start date to get the next renewal date, then group normalised monthly revenue by that month across the coming twelve months. The output is a bar per month, and the tallest bar is the cliff. It takes about ten minutes and it is rarely in the data room."),
],
"tool": ("/annual-plan-churn-risk", "annual-plan churn risk analysis"),
"related": ["no-customer-concentration", "2-percent-monthly-churn", "no-one-has-churned-recently", "revenue-is-fully-recurring"],
},
{
"slug": "mrr-has-grown-every-month",
"claim": "MRR has grown every month for two years.",
"title": "Seller Says MRR Has Grown Every Month — How to Verify It | ChurnLens",
"description": "Monotonic MRR growth is compatible with deteriorating retention, because new sales can mask any churn rate. Here is how to decompose the growth into its four components.",
"h1": "The seller says: &ldquo;MRR has grown every month for two years&rdquo;",
"lead": "A rising MRR line is the most persuasive chart in any deal, and it is also the most compatible with bad news. Net growth is the sum of four movements, and new-customer revenue can cover an arbitrarily high churn rate for as long as acquisition holds. What you are buying is the retained base; what the chart shows is the base plus the sales engine.",
"why": "Sellers show the net line because it is the line they run the business on, and because it is genuinely the right summary for an operator. For a buyer it is the wrong altitude: you are acquiring the installed base and inheriting a sales motion whose future you cannot observe. The decomposition is not something sellers withhold, it is something most billing dashboards simply do not display.",
"hides": [
("Rising churn masked by rising acquisition",
 "If new revenue grows faster than churned revenue, the net line rises while retention deteriorates. Plot churned MRR as a percentage of opening MRR by month. A rising series inside a rising net line is the finding."),
("Growth that is entirely price, not volume",
 "Separate rate from quantity. Revenue per account rising while account count is flat means the growth came from pricing, which is finite and usually followed by elevated churn at the next renewals."),
("A single channel doing all the acquisition",
 "If most new revenue arrives from one channel, the growth line is a bet on that channel persisting under new ownership. Directory rankings, integration marketplace placement and a founder's personal audience are all channels that do not transfer cleanly."),
("Late-stage flattening inside the trailing average",
 "Twenty-four months of growth can contain six months of stagnation and still be described accurately as growth. Look at the last two quarters on their own, and at month-over-month growth rate rather than level."),
],
"verify": [
"Rebuild MRR from the subscription rows for each of the last twenty-four months rather than trusting a reported series. Normalise annual plans to monthly. If your rebuild does not track the seller's chart, resolve that before anything else.",
"Decompose each month into four buckets: new, expansion, contraction, churn. New plus expansion minus contraction minus churn must equal the change in MRR.",
"Plot churned MRR as a percentage of opening MRR by month. This is the series that matters, and it is independent of how good the sales team is.",
"Plot new MRR as a percentage of opening MRR. If it is falling while churn is flat, the growth line is about to turn regardless of retention.",
"Split account count from revenue per account. Growth in the second with none in the first is a pricing story.",
"Compute the quick ratio — new plus expansion divided by churn plus contraction — by month. It tells you how many dollars of growth are being manufactured per dollar lost.",
"Look at the last two quarters in isolation, and at the trailing three-month growth rate rather than the two-year shape.",
],
"thresholds": [
["Churn as a share of opening MRR is flat or falling across 24 months", "Green", "The growth is coming from a base that also holds. This is the case the chart implies."],
["Churn share rising while net MRR rises", "Price it in", "Acquisition is outrunning a worsening leak. Model what the line does if new sales fall 30% post-transition."],
["Account count flat, revenue per account rising", "Investigate", "Growth is pricing. Ask for the pricing-change history and check churn in the following two renewal cycles."],
["Quick ratio below 2 in recent months", "Investigate", "Each dollar of growth is costing close to a dollar of loss. Efficiency is deteriorating even if the level is rising."],
["More than 60% of new revenue from one channel", "Investigate", "The growth line is a bet on that channel surviving the ownership change. Establish whether it transfers."],
],
"dataroom": [
"Subscription-level rows sufficient to rebuild the MRR series independently, including cancelled subscriptions.",
"Monthly new, expansion, contraction and churn in dollars for the last twenty-four months.",
"Acquisition source per new customer, or the best available proxy, for the last twelve months.",
"The complete pricing-change history and any grandfathering rules.",
],
"worked": "Illustrative. MRR rises from $40,000 to $70,000 over twenty-four months with no down month, which the chart shows clearly. Decomposed, churned MRR grows from 2.1% to 5.8% of opening MRR over the same period, while new MRR grows from 4.0% to 8.2%. The net line is monotonic because the sales engine accelerated faster than the leak widened. Underwrite the sales engine at its current rate and the model works; assume it falls by a third during the ownership transition, which is a common outcome when a founder-led channel changes hands, and MRR declines from month two. The chart was accurate and it was the wrong chart.",
"consequence": "This is the most consequential decomposition in buyer-side diligence, because a monotonic MRR line does more to justify a multiple than any other artifact and it constrains retention not at all. Underwrite the retained base and treat the sales engine as a separate asset with its own transfer risk. If the growth depends on a founder's audience or one channel placement, that dependency belongs in the structure — an earn-out, a transition services agreement, or a lower multiple.",
"faqs": [
("Can MRR grow every month while churn gets worse?",
 "Yes, and it is common. Net MRR change is new plus expansion minus contraction minus churn. As long as new revenue grows faster than churned revenue, the net line rises no matter what retention does. That is why the decomposition matters more than the level."),
("What is the SaaS quick ratio and why should a buyer care?",
 "It is new plus expansion revenue divided by churn plus contraction revenue. It measures how many dollars of growth the business manufactures per dollar it loses. A high level with a falling quick ratio means the business is working harder every month to keep the line rising, which is exactly the trend a new owner inherits."),
("How do I rebuild an MRR series from a subscription export?",
 "For each month, sum the normalised monthly amount of every subscription active in that month, treating annual plans as their annual price divided by twelve. Do it for twenty-four months and compare your series to the seller's chart. A gap between the two is itself a finding worth resolving before you look at anything else."),
],
"tool": ("/mrr-trajectory-forensics", "MRR trajectory forensics"),
"related": ["2-percent-monthly-churn", "net-negative-churn", "the-churn-spike-was-seasonal", "revenue-is-fully-recurring"],
},
{
"slug": "the-churn-spike-was-seasonal",
"claim": "That churn spike was seasonal.",
"title": "Seller Says the Churn Spike Was Seasonal — How to Verify It | ChurnLens",
"description": "Seasonality is a testable claim: it requires the same spike in the same month across multiple years. Here is how to test it, and what the four alternative explanations look like in the data.",
"h1": "The seller says: &ldquo;that churn spike was seasonal&rdquo;",
"lead": "Seasonality is one of the few diligence claims that is fully falsifiable from data you already have. A seasonal pattern repeats in the same month across years. If the spike appears once, it is an event, and the only question is which event.",
"why": "When a chart shows an ugly month, seasonality is the most available explanation and it is often offered in complete good faith — small businesses do have quiet quarters, and a founder who has lived through two Januaries can reasonably believe January is just like that. The problem is that a single observation cannot distinguish a season from a price increase, a churned cohort, an outage or a competitor launch, and the four have very different implications for a buyer.",
"hides": [
("A price increase two renewal cycles earlier",
 "Price rises show up as elevated churn at the next renewal, not immediately. Line the churn series up against the pricing-change history with a two-to-three cycle lag before accepting any other explanation."),
("A single cohort reaching the end of its natural life",
 "A promotion or launch cohort that all signed up together will all reach their decision point together. That looks exactly like seasonality once, and never again."),
("An outage, a migration or a support collapse",
 "Product and service incidents produce churn with a lag of one to two billing cycles. Ask for the incident history and the support-ticket volume by month, and overlay them."),
("A competitor launch or a platform change",
 "If a marketplace changed its ranking, or an integration partner shipped the same feature natively, churn concentrates among the accounts that arrived through that channel. Segment the spike by acquisition source and it usually resolves immediately."),
],
"verify": [
"Build monthly churn as a percentage of opening MRR for at least twenty-four months, ideally thirty-six. Seasonality needs more than one cycle to be visible at all.",
"Compare the same calendar month across years. A genuine seasonal effect gives you an elevated January in every January, not one bad January.",
"Compute each month's deviation from its own trailing twelve-month average. One month more than two standard deviations out, with no repeat, is an event.",
"Segment the spike itself: by plan, by tenure, by acquisition source, by geography if available. Events concentrate in a segment; seasons do not.",
"Overlay the pricing-change history with a two-to-three renewal-cycle lag.",
"Overlay incidents, migrations and any support disruption.",
"Check what happened in the three months after the spike. A season reverts to trend; an event often leaves the base permanently lower.",
],
"thresholds": [
["The same month is elevated in two or more years", "Green", "Genuine seasonality. Model it and move on; it is a working-capital consideration, not a valuation one."],
["One elevated month, 24+ months of data, no repeat", "Investigate", "This is an event. Identify it before you accept any explanation, because the explanation determines whether it recurs."],
["The spike concentrates in one plan, cohort or channel", "Price it in", "A segment-specific event. Establish whether the cause is still present, because if it is, the rest of that segment is next."],
["The base did not recover to trend within three months", "Price it in", "Permanent impairment, not a season. Rebase your model on the post-spike level."],
["Fewer than 18 months of history available", "Investigate", "Seasonality is untestable with this much data. Treat the claim as unevidenced, not as false."],
],
"dataroom": [
"At least twenty-four and preferably thirty-six months of subscription-level history.",
"The complete pricing-change history with effective dates.",
"An incident, outage and migration log for the same period.",
"Support ticket volume by month, and any change of support staffing or tooling.",
],
"worked": "Illustrative. Churn runs at 3% and spikes to 11% in a single February. Seasonal, says the memo. Three years of history shows February at 3.1% and 2.8% in the other two years, so the season hypothesis dies immediately. Segmenting the spike shows 80% of it in accounts acquired through one integration marketplace, and the marketplace changed its default listing that January. The cause is external, ongoing, and the remaining accounts from that channel are the next cohort at risk. That is a completely different finding from seasonality, and it took two groupings to reach.",
"consequence": "Whether a spike is a season or an event determines whether you model reversion or impairment, which is usually the difference between two valuations. It also determines whether the cause is still operating, which is the part that matters most: an event with a live cause is a forecast, not a historical note. Ask for thirty-six months up front; the most common reason this analysis fails is simply not having enough history to run it.",
"faqs": [
("How can I tell if a SaaS churn spike is seasonal or structural?",
 "Compare the same calendar month across multiple years. Seasonality repeats; a one-off spike does not. With fewer than eighteen months of history the question cannot be answered either way, which is a reason to ask for more data rather than to accept the explanation."),
("What usually causes a one-off churn spike in a small SaaS?",
 "In our experience the four most common causes are a price increase landing two or three renewal cycles earlier, a single sign-up cohort reaching the end of its natural life together, a product or support incident, and an external change such as a marketplace ranking or an integration partner shipping the same feature natively. Segmenting the spike by plan, tenure and acquisition source usually distinguishes them."),
("Why does the lag between a price increase and churn matter?",
 "Because subscribers mostly cannot act on a price change until their next renewal. Churn therefore appears one to three cycles later, which is long enough that the connection is easy to miss and the spike gets attributed to whatever was happening in the month it appeared."),
],
"tool": ("/churn-divergence-detector", "churn divergence detector"),
"related": ["mrr-has-grown-every-month", "we-intentionally-churned-bad-customers", "2-percent-monthly-churn", "logo-churn-is-low"],
},
{
"slug": "we-intentionally-churned-bad-customers",
"claim": "We intentionally churned our bad customers.",
"title": "Seller Says They Intentionally Churned Bad Customers — How to Verify It | ChurnLens",
"description": "Deliberate customer pruning is a real strategy with a distinctive data signature. Here is how to distinguish it from churn that is being reframed after the fact.",
"h1": "The seller says: &ldquo;we intentionally churned our bad customers&rdquo;",
"lead": "Deliberately removing unprofitable customers is a legitimate and sometimes excellent decision. It also leaves a specific, checkable signature in the data. Intentional pruning is selective, bounded in time, and improves the metrics of what remains. Churn reframed as pruning after the fact is none of those things.",
"why": "This claim usually arrives after a buyer points at a bad period, and it is often true. Founders do fire customers, sunset cheap legacy tiers and exit segments that consume all the support capacity. The reason it needs testing is not dishonesty but hindsight: the same founder is being asked to explain a period they lived through, and a decision that was partly reactive at the time is easy to remember as strategy. The data does not have hindsight.",
"hides": [
("Churn that was not selective at all",
 "Real pruning concentrates in an identifiable segment — one plan, one price point, one usage band. If the departures are spread evenly across plans, tenures and sizes, nothing was targeted."),
("A support or product failure that pushed everyone out",
 "The accounts that leave under strain are disproportionately the demanding ones, which makes indiscriminate churn look selective. Check whether the remaining base's engagement also fell in the same period."),
("Revenue quality that did not actually improve",
 "The whole point of pruning is that what remains is better. If revenue per account, gross retention and expansion are unchanged afterwards, the strategy either was not executed or did not work."),
("A pruning event that never ended",
 "Intentional removal is bounded: a decision, an execution window, a return to baseline. If elevated churn continues in the same segment for a year, that is not a decision, it is a condition."),
],
"verify": [
"Establish the window the seller says the pruning happened in, in writing, before you look at the data.",
"Inside that window, segment departures by plan, price point, tenure and usage. Compute what share of churned revenue came from the segment the seller says was targeted.",
"Compare the churn rate inside the targeted segment against the rest of the book in the same window. Pruning gives you a wide gap.",
"Compare the three months before and the three months after the window on the remaining base: gross revenue retention, revenue per account, expansion rate, support load if available.",
"Check that churn returned to baseline after the window. Plot the targeted segment separately from everything else for twelve months on each side.",
"Look for the mechanism. Deliberate removal usually leaves a trace: a sunset notice, a plan discontinued in the price history, a migration deadline, a coupon that stopped being honoured. Ask for it.",
"Check whether the pruned segment still exists. If the cheap legacy tier is still being sold, the decision was not made.",
],
"thresholds": [
["Churn concentrated in one segment, bounded window, retention improved after", "Green", "The claim holds and the strategy worked. Credit it."],
["Concentrated and bounded, but revenue quality unchanged", "Investigate", "The decision was made and did not deliver. Not a red flag, but do not price in a benefit that did not appear."],
["Churn spread evenly across plans and tenures", "Price it in", "Nothing was targeted. Treat the period as ordinary churn and re-read the explanation as hindsight."],
["Elevated churn in the same segment continues past the window", "Price it in", "This is a condition, not a decision. Model it as ongoing."],
["No documentary trace of a sunset, migration or plan discontinuation", "Investigate", "Deliberate removal normally leaves paperwork. Ask for it; absence is not proof, but it shifts the burden."],
],
"dataroom": [
"The window of the pruning decision, stated in writing with dates.",
"Plan, price point and tenure for every subscription that churned in that window.",
"Any sunset notice, migration deadline or discontinuation announcement sent to customers.",
"The pricing and plan history showing the tier being discontinued.",
],
"worked": "Illustrative. Churn runs at 3.5% and hits 9% across one quarter. The seller says they sunset a $9 legacy tier that consumed most of support. The data agrees: 71% of churned revenue in that quarter came from the $9 tier, churn in the rest of the book was 3.6% and unchanged, there is a migration email with a deadline, and the tier is gone from the price list. In the two quarters after, revenue per account rises 22% and gross retention improves by four points. That is a well-evidenced, well-executed decision and it should count in the seller's favour. The same claim against a spike spread evenly across five plans, with no notice and no subsequent improvement, is a different page in the memo.",
"consequence": "This claim is worth testing carefully in both directions, because a confirmed pruning event is genuinely good news that a mechanical churn screen would score as a red flag. Where it fails, the correction is not to distrust the seller but to move the period from the explained column back into the modelled one. What you must not do is accept the explanation and then also model the improved revenue quality that never showed up in the data.",
"faqs": [
("Is it a red flag when a SaaS seller says they fired customers?",
 "Not on its own, and it can be a positive. Deliberately removing unprofitable customers is a real strategy that leaves a checkable signature: churn concentrated in a specific segment, bounded to a defined window, followed by measurable improvement in what remains. Test for that signature rather than for the intent."),
("How can I tell deliberate customer pruning from ordinary churn?",
 "Selectivity, boundedness and consequence. Pruning concentrates in one plan or price band, stops when the decision has been executed, and improves revenue per account and gross retention afterwards. Ordinary churn reframed after the fact is spread across segments, does not stop, and leaves the remaining base's metrics unchanged."),
("What documentation should I ask for?",
 "The sunset or migration notice sent to customers, the plan history showing the tier being discontinued, and the dates of the decision in writing. Deliberate removal is a project and projects leave paperwork. Its absence does not disprove the claim, but it does move the burden of proof."),
],
"tool": ("/revenue-quality-scorecard", "revenue quality scorecard"),
"related": ["the-churn-spike-was-seasonal", "logo-churn-is-low", "2-percent-monthly-churn", "refunds-are-negligible"],
},
{
"slug": "revenue-is-fully-recurring",
"claim": "Revenue is 100% recurring.",
"title": "Seller Says Revenue Is 100% Recurring — How to Verify It | ChurnLens",
"description": "Recurring is not the same as contracted, and neither is the same as repeatable. Here is how to separate genuine subscription revenue from setup fees, usage and one-off work.",
"h1": "The seller says: &ldquo;revenue is 100% recurring&rdquo;",
"lead": "Recurring revenue is what earns a subscription multiple, so it is worth establishing exactly how much of the revenue qualifies. Three things get counted as recurring that are not: billing that merely repeats, revenue that is contracted but consumption-based, and one-off work booked through the same invoice.",
"why": "Most billing systems put every charge on the same ledger, so a setup fee, an implementation project and a monthly subscription all appear as revenue in the same place. A seller reading their own totals will describe the whole thing as recurring because it all arrives through the subscription system. Separating the components requires looking at line items rather than totals, which most operators have never had a reason to do.",
"hides": [
("Setup, onboarding and implementation fees",
 "One-time charges booked at the start of a relationship inflate revenue in the month they land and do not repeat. They should be excluded from MRR entirely and, if material, valued separately at a services multiple."),
("Usage-based revenue described as subscription revenue",
 "Consumption billing is contracted but not committed. It falls when your customers' own volumes fall, which means it carries their cyclicality. Separate committed minimums from overage and treat only the minimum as recurring."),
("Services revenue inside the same invoices",
 "Consulting, migration and custom development are real revenue at a much lower multiple. If they run through the subscription system they get counted in MRR by default."),
("Annual amounts recognised in the collection month",
 "An annual prepayment recognised entirely in the month it was received creates a revenue spike and distorts every month-over-month comparison around it. Normalise to a monthly amount before you compute anything."),
],
"verify": [
"Work from line items, not invoice totals. Ask for the charge-level export if the subscription export only carries totals.",
"Classify every charge into committed recurring, usage or overage, one-time fee, and services. Anything you cannot classify goes in a fifth bucket and gets asked about.",
"Compute each bucket's share of trailing twelve-month revenue. This is the number the multiple should be applied to, bucket by bucket.",
"Normalise annual and multi-year amounts to monthly before summing anything.",
"For usage revenue, separate the committed minimum from the overage and check overage volatility across twenty-four months. Volatile overage is your customers' business cycle, not yours.",
"Check whether one-time fees are growing as a share of revenue. A rising share means growth is increasingly front-loaded and increasingly dependent on new sales.",
"Recompute MRR with only committed recurring revenue, and compare it to the seller's figure. The gap is the finding.",
],
"thresholds": [
["Committed recurring above 90% of revenue", "Green", "The subscription framing is accurate. Apply the multiple to essentially all of it."],
["Committed recurring 75&ndash;90%", "Investigate", "Normal. Value the non-recurring portion separately rather than at the subscription multiple."],
["Committed recurring below 75%", "Price it in", "This is a hybrid business being sold as a subscription business. The blended multiple should reflect the mix."],
["Overage more than 20% of revenue and volatile", "Investigate", "You are buying exposure to your customers' volumes. Model the downside case on committed minimums only."],
["One-time fees rising as a share of revenue", "Investigate", "Growth is front-loading. Each new customer contributes more up front and less over time, which makes the model more sales-dependent."],
],
"dataroom": [
"A charge-level or line-item export, not just subscription totals.",
"A written classification of every product and price ID into recurring, usage, one-time and services.",
"Committed minimums versus actual consumption for every usage-based contract.",
"The revenue recognition policy, especially for annual prepayments and setup fees.",
],
"worked": "Illustrative. Reported ARR of $600,000, described as fully recurring. Line items resolve to $468,000 of committed subscription revenue, $72,000 of onboarding fees, $41,000 of usage overage and $19,000 of migration work. Committed recurring is 78% of the total. At a 4&times; multiple on the recurring portion and 1&times; on services and fees, the value is materially below 4&times; on the whole, and the gap is not a negotiating position — it is what the line items say. Separately, the overage tracks the customers' own transaction volumes, so the downside case has to be built on minimums.",
"consequence": "This is a valuation question more than a risk question, and it is the one most often settled by assertion rather than by data. The fix is mechanical: classify line items, apply the multiple bucket by bucket, and state the classification in the memo so it can be argued about explicitly. Where usage revenue is significant, also build the downside case on committed minimums only, because that is the floor you actually own.",
"faqs": [
("What counts as recurring revenue in a SaaS acquisition?",
 "Committed, contractual, repeating subscription revenue. Setup and onboarding fees are one-time. Usage overage above a committed minimum is contracted but not committed. Services and custom development are services revenue. All four can arrive through the same billing system, which is why they get blended together."),
("Should usage-based revenue be valued the same as subscription revenue?",
 "Generally not at the same multiple. The committed minimum behaves like subscription revenue; the overage behaves like your customers' business cycle, and it falls when their volumes fall. Separate the two and build the downside case on minimums only."),
("How do I separate one-time fees from MRR in a billing export?",
 "You need charge-level or line-item data rather than invoice totals, plus a mapping of product or price IDs to categories. Then classify every charge into committed recurring, usage, one-time and services, and recompute MRR from the first bucket alone. The gap against the reported figure is usually the entire finding."),
],
"tool": ("/free/mrr-health-check", "free MRR health check"),
"related": ["mrr-has-grown-every-month", "net-negative-churn", "ltv-is-3000", "all-customers-are-on-annual-contracts"],
},
{
"slug": "refunds-are-negligible",
"claim": "Refunds and chargebacks are negligible.",
"title": "Seller Says Refunds Are Negligible — How to Verify It | ChurnLens",
"description": "Refunds are usually small in aggregate and highly informative in distribution. Here is how to check the refund rate, the timing, and what a chargeback rate implies about the payment account you are inheriting.",
"h1": "The seller says: &ldquo;refunds and chargebacks are negligible&rdquo;",
"lead": "Refunds are rarely large enough to change a valuation, and that is exactly why the claim is worth checking: it is cheap to verify and the distribution tells you things nothing else in the export will. Early refunds indicate an expectation gap in the sales process. Chargebacks indicate the health of a payment account you are about to inherit.",
"why": "Sellers say this because it is usually true in aggregate, and because refunds are netted out of the revenue figures they look at, so the gross amount is genuinely not visible to them day to day. The information that matters is not the total but the shape: when refunds happen relative to sign-up, which plans they cluster in, and whether the chargeback rate is anywhere near the level at which a payment processor takes an interest.",
"hides": [
("Refunds clustered in the first thirty days",
 "A high early-refund rate means customers are arriving with the wrong expectation. That is a marketing and onboarding finding, and it usually correlates with elevated first-cycle churn among the customers who do not ask for their money back."),
("Chargebacks as a processor risk rather than a revenue item",
 "Chargeback rates above the thresholds payment processors monitor can trigger reserves, higher fees or account review. You are inheriting that account and its history. This is an operational risk that does not appear anywhere in the revenue analysis."),
("Refunds issued as credits or comped months instead",
 "A business that resolves complaints by extending the subscription for free shows almost no refunds and carries the cost in unbilled revenue. Look for zero-amount or heavily discounted periods on otherwise paying accounts."),
("A concentrated refund event",
 "One incident, one bad launch or one broken migration can produce a refund cluster in a single month. That is a service-failure signal, and the accounts involved are the ones most likely to churn in the following cycles."),
],
"verify": [
"Get gross refunds by month for twenty-four months, in dollars, before any netting.",
"Compute refunds as a share of gross revenue by month and look at the series, not the average.",
"Compute days from subscription start to refund for every refunded charge, and plot the distribution. The mass should be thin and spread, not piled inside the first month.",
"Segment refunds by plan and by acquisition channel. Concentration in one of either is a targeted finding.",
"Get the chargeback count and rate separately from refunds. Refunds are a business decision; chargebacks are a dispute, and processors treat them very differently.",
"Look for comped or zero-amount periods on paying accounts, which is where a no-refunds policy usually hides its costs.",
"Check the refund policy as actually stated to customers, and compare it to what the data shows happening.",
],
"thresholds": [
["Refunds under 2% of gross revenue, spread across tenure", "Green", "Genuinely negligible. Note it and move on."],
["Refunds 2&ndash;5% of gross revenue", "Investigate", "Not alarming, but worth understanding. Check the tenure distribution before accepting it."],
["More than half of refunds inside the first 30 days", "Investigate", "An expectation gap between what is sold and what is delivered. Expect it to show up in first-cycle churn too."],
["A single month above 3&times; the trailing average", "Investigate", "A service or product event. Identify it and check churn among the affected accounts in the following cycles."],
["Chargeback rate near processor monitoring thresholds", "Price it in", "This is a payment-account risk you inherit, including reserves and fees. Verify the account standing directly with the processor before close."],
],
"dataroom": [
"Gross refunds by month for twenty-four months, before netting.",
"Refund-level records with the original charge date, so time-to-refund can be computed.",
"Chargeback count, rate and outcomes, separately from refunds.",
"The current standing of the payment processor account, including any reserve, and the stated refund policy.",
],
"worked": "Illustrative. Refunds are 1.4% of gross revenue, which supports the claim. But 68% of refunded dollars are refunded within twenty-one days of sign-up, and 80% of those come from one paid acquisition channel. The aggregate is negligible and the distribution says the channel is buying customers who did not want the product. Those customers are also 3&times; more likely to churn in the first ninety days if they do not request a refund, so the refund line is a visible corner of a much larger acquisition-quality problem. The aggregate answer was true and uninformative.",
"consequence": "Refund analysis rarely moves a price and often changes what you do in the first quarter, which is why it is worth the twenty minutes. Early-refund clustering tells you which acquisition channels to turn off before you scale spend. Chargeback standing tells you whether the payment account you are inheriting is in good order, and that is a question best answered by the processor rather than by the seller.",
"faqs": [
("What is a normal refund rate for a small SaaS business?",
 "As a working guide we treat under 2% of gross revenue as unremarkable and above 5% as worth a specific explanation. Those are our thresholds rather than an industry standard, and the distribution matters more than the level: 1% concentrated in the first two weeks is more informative than 3% spread evenly across tenure."),
("Why do chargebacks matter separately from refunds?",
 "A refund is a decision the business made; a chargeback is a dispute the customer escalated to their card issuer. Processors monitor chargeback rates and can impose reserves, higher fees or account review. Because you inherit the payment account, chargeback history is an operational risk that does not appear in any revenue metric."),
("What does it mean if most refunds happen in the first month?",
 "That customers are arriving with a different expectation than the product delivers, which is a sales and onboarding problem rather than a product-quality one. It usually travels with elevated first-cycle churn among the customers who do not ask for a refund, so the visible refund line understates the size of the issue."),
],
"tool": ("/free/saas-health-score", "free SaaS health score"),
"related": ["we-intentionally-churned-bad-customers", "no-one-has-churned-recently", "logo-churn-is-low", "revenue-is-fully-recurring"],
},
{
"slug": "logo-churn-is-low",
"claim": "Logo churn is low.",
"title": "Seller Says Logo Churn Is Low — How to Verify It | ChurnLens",
"description": "Low logo churn is compatible with severe revenue churn when the departing accounts are large. Here is how to test the two against each other and read the divergence.",
"h1": "The seller says: &ldquo;logo churn is low&rdquo;",
"lead": "Logo churn counts customers; revenue churn counts dollars. Which one is lower depends entirely on whether the accounts that leave are bigger or smaller than average, and the gap between them is often the most informative single number you can compute from a subscription export.",
"why": "Logo churn is the figure most billing dashboards show first, and it is the intuitive one — customers are countable, dollars require normalising annual plans and handling partial periods. A seller quoting logo churn is quoting the number in front of them. The issue is that a buyer is acquiring revenue, and the two series diverge in exactly the situation a buyer most needs to know about.",
"hides": [
("Large accounts leaving among many small ones staying",
 "Losing 2% of logos that represent 8% of revenue is a serious event described in reassuring terms. Compute both and look at the ratio; a revenue-to-logo ratio above 2&times; means the book is losing its best customers."),
("A long tail of tiny accounts propping up the denominator",
 "Hundreds of low-price accounts make the logo percentage small and stable no matter what happens at the top. Recompute logo churn on the accounts that make up 80% of revenue and see whether the answer survives."),
("Downgrades that are not churn at all",
 "An account moving from $500 to $50 has not churned by any logo measure and has taken 90% of its revenue with it. Contraction has to be measured separately or it disappears entirely from a logo-based view."),
("Multi-subscription accounts counted once",
 "Where one customer holds several subscriptions, cancelling most of them barely registers as logo churn. Aggregate to the account level before counting anything."),
],
"verify": [
"Compute gross logo churn and gross revenue churn on the same period, the same denominator and the same paying-only filter. Never compare figures built on different bases.",
"Take the ratio of revenue churn to logo churn. At 1.0 the departing accounts are average sized; above 1.5 they are materially larger; below 0.7 you are losing the tail, which is a different and usually milder story.",
"Compute average revenue per churned account against average revenue per retained account, by month.",
"Recompute logo churn restricted to the accounts that make up the top 80% of revenue. If that figure is much worse than the headline, the tail was doing the work.",
"Measure contraction separately: revenue lost from accounts that shrank but did not leave, as a share of opening MRR.",
"Aggregate multiple subscriptions to one account identifier before any counting, and check how much difference that alone makes.",
"Plot both series for twenty-four months. A widening gap is the finding, more than either level.",
],
"thresholds": [
["Revenue-to-logo churn ratio between 0.8 and 1.3", "Green", "Departures are roughly average sized. The logo figure is a fair summary."],
["Ratio 1.3&ndash;2.0", "Investigate", "Larger accounts are leaving faster. Look at what the departing cohort has in common."],
["Ratio above 2.0", "Price it in", "The book is losing its best customers while the logo count looks stable. Underwrite on revenue churn only."],
["Contraction above 2% of opening MRR per month", "Investigate", "Significant revenue loss that no logo-based measure will ever show. Add it to the retention picture explicitly."],
["Logo churn on the top-80%-of-revenue accounts is much worse than the headline", "Price it in", "The tail was flattering the figure. The commercially relevant part of the book is churning faster."],
],
"dataroom": [
"Subscription rows with a stable account identifier, so multiple subscriptions can be aggregated to one customer.",
"Plan-change history, so downgrades can be separated from cancellations.",
"Normalised monthly amounts, or enough information to compute them for annual and multi-year terms.",
"A list of accounts that are not arm's-length paying customers, so they can be excluded from both measures.",
],
"worked": "Illustrative. Logo churn of 1.8% a month, which is genuinely good. Revenue churn on the same base is 5.1%, giving a ratio of 2.8. Average revenue per churned account is $340 against $118 for retained accounts. Recomputing logo churn on the accounts making up the top 80% of revenue gives 4.4%. The book has hundreds of small accounts that stay and a steady loss of the large ones that pay for everything. Both numbers are correct. The seller quoted the one that describes the customer list, and you are buying the revenue.",
"consequence": "The revenue-to-logo ratio is the cheapest high-value calculation in buyer-side diligence: two numbers you were computing anyway, one division, and it immediately tells you whether the churn you are being shown describes the part of the business you are paying for. Where the ratio is high, look at what the departing large accounts share — a plan, a vintage, a channel, a use case — because that commonality is usually the actual finding.",
"faqs": [
("What is the difference between logo churn and revenue churn?",
 "Logo churn is the share of customers lost; revenue churn is the share of recurring revenue lost. They differ whenever departing accounts are not average sized. If you lose many small customers, revenue churn is lower than logo churn; if you lose a few large ones, it is higher, and that is the case a buyer needs to catch."),
("Can logo churn be low while revenue churn is high?",
 "Yes, and it is one of the most common ways a retention story misleads. A long tail of small accounts that stay keeps the logo percentage low and stable while larger accounts leave. Take the ratio of revenue churn to logo churn: above about 2 means the book is losing its best customers."),
("Does a downgrade count as churn?",
 "Not as logo churn, and that is the problem. An account that drops from $500 to $50 has taken 90% of its revenue away without appearing in any customer-count measure. Contraction has to be measured separately as revenue lost from accounts that shrank but stayed, or it vanishes from the analysis entirely."),
],
"tool": ("/free/churn-calculator", "free churn calculator"),
"related": ["2-percent-monthly-churn", "no-customer-concentration", "the-churn-spike-was-seasonal", "no-one-has-churned-recently"],
},
{
"slug": "no-one-has-churned-recently",
"claim": "Nobody has churned in the last six months.",
"title": "Seller Says Nobody Has Churned Recently — How to Verify It | ChurnLens",
"description": "Zero churn over a period is usually a data artifact rather than a retention achievement. Here are the six mechanisms that produce it, and how to check each from the raw export.",
"h1": "The seller says: &ldquo;nobody has churned in the last six months&rdquo;",
"lead": "Absolute zero over a meaningful period is rare enough that the first hypothesis should always be a data artifact rather than an achievement. Six mechanisms produce it, only one of them is good news, and each leaves a distinctive trace in the export.",
"why": "This claim is often made in complete sincerity by someone reading a dashboard filter that excludes exactly the rows they need. Cancelled subscriptions are frequently hidden by default; failed payments sit in a dunning state that is neither active nor cancelled; and a book that is mostly annual genuinely has very few cancellation opportunities in any six-month window. The seller is describing what their screen shows.",
"hides": [
("Cancelled rows excluded from the export",
 "The most common cause by far. If the export was generated with an active-only filter, churn is definitionally zero. Check whether any row has a cancellation date at all; if none do across a two-year file, the filter is the finding."),
("Failed payments stuck in dunning",
 "An account that has not paid for four months but has not been formally cancelled is churn in every economic sense and is not cancelled in any data sense. Count subscriptions whose last successful payment is more than two cycles old."),
("Annual terms with no renewal in the window",
 "An annual-heavy book has few opportunities to churn in any given six months. Zero churn in a window with no renewals in it is arithmetic, not retention."),
("Zombie accounts that pay and do not use",
 "Accounts still billing with no meaningful usage are revenue that will disappear at the next review, price change or expense audit. They are indistinguishable from healthy revenue in a billing export and are the reason usage data is worth asking for."),
("Comped, internal and test accounts left active",
 "Internal accounts, lifetime deals and friends-and-family comps never churn and never generate cash. They inflate the base and suppress every rate computed against it."),
("Cancellations recorded as pauses or downgrades",
 "Where a product offers a pause or a free tier, departures land as a status change rather than a cancellation. Economically they are gone; in the export they are still there."),
],
"verify": [
"First, confirm the export contains cancelled subscriptions at all. Count rows with a non-null cancellation date across the full history. Zero across two years means an active-only filter, and you need a new export before anything else.",
"Count active subscriptions whose most recent successful payment is more than two billing cycles old. That is uncollected churn.",
"Count subscriptions in a dunning, past-due, unpaid or incomplete state, and their revenue as a share of reported MRR.",
"Count how many renewal events actually fell inside the six-month window. If very few did, the claim is about the calendar.",
"Identify zero-amount, 100%-discounted, internal-domain and lifetime-deal subscriptions, and exclude them from the base.",
"Ask for a paused or free-tier count and its trend. A rising pause count immediately before a sale is worth understanding.",
"If any usage or login data exists, count paying accounts with no activity in ninety days. That is the zombie MRR figure and it is often the largest single adjustment on this page.",
],
"thresholds": [
["Export contains cancellations, dunning under 2% of MRR, renewals did occur in the window", "Green", "Remarkable and apparently real. Verify with usage data if any exists, then credit it."],
["No cancelled rows anywhere in a 24-month export", "Red", "This is a filtered export, not a retention record. Request a complete one before doing any further analysis."],
["Dunning and past-due above 5% of reported MRR", "Price it in", "Churn that has happened and not been recorded. Deduct it from MRR before you value anything."],
["Fewer than 10% of subscriptions had a renewal in the window", "Investigate", "Zero churn is a property of the calendar. Reassess after the next renewal cohort."],
["Paying accounts with no 90-day activity above 10%", "Price it in", "Zombie MRR. It will not survive a price change, a card expiry or the customer's next expense review."],
],
"dataroom": [
"A complete subscription export explicitly including cancelled, paused and past-due rows.",
"Subscription status and the date of the most recent successful payment, per subscription.",
"A count of paused and free-tier accounts by month for twenty-four months.",
"Any usage, login or activity signal, even a crude one such as last login date.",
],
"worked": "Illustrative. The export shows 412 active subscriptions and no cancellations in six months. It also contains no cancellation dates at all across twenty-six months, which resolves the whole question: the file was generated active-only. A complete re-export shows 2.9% monthly churn. Separately, 31 of the 412 subscriptions last paid more than three months ago and sit in dunning, which is 7% of reported MRR that has economically churned and is still being counted. And 44 accounts have not logged in for ninety days. The true starting MRR is roughly 12% below the reported figure before a single churn calculation is run.",
"consequence": "This claim is worth taking seriously precisely because it is usually a filter rather than a fiction, which means it is fixable in one email. What is not fixable by re-export is the second half: dunning revenue and zombie accounts have to be deducted from MRR before you apply any multiple, because they will not be there in ninety days. That deduction is often larger than the entire churn adjustment.",
"faqs": [
("Is zero churn possible for a SaaS business?",
 "Over a short window with a small, annual, high-touch customer base, yes. Over six months with a monthly book, it is nearly always a data artifact — most often an export filtered to active subscriptions only, or failed payments sitting in dunning rather than being recorded as cancellations."),
("What is zombie MRR?",
 "Revenue from accounts that are still being billed but no longer use the product. It looks identical to healthy revenue in a billing export, and it disappears at the next price change, card expiry or expense review. Detecting it needs a usage or login signal alongside the billing data, which is why that signal is worth asking for."),
("How do I know if a subscription export is filtered?",
 "Count rows with a cancellation date. A genuine multi-year export from any real business contains many. Zero cancellation dates across two years means the export was generated with an active-only filter, and no analysis you run on it will be meaningful until you have a complete file."),
],
"tool": ("/free/zombie-mrr-detector", "free zombie MRR detector"),
"related": ["2-percent-monthly-churn", "all-customers-are-on-annual-contracts", "logo-churn-is-low", "refunds-are-negligible"],
},
{
"slug": "ltv-is-3000",
"claim": "Our LTV is $3,000, so we can spend $1,000 to acquire a customer.",
"title": "Seller Says LTV Is $3,000 — How to Verify It | ChurnLens",
"description": "LTV computed as ARPA divided by churn is arithmetically valid and practically unusable at low churn rates. Here is how to test an LTV claim and rebuild it on a bounded horizon.",
"h1": "The seller says: &ldquo;our LTV is $3,000&rdquo;",
"lead": "The standard LTV formula divides average revenue per account by the churn rate, which means the answer approaches infinity as churn approaches zero. Any error in a churn estimate is amplified into the LTV, and every LTV claim is therefore a churn claim wearing a dollar sign.",
"why": "Sellers quote LTV because it is the number that justifies acquisition spend, and the formula is genuinely standard. The trouble is structural rather than motivational: the formula assumes a constant churn rate applied forever, and no real business has either. At 2% monthly churn it implies a fifty-month average life; at 5% it implies twenty. The claim is not usually inflated on purpose, it is inflated by a denominator that was already the weakest number in the file.",
"hides": [
("An unbounded horizon",
 "Dividing by churn implicitly extrapolates forever. Recompute on twenty-four or thirty-six months of contribution, which is a horizon you can actually observe and underwrite, and the figure usually falls by half or more."),
("Gross revenue instead of gross margin",
 "LTV should use contribution after cost of revenue: hosting, payment fees, support and third-party API costs. Payment processing alone is typically a few percent, and support costs are frequently the largest single omission."),
("A churn rate borrowed from the wrong cohort",
 "Early-tenure churn is almost always much higher than late-tenure churn. Using a blended rate overstates the life of new customers, which is exactly the group the acquisition spend is buying."),
("No discounting",
 "Revenue arriving in month forty is worth materially less than revenue in month two. An undiscounted LTV overstates a long-horizon figure precisely where it is least reliable."),
],
"verify": [
"Recompute ARPA on paying accounts only, with annual plans normalised to monthly.",
"Recompute the churn rate yourself, in revenue terms, on a paying-only base. LTV inherits every error in this number and amplifies it.",
"Compute the naive formula, ARPA divided by monthly revenue churn, so you can see the seller's figure reproduced.",
"Now compute a bounded version: cumulative contribution over twenty-four and thirty-six months, using observed retention by tenure rather than a single constant rate.",
"Apply gross margin. Subtract hosting, payment fees, support and third-party costs to get contribution rather than revenue.",
"Build a retention curve by tenure month from actual cohorts, and use it instead of a flat rate. Early-tenure churn is the part that governs the payback on new acquisition.",
"Compute the payback period in months as customer acquisition cost divided by monthly gross-margin contribution. For a buyer this is more decision-relevant than LTV, because it is bounded and observable.",
],
"thresholds": [
["Bounded 24-month margin LTV within 25% of the claim", "Green", "The claim is conservative and usable. Rare, and worth noting when you see it."],
["Bounded figure is 40&ndash;60% of the claim", "Investigate", "Normal for an unbounded, gross-revenue formula. Recalibrate the acquisition maths on your number rather than theirs."],
["Bounded figure is under 40% of the claim", "Price it in", "The acquisition spend that the business has been running may not have been profitable. Check whether historical spend was justified by the real figure."],
["Payback period above 18 months", "Investigate", "Cash-hungry regardless of what LTV says. This is a working-capital question for the first year of ownership."],
["Cost of revenue not available at all", "Investigate", "LTV cannot be computed on margin without it. Treat any quoted figure as revenue-based and discount accordingly."],
],
"dataroom": [
"Cohort retention by tenure month, so a curve can replace a flat rate.",
"Cost of revenue detail: hosting, payment processing, support, third-party APIs.",
"Marketing and sales spend by month and by channel, so acquisition cost can be computed rather than asserted.",
"The formula behind the quoted LTV, in writing, including the churn rate used and its source.",
],
"worked": "Illustrative. ARPA of $60 and a quoted 2% monthly churn gives $3,000, which is the seller's figure and the formula is applied correctly. Recomputing churn on a paying-only, revenue-weighted base gives 4.1%, which alone takes the naive figure to $1,463. Applying a 78% gross margin gives $1,141. Bounding the horizon at thirty-six months with an observed retention curve, where first-year churn is higher than the blend, gives roughly $780. The claim and the rebuilt figure differ by nearly 4&times;, and every step between them is a definitional choice rather than a disagreement about the data. At a $1,000 acquisition cost, the first number says spend and the last says stop.",
"consequence": "LTV is the most leveraged number in a SaaS deal because it sits downstream of churn and multiplies its error. That makes it a poor primary metric for a buyer and an excellent secondary check: if the seller's LTV cannot be reproduced from your own churn figure, you have found a disagreement about retention, which is the thing you actually care about. Underwrite on payback period and bounded contribution instead, both of which are observable within a horizon you will own.",
"faqs": [
("Why is the standard LTV formula unreliable?",
 "Because dividing ARPA by the churn rate extrapolates a constant churn rate to infinity, so the answer approaches infinity as churn approaches zero. At 2% monthly churn it implies a fifty-month customer life; at 4% it implies twenty-five. Small errors in the churn estimate become large errors in LTV, and churn is usually the least reliable number in the file."),
("Should LTV use revenue or gross margin?",
 "Gross margin, always, for any decision about acquisition spend. Hosting, payment processing, support and third-party API costs all come out before the customer contributes anything. Using gross revenue overstates LTV by whatever the cost of revenue is, and support cost is the component most often left out."),
("What should a buyer use instead of LTV?",
 "Payback period and bounded contribution. Acquisition cost divided by monthly gross-margin contribution gives a payback in months, and cumulative contribution over twenty-four or thirty-six months gives a value on a horizon you can actually observe. Both avoid extrapolating a churn rate forever."),
],
"tool": ("/free/ltv-calculator", "free LTV calculator"),
"related": ["2-percent-monthly-churn", "net-negative-churn", "revenue-is-fully-recurring", "the-business-runs-itself"],
},
{
"slug": "the-business-runs-itself",
"claim": "The business runs itself, about five hours a week.",
"title": "Seller Says the Business Runs Itself — How to Verify It | ChurnLens",
"description": "The five-hours-a-week claim is testable against the subscription data. Here is where founder dependency shows up in a billing export, and what to ask for when it does.",
"h1": "The seller says: &ldquo;the business runs itself, about five hours a week&rdquo;",
"lead": "This is the claim that most changes what you are buying, and the one least visible in financial statements. It is more testable than it looks: founder dependency leaves fingerprints in the subscription data, in the acquisition mix, and in the shape of the largest accounts.",
"why": "Sellers are usually describing their current steady state honestly. Five hours a week can be genuinely true for a mature product with a settled customer base, and it can also be true only because the founder has absorbed a decade of context that makes each decision fast. The distinction is not about hours; it is about which of those hours are transferable. Nothing in a P&L captures that, so the test has to come from elsewhere.",
"hides": [
("Acquisition that is the founder personally",
 "If new customers arrive from the founder's audience, community presence, podcast appearances or personal network, the channel does not convey with the asset. Ask for acquisition source by month and check what share is attributable to a person rather than a system."),
("Support that is the founder personally",
 "Low support hours with high customer satisfaction often means one person answers everything with total product knowledge. Ask for ticket volume, median response time, and whether any documented process or macro library exists."),
("Relationships holding the largest accounts",
 "The top accounts in a founder-led business are frequently retained by a relationship rather than by the product. Cross-check the concentration analysis against tenure: long-tenured large accounts with no formal contract are relationship-held."),
("Deferred maintenance",
 "Five hours a week is sometimes achieved by not doing things. Ask about dependency versions, unpatched libraries, the last significant infrastructure change and any single-person deployment process. Deferred work becomes your work in month one."),
],
"verify": [
"Ask for acquisition source per new customer for twelve months. Compute the share arriving through channels that depend on a named individual.",
"Check whether new-customer volume correlates with the founder's public activity. A spike after each appearance is a personal-brand channel, not a marketing system.",
"Cross-reference the top twenty accounts against tenure and contract status. Long-tenured, large, uncontracted accounts are relationship-held.",
"Ask for support ticket volume by month, median first-response time, and whether documentation, macros or a help centre exist. Five hours a week with 400 customers implies something is either very well systematised or very well absorbed.",
"Establish who else touches the business: contractors, a virtual assistant, a support agency. Get the cost, because if it is not in the P&L your post-close cost base is understated.",
"Ask what the founder actually did in the last four weeks, specifically. The answer is usually more informative than any documentation.",
"Check the deployment and infrastructure story: who can deploy, what is the recovery process, when was the last dependency update.",
],
"thresholds": [
["Documented processes, non-founder support, systematised acquisition", "Green", "The claim is about the system rather than the person. This is what transferable looks like."],
["Under 20% of new customers from founder-attributable channels", "Green", "Acquisition will survive the transition. Verify the support story separately."],
["More than 40% of new customers from founder-attributable channels", "Price it in", "You are buying a product and not its distribution. Budget for replacement acquisition from day one."],
["Top accounts long-tenured, large and uncontracted", "Investigate", "Relationship-held revenue. Meet those customers before close and consider a hold-back tied to their retention."],
["No documentation, no second person, no deployment process", "Price it in", "The five hours are absorbed context. Price a transition period and a real handover, or budget to rebuild the knowledge."],
],
"dataroom": [
"Acquisition source per new customer for at least twelve months.",
"Support ticket volume, median response time, and any documentation, macros or help centre.",
"A list of everyone who touches the business, their role and their cost, whether or not it appears in the P&L.",
"Contract status and tenure for the top twenty accounts, and the deployment and recovery process in writing.",
],
"worked": "Illustrative. A $18,000 monthly SaaS, five hours a week, no employees. Acquisition source data shows 54% of new customers over twelve months arriving from one founder's community presence, with clear spikes after each public appearance. Six of the top ten accounts have been customers for over four years with no written contract. Support is 40 tickets a month answered personally, median response under two hours, with no documentation. Nothing here is misrepresented: the founder really does spend five hours a week. But roughly half the acquisition channel and a meaningful share of the retention leave with them, and the five hours become twenty for a new owner without the context. The correct response is not to walk away, it is to price the transition and to structure the deal so the handover actually happens.",
"consequence": "Founder dependency is the risk most likely to change the outcome of a small SaaS acquisition and the one least represented in the financials. It is also the most addressable through structure rather than price: a transition services agreement with defined deliverables, an earn-out tied to retained revenue, direct introductions to the largest accounts before close, and a documentation requirement as a condition of closing. Diagnose it from the data, then solve it in the contract.",
"faqs": [
("How do I test a claim that a SaaS business runs itself?",
 "Look for the founder in the data rather than in the hours. Acquisition source by month shows whether new customers arrive through a system or a person. Tenure and contract status on the largest accounts show whether revenue is held by the product or by a relationship. Support volume against documented process shows whether low hours mean systematised or absorbed."),
("What is founder dependency in a SaaS acquisition?",
 "The share of the business's performance that relies on one person's audience, relationships or accumulated context rather than on transferable systems. It rarely appears in financial statements, and it is usually the largest single gap between the business the seller runs and the business the buyer receives."),
("Can founder dependency be solved without changing the price?",
 "Often, yes, and structure is usually the better tool. A transition services agreement with specific deliverables, an earn-out tied to retained revenue, introductions to the top accounts before close and a documentation requirement as a closing condition all address the risk directly. Price is a blunt instrument for a problem that is really about handover."),
],
"tool": ("/saas-buyer-risk-assessment", "buyer risk assessment"),
"related": ["no-customer-concentration", "mrr-has-grown-every-month", "ltv-is-3000", "revenue-is-fully-recurring"],
},
]

BY_SLUG = {c["slug"]: c for c in CLAIMS}

# ---------------------------------------------------------------------------


def build_body(c: dict) -> str:
    p = []
    # TL;DR block: the site uses this pattern sitewide and it is what answer engines
    # lift as the direct answer.
    p.append(f'<p><strong>TL;DR:</strong> {c["description"]}</p>')

    p.append("<h2>What the claim usually means</h2>")
    p.append(f"<p>{c['why']}</p>")

    p.append("<h2>What it can hide</h2>")
    p.append("<p>Four mechanisms account for most of the gap between this claim and what the "
             "raw rows show. They are not mutually exclusive and they compound.</p>")
    for i, (name, expl) in enumerate(c["hides"], 1):
        p.append(f"<h3>{i}. {name}</h3><p>{expl}</p>")

    p.append("<h2>How to verify it from the raw subscription export</h2>")
    p.append("<p>Every step below runs on a subscription-level export in a spreadsheet. "
             "None of it needs access to the seller's live billing account, which matters, "
             "because as a buyer you will not get one.</p>")
    p.append("<ol>" + "".join(f"<li>{s}</li>" for s in c["verify"]) + "</ol>")

    p.append("<h2>Reading the result</h2>")
    p.append("<p>These are the thresholds we use in our own reports. They are working "
             "thresholds rather than industry standards, and the right line for a given deal "
             "depends on contract length, tenure and how transferable the customer "
             "relationships are.</p>")
    p.append(table(["What you find", "Verdict", "What to do about it"], c["thresholds"]))

    p.append("<h2>What to ask for in the data room</h2>")
    p.append("<p>Ask for these before the LOI. After the LOI you are renegotiating rather "
             "than negotiating, and a seller who will not produce subscription-level rows "
             "has told you something useful either way.</p>")
    p.append("<ul>" + "".join(f"<li>{s}</li>" for s in c["dataroom"]) + "</ul>")

    p.append("<h2>A worked example</h2>")
    p.append(f"<p>{c['worked']}</p>")

    p.append("<h2>Why it matters to the price</h2>")
    p.append(f"<p>{c['consequence']}</p>")

    tool_path, tool_label = c["tool"]
    p.append(f'<p>The relevant tool on this site is the <a href="{BASE}{tool_path}">'
             f'{tool_label}</a>, which runs the arithmetic above on a file you paste in. '
             f'The full method is documented in the '
             f'<a href="{BASE}/5-risk-buyer-side-method">5-risk buyer-side method</a> and the '
             f'<a href="{BASE}/saas-due-diligence-checklist">due-diligence checklist</a>.</p>')

    p.append("<h2>Other claims worth testing</h2>")
    p.append("<ul>" + "".join(
        f'<li><a href="{BASE}{HUB}/{r}">&ldquo;{esc(BY_SLUG[r]["claim"])}&rdquo;</a></li>'
        for r in c["related"] if r in BY_SLUG) + "</ul>")
    p.append(f'<p><a href="{BASE}{HUB}"><strong>All twelve seller claims &rarr;</strong></a></p>')

    return "\n".join(x for x in p if x)


def main() -> None:
    n = 0
    for c in CLAIMS:
        body = build_body(c)
        page = render(
            url_path=f"{HUB}/{c['slug']}",
            title=c["title"],
            description=c["description"],
            h1=c["h1"],
            lead=c["lead"],
            body=body,
            faqs=c["faqs"],
            hub_name=HUB_NAME,
            hub_path=HUB,
            breadcrumb_name=c["claim"].rstrip("."),
        )
        write(f"seller-claims/{c['slug']}", page)
        n += 1

    # ---- hub -------------------------------------------------------------
    rows = [[f'<a href="{BASE}{HUB}/{c["slug"]}">&ldquo;{esc(c["claim"])}&rdquo;</a>',
             c["hides"][0][0],
             f'<a href="{BASE}{c["tool"][0]}">{c["tool"][1]}</a>']
            for c in CLAIMS]
    hub_body = "\n".join([
        "<h2>The twelve claims</h2>",
        "<p>Each page takes one thing sellers say, explains why they say it, lists the "
        "mechanisms that can sit behind it, and gives the exact procedure for reproducing "
        "or refuting it from a subscription-level export. Thresholds are the ones we use in "
        "our own reports.</p>",
        table(["The claim", "Most common thing behind it", "Tool"], rows),
        "<h2>How to use this",
        "</h2>",
        "<p>Work through the claims that apply to the deal in front of you, in order of how "
        "much of the valuation rests on each. In practice that usually means starting with "
        "the churn rate, then customer concentration, then whichever growth or retention "
        "claim the price was justified by. Every check runs on a spreadsheet export; none of "
        "them needs access to the seller's live billing account.</p>",
        "<p>Two things are worth saying plainly. First, most of these claims are made in good "
        "faith &mdash; the usual cause is a dashboard default, not a deception, and the point "
        "of the exercise is to recompute under your own definition rather than to catch "
        "anyone out. Second, the answer that matters is rarely the level. It is the gap "
        "between the seller's figure and yours, and what explains it.</p>",
        f'<p>Related: <a href="{BASE}/saas-due-diligence-checklist">the 23-point due-diligence '
        f'checklist</a>, the <a href="{BASE}/5-risk-buyer-side-method">5-risk buyer-side '
        f'method</a>, <a href="{BASE}/marketplaces">due diligence by marketplace</a>, and '
        f'<a href="{BASE}/export">getting the export in the first place</a>.</p>',
    ])
    hub = render(
        url_path=HUB,
        title="What SaaS Sellers Say, and How to Verify It | ChurnLens",
        description="Twelve things SaaS sellers say about churn, retention and revenue quality — and the exact procedure for reproducing or refuting each one from a subscription-level export.",
        h1="What sellers say about churn, and how to check it",
        lead="Twelve claims you will hear in a SaaS acquisition, each with the mechanisms that can sit behind it and the arithmetic that settles it. Most are made in good faith and most do not survive recomputation under a buyer's definition.",
        body=hub_body,
        faqs=[
            ("Why do so many SaaS churn claims not survive verification?",
             "Because churn has no single agreed definition. Whether free accounts sit in the denominator, whether the figure counts customers or dollars, how annual plans are treated in non-renewal months, and whether reactivations are netted off each move the answer by between half a point and several points. A seller quoting their dashboard is quoting a real number computed under undisclosed assumptions."),
            ("What should a buyer ask for before the LOI?",
             "A subscription-level export including cancelled, paused and past-due rows, covering at least twenty-four months; the formula behind any quoted churn or retention figure in writing; contract terms and renewal dates for every account above 2% of revenue; and any usage or last-login signal. Aggregated monthly summaries cannot answer most of the questions that matter."),
            ("Do I need software to run these checks?",
             "No. Every procedure on these pages runs in a spreadsheet on a subscription export, and doing it by hand is the best way to understand a target's book. ChurnLens exists because most buyers would rather not spend the evening on it: send the export and we run the full human-reviewed analysis, with a free tier that covers one file a month."),
        ],
        hub_name="Home",
        hub_path="/",
        breadcrumb_name="Seller Claims",
    )
    write("seller-claims", hub)
    print(f"seller-claims: wrote {n} pages + hub")


if __name__ == "__main__":
    main()
