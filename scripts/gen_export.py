#!/usr/bin/env python3
"""/export/<platform> — getting a churn-analysable subscription export out of each billing system.

Strategic note: the 2026-07-25 traffic audit found that "buyer-side SaaS due
diligence" is a genuinely tiny query universe. These pages deliberately sit
upstream of it — "how do I export subscriptions from X" is asked by operators and
sellers as well as buyers, and everyone asking it has a file they want to
understand. It is the site's widest honest entry point and it lands on the
product's activation step.

Accuracy policy: describes each platform's *data model and known traps*, which are
stable, rather than UI click paths, which are not. Platforms are excluded rather
than guessed at. Links point at vendor documentation roots, never at deep URLs
that rot. Four platforms already covered under /integrations/ (Stripe, ChartMogul,
ProfitWell, QuickBooks) are deliberately not duplicated here.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pseo_shell import BASE, esc, render, table, write  # noqa: E402

HUB = "/export"
HUB_NAME = "Billing Exports"

# The seven fields every churn calculation needs. Shared framing, per-platform mapping.
NEEDED = [
    ("Account identifier", "A stable ID for the <em>customer</em>, not the subscription. Needed to aggregate multiple subscriptions to one account before counting anything."),
    ("Subscription status", "The current state, using the platform's own vocabulary. This is where most churn errors originate, because platform state names rarely mean what they sound like."),
    ("Amount and currency", "The recurring charge and its currency. Mixed-currency books need a conversion policy stated up front or every total is wrong."),
    ("Billing interval and term", "Monthly, annual or custom. Required to normalise everything to a monthly figure before any comparison."),
    ("Start date", "When the subscription began. Drives cohort analysis, tenure and the renewal calendar."),
    ("Cancellation or end date", "When it ended, if it did. An export without this field cannot produce a churn rate at all."),
    ("Last successful payment date", "The single most useful optional field. It separates subscriptions that are genuinely active from ones sitting in failed-payment limbo."),
]

PLATFORMS = [
{
"slug": "paddle",
"name": "Paddle",
"docs": "https://developer.paddle.com/",
"title": "Export Subscription Data from Paddle for Churn Analysis | ChurnLens",
"description": "Paddle is a merchant of record, so its revenue figures are net of fees and its prices are often tax-inclusive. Here is which Paddle objects to export, how to normalise them, and how Paddle Billing differs from Paddle Classic.",
"h1": "Exporting subscription data from Paddle for churn analysis",
"lead": "Paddle sells as merchant of record, which is convenient operationally and adds two specific distortions to any churn or MRR analysis: revenue arrives net of Paddle's fees, and displayed prices are frequently tax-inclusive with the tax rate varying by the customer's country.",
"model": "Paddle exposes subscriptions, transactions, customers and prices as separate objects. The subscription carries the recurring commitment; the transaction carries what actually moved, net of fees and tax. For churn you want the subscription objects, with transactions used only to establish whether payments have actually been landing. Note that Paddle has two generations of API and dashboard — Paddle Billing and the older Paddle Classic — with different object shapes and different export layouts. Establish which one the target is on before anything else, because a script written against one will silently misread the other.",
"mapping": [
["Account identifier", "Customer ID on the subscription object. Do not use the email, which changes.", "One customer can hold several subscriptions; aggregate first."],
["Subscription status", "<code>active</code>, <code>trialing</code>, <code>past_due</code>, <code>paused</code>, <code>canceled</code>", "<code>past_due</code> is unresolved churn, not revenue. Treat separately."],
["Amount and currency", "Recurring price on the subscription, plus currency code", "Frequently tax-inclusive. Two customers on the same plan in different countries can show different amounts."],
["Billing interval and term", "Billing cycle interval and frequency", "Normalise annual to monthly before summing."],
["Start date", "Subscription start / first billed date", "Paddle Classic and Billing name this differently."],
["Cancellation or end date", "Canceled-at, plus the scheduled change if a cancellation is pending", "A pending cancellation is economically churned and still shows as active."],
["Last successful payment date", "Derive from the most recent completed transaction", "Not present on the subscription object; you have to join."],
],
"gotchas": [
("Tax-inclusive pricing distorts MRR by geography",
 "Where displayed prices include VAT or sales tax, the recurring amount varies with the customer's country for the same plan. Summing those amounts gives you a gross-of-tax figure that is not revenue. Either use the net amount from the transaction records or apply the plan's list price consistently, and say in the memo which you did."),
("Revenue is net of merchant-of-record fees",
 "Because Paddle is the seller, what you see in payouts is after their fee and after tax remittance. A gross MRR built from subscription prices and a net revenue figure from payouts will never reconcile, and the gap is not a discrepancy — it is the fee and the tax. Reconcile them deliberately once, then work in one of the two consistently."),
("Paddle Billing and Paddle Classic are different systems",
 "Object names, status vocabularies and export columns differ between the two. A target that migrated part-way through the period you are analysing may have history split across both. Ask which generation the data came from, and whether the file spans a migration."),
("Pending cancellations look active",
 "A subscription scheduled to cancel at period end is still <code>active</code> until it ends. If you count status alone you will miss revenue that is already committed to leaving. Check for scheduled changes as well as status."),
],
"ask": "Please export all subscriptions from Paddle, including cancelled and past-due ones, for the full history. Confirm whether the account is on Paddle Billing or Paddle Classic. Include the recurring amount, currency, billing interval, start date, cancellation date and status, plus a note on whether displayed prices include tax. Separately, please export completed transactions so payment history can be reconciled.",
"faqs": [
("Why does Paddle MRR not match the payout figures?",
 "Because Paddle is a merchant of record. Subscription prices are gross and often tax-inclusive, while payouts are net of Paddle's fee and net of the tax they remit. Both numbers are correct and they measure different things. Reconcile them once, decide whether you are working gross or net, and state which in the analysis."),
("Does Paddle include cancelled subscriptions in an export?",
 "Only if the export was not filtered to active subscriptions. This is the single most common reason a churn analysis returns zero. Count rows with a cancellation date before doing anything else — if none exist across a multi-year file, request a complete export."),
("What is the difference between Paddle Billing and Paddle Classic for reporting?",
 "They are different generations with different object models, status vocabularies and export layouts. Analysis written for one misreads the other, usually silently. Establish which one produced the file, and ask specifically whether the history spans a migration between them."),
],
"related": ["chargebee", "lemon-squeezy", "fastspring", "recurly"],
},
{
"slug": "chargebee",
"name": "Chargebee",
"docs": "https://apidocs.chargebee.com/",
"title": "Export Subscription Data from Chargebee for Churn Analysis | ChurnLens",
"description": "Chargebee's non_renewing status is the trap: economically churned, still counted as active. Here is which Chargebee objects to export and how to handle addons, item prices and paused subscriptions.",
"h1": "Exporting subscription data from Chargebee for churn analysis",
"lead": "Chargebee produces some of the richest subscription exports available, which is good news, and it carries one status value that reverses the meaning of a churn calculation if you take it at face value: <code>non_renewing</code>.",
"model": "Chargebee separates customers, subscriptions, plans or item prices, addons and invoices. The subscription references one plan and any number of addons, and critically the addon amounts are held separately from the plan amount. An export that captures only the plan price understates MRR for every account with an addon, which in a mature Chargebee account is often most of them. Chargebee also distinguishes the subscription's own currency from the site currency, so multi-currency books need explicit handling.",
"mapping": [
["Account identifier", "Customer ID, distinct from subscription ID", "Chargebee's model genuinely supports many subscriptions per customer. Aggregate."],
["Subscription status", "<code>active</code>, <code>in_trial</code>, <code>non_renewing</code>, <code>paused</code>, <code>cancelled</code>, <code>future</code>", "<code>non_renewing</code> means it will not renew. Economically gone, textually active."],
["Amount and currency", "Plan unit amount &times; quantity, <strong>plus addon amounts</strong>, plus currency code", "Missing addons is the most common Chargebee MRR error."],
["Billing interval and term", "Billing period and billing period unit", "Chargebee supports arbitrary periods, not just month and year."],
["Start date", "Subscription started-at, and separately activated-at", "Trials mean these differ. Use activated-at for paying tenure."],
["Cancellation or end date", "Cancelled-at, plus cancel-scheduled-at for pending cancellations", "Both matter; the second is your forward churn."],
["Last successful payment date", "Derive from paid invoices for the subscription", "Chargebee's invoice history makes this reliable, unlike most platforms."],
],
"gotchas": [
("<code>non_renewing</code> is churn that has already happened",
 "A <code>non_renewing</code> subscription is still serving and still counted in most active-subscription reports, but the customer has already decided to leave. It should be excluded from forward MRR and counted as churn in the period the decision was made, not the period the subscription finally ends. Treating it as active is the single largest source of overstated MRR in a Chargebee book."),
("Addons sit outside the plan amount",
 "MRR built from plan price alone can be materially below actual billing. Sum plan amount times quantity, then add every recurring addon at its own quantity. Non-recurring addons should be excluded entirely, which means you also need each addon's type."),
("Paused subscriptions are ambiguous",
 "A pause can be a retention save or a slow cancellation, and the data does not distinguish them. Count paused subscriptions and their revenue separately, look at how many resume historically, and ask whether pausing was offered as an alternative to cancelling — because if it was, the pause count is part of the churn figure."),
("Item prices replaced plans in newer accounts",
 "Chargebee's newer product catalogue model uses items and item prices where older accounts used plans and addons. Exports differ accordingly. Confirm which catalogue version the account uses so you know whether you are missing a component."),
],
"ask": "Please export all subscriptions from Chargebee including cancelled, paused and non-renewing ones, for the full history, with customer ID, status, plan amount and quantity, all recurring addon amounts and quantities, currency, billing period and unit, started-at, activated-at, cancelled-at and any scheduled cancellation date. Please confirm whether the account uses plans and addons or the newer items and item prices catalogue.",
"faqs": [
("What does non_renewing mean in Chargebee?",
 "The subscription is still active and serving, but it is set not to renew at the end of the current term. Economically the customer has already churned; the revenue simply has not stopped yet. For any forward-looking MRR figure it should be excluded, and it should be counted as churn in the period the decision was made rather than the period service ends."),
("Why is my Chargebee MRR lower than actual billing?",
 "Almost always because addons were not included. Chargebee holds addon amounts separately from the plan amount, so an export or query that reads only the plan price understates every account carrying an addon. Sum plan amount times quantity plus each recurring addon, and exclude non-recurring addons."),
("Should paused Chargebee subscriptions count as churned?",
 "It depends on whether pausing is offered as a retention alternative to cancelling, and on how many historically resume. Count them separately either way and ask the seller both questions. If pause was the save offer, the pause count belongs in the churn analysis rather than beside it."),
],
"related": ["recurly", "maxio", "paddle", "zuora"],
},
{
"slug": "recurly",
"name": "Recurly",
"docs": "https://recurly.com/developers/",
"title": "Export Subscription Data from Recurly for Churn Analysis | ChurnLens",
"description": "In Recurly, canceled does not mean gone — expired does. Getting that backwards inverts a churn rate. Here is the state model, the export you need, and how to handle add-ons and trials.",
"h1": "Exporting subscription data from Recurly for churn analysis",
"lead": "Recurly has the most consequential vocabulary trap of any major billing platform. A <code>canceled</code> subscription is still active and still serving until its term ends. The state that means actually gone is <code>expired</code>. Analyse Recurly with the intuitive reading of those words and your churn rate is wrong in both directions at once.",
"model": "Recurly models accounts, subscriptions, plans, add-ons and invoices. A subscription belongs to an account, references a plan, and can carry add-ons whose amounts are separate from the plan's unit amount. The state machine is the important part: <code>future</code>, <code>active</code>, <code>canceled</code>, <code>expired</code>, <code>paused</code> and <code>failed</code>, where <code>canceled</code> is a subscription that will not renew but has not yet reached the end of its paid term.",
"mapping": [
["Account identifier", "Account code or account ID, not the subscription UUID", "Recurly accounts can hold multiple concurrent subscriptions."],
["Subscription status", "<code>future</code>, <code>active</code>, <code>canceled</code>, <code>expired</code>, <code>paused</code>, <code>failed</code>", "<strong><code>canceled</code> is still serving. <code>expired</code> is gone.</strong> This is the whole game."],
["Amount and currency", "Plan unit amount &times; quantity, plus add-on amounts, plus currency", "Add-ons are separate objects with their own quantities."],
["Billing interval and term", "Plan interval unit and interval length", "Recurly supports multi-month terms that are neither monthly nor annual."],
["Start date", "Activated-at, and separately trial-started-at / trial-ends-at", "Use activated-at for paying tenure, not created-at."],
["Cancellation or end date", "Canceled-at (decision date) and expires-at (service end date)", "Two different dates with two different meanings. You need both."],
["Last successful payment date", "Derive from the subscription's paid invoices", "Also check for subscriptions in a failed or dunning state."],
],
"gotchas": [
("<code>canceled</code> versus <code>expired</code> inverts the answer",
 "Counting <code>canceled</code> as churn overstates churn in the current period, because those subscriptions are still paying until they expire. Counting only <code>expired</code> as churn understates forward churn, because it ignores every customer who has already decided to leave. The correct treatment uses both: <code>canceled_at</code> as the churn <em>decision</em> date for cohort analysis, and <code>expires_at</code> as the revenue <em>stop</em> date for MRR. Report the decision date, because it is the one that tells you what is happening now."),
("Add-ons are separate and quantity-bearing",
 "As in Chargebee, an MRR figure built from plan amounts alone understates any account with add-ons. Recurly add-ons carry their own quantities, so you need amount and quantity for each rather than a single add-on total."),
("Trials inflate the account count",
 "Subscriptions in trial are active and paying nothing. Filter them out of the churn denominator or the rate is diluted directly. Recurly gives you trial start and end dates, so this is straightforward once you remember to do it."),
("Paused subscriptions keep their term",
 "Recurly's pause holds the subscription without advancing the billing cycle. For a buyer, paused revenue is neither present nor definitively lost. Count it separately and ask for the historical resume rate."),
],
"ask": "Please export all Recurly subscriptions in every state including canceled, expired, paused and failed, for the full history, with account code, state, plan code, plan unit amount and quantity, all add-on codes with amounts and quantities, currency, interval unit and length, activated-at, trial start and end, canceled-at and expires-at. The distinction between canceled-at and expires-at matters, so please include both columns.",
"faqs": [
("What is the difference between canceled and expired in Recurly?",
 "A canceled Recurly subscription will not renew but is still active and still serving until the end of its paid term. An expired subscription has actually ended. The intuitive reading of those two words is backwards, and getting it wrong inverts a churn rate — so use canceled-at as the churn decision date and expires-at as the revenue stop date."),
("Which Recurly date should a churn cohort use?",
 "The cancellation date, because that is when the customer decided to leave and it is what tells you about the current period. The expiry date is what you use for MRR, since revenue continues until then. Reporting only expiry dates lags reality by up to a full billing term."),
("Do Recurly add-ons need to be included in MRR?",
 "Yes. Add-ons are separate objects with their own amounts and quantities, so a figure built from plan unit amounts alone understates any account carrying one. Sum plan amount times quantity plus each add-on amount times its own quantity."),
],
"related": ["chargebee", "maxio", "braintree", "paddle"],
},
{
"slug": "maxio",
"name": "Maxio (Chargify)",
"docs": "https://developers.maxio.com/",
"title": "Export Subscription Data from Maxio / Chargify for Churn Analysis | ChurnLens",
"description": "Maxio combines Chargify billing with SaaSOptics reporting, and components hold revenue outside the product price. Here is which side of the platform your export came from and what it omits.",
"h1": "Exporting subscription data from Maxio and Chargify for churn analysis",
"lead": "Maxio is two products that were merged: Chargify on the billing side and SaaSOptics on the reporting side. Which one produced your file changes what it contains and what it has already decided on your behalf, and that is the first thing to establish.",
"model": "On the Chargify side the objects are customers, subscriptions, products, product families and components, where components carry quantity-based, metered and on-off charges separately from the product price. On the SaaSOptics side you get contract and revenue-schedule level data that has already had revenue recognition applied. The two describe the same business with different assumptions baked in, and a churn analysis built on a recognition-adjusted export is answering a different question from one built on billing records.",
"mapping": [
["Account identifier", "Customer ID on the Chargify side; contract or account on the SaaSOptics side", "The two do not always map one-to-one. Ask which is authoritative."],
["Subscription status", "<code>active</code>, <code>trialing</code>, <code>past_due</code>, <code>canceled</code>, <code>on_hold</code>, <code>unpaid</code>, <code>trial_ended</code>", "<code>on_hold</code> and <code>unpaid</code> are both revenue at risk, not revenue."],
["Amount and currency", "Product price, <strong>plus every component</strong> (quantity-based, metered, on-off)", "Components are the Chargify equivalent of addons and are easy to miss entirely."],
["Billing interval and term", "Product interval and interval unit", "Chargify supports arbitrary interval lengths."],
["Start date", "Subscription created-at and activated-at", "Trials separate the two."],
["Cancellation or end date", "Canceled-at, plus delayed-cancel-at for end-of-term cancellations", "Delayed cancellation is a pending churn signal."],
["Last successful payment date", "Derive from the subscription's transactions or statements", "Also check <code>past_due</code> and <code>unpaid</code> counts."],
],
"gotchas": [
("Metered components make MRR genuinely ambiguous",
 "Where a meaningful share of revenue comes from metered usage, there is no single correct MRR. The defensible approach is to report committed recurring revenue from product prices and fixed components separately from usage revenue, and to build the downside case on committed amounts only. Blending them produces a figure that falls when your customers' volumes fall, which is not what a subscription multiple is meant to price."),
("A SaaSOptics-side export has recognition already applied",
 "Revenue recognition smooths annual contracts across the term, which is correct for accounting and wrong for a renewal calendar. If your file came from the reporting side you cannot see when contracts actually renew, which is the artifact a buyer most needs. Ask for billing-side subscription records as well."),
("<code>on_hold</code> and <code>unpaid</code> are not active",
 "Both states describe subscriptions that are not currently producing cash. They frequently sit inside an active-subscription count. Separate them and treat their revenue as at risk until proven otherwise."),
("Product families fragment the plan picture",
 "Chargify organises products into families, and a target with several families may have overlapping or superseded pricing across them. Get the full product and component catalogue, not just the subscription rows, or you will not be able to tell a legacy price from a current one."),
],
"ask": "Please export all Chargify subscriptions including canceled, on-hold, unpaid and past-due, for the full history, with customer ID, state, product handle and price, every component with its type, quantity and amount, currency, interval and unit, created-at, activated-at, canceled-at and any delayed-cancellation date. Please also send the full product and component catalogue. If any figures come from the SaaSOptics side, please say so, since revenue recognition changes what they mean.",
"faqs": [
("Is Maxio the same as Chargify?",
 "Maxio is the combined company formed from Chargify and SaaSOptics. Chargify is the billing side and SaaSOptics is the revenue-reporting side. They are different data models with different assumptions, so the first question about any Maxio export is which side produced it."),
("How should usage-based revenue be handled in a churn analysis?",
 "Separately. Report committed recurring revenue from product prices and fixed components apart from metered usage, and build the downside case on committed amounts only. Usage revenue tracks your customers' volumes rather than your own retention, so blending it into MRR prices someone else's business cycle at a subscription multiple."),
("Why does a SaaSOptics export not show renewal dates?",
 "Because revenue recognition spreads an annual contract evenly across its term, which removes the lumpiness that a renewal calendar is made of. It is the right treatment for accounting and the wrong input for working out which month a fifth of your revenue comes up for renewal. Ask for billing-side subscription records alongside it."),
],
"related": ["chargebee", "recurly", "zuora", "paddle"],
},
{
"slug": "braintree",
"name": "Braintree",
"docs": "https://developer.paypal.com/braintree/docs/",
"title": "Export Subscription Data from Braintree for Churn Analysis | ChurnLens",
"description": "Braintree is a gateway, not a subscription analytics platform, so there is no MRR figure to disagree with. Here is how to assemble one from plans, subscriptions, add-ons and discounts.",
"h1": "Exporting subscription data from Braintree for churn analysis",
"lead": "Braintree is a payment gateway that happens to offer recurring billing, not a subscription management platform. That has one advantage for a buyer: there is no dashboard MRR figure to reconcile against, so nobody has already made definitional choices for you. Everything has to be assembled, which means you get to make those choices yourself.",
"model": "Braintree models customers, payment methods, plans, subscriptions, add-ons, discounts and transactions. The subscription references a plan and carries its own price, which may differ from the plan price because add-ons and discounts are applied as separate objects with their own amounts and quantities. There is no built-in cohort or churn reporting, so the export is a raw materials list rather than a report.",
"mapping": [
["Account identifier", "Customer ID, distinct from payment method token", "A customer can have multiple payment methods and subscriptions."],
["Subscription status", "<code>Active</code>, <code>Canceled</code>, <code>Expired</code>, <code>Past Due</code>, <code>Pending</code>", "<code>Past Due</code> is a dunning state and is common in card-heavy books."],
["Amount and currency", "Subscription price, <strong>plus add-ons, minus discounts</strong>", "The subscription price alone is not what is billed."],
["Billing interval and term", "Plan billing frequency in months", "Braintree expresses everything in months; annual is 12."],
["Start date", "First billing date, and separately created-at", "Free trials shift these apart."],
["Cancellation or end date", "Subscription updated-at when status became Canceled", "Braintree does not always give a clean dedicated cancellation timestamp; derive from status history if available."],
["Last successful payment date", "Most recent settled transaction on the subscription", "Essential here, because Braintree's dunning behaviour is configurable per merchant."],
],
"gotchas": [
("There is no MRR, so build it explicitly",
 "Because Braintree offers no MRR figure, nobody has decided how annual plans, discounts or trials are treated. Write your definition down before you compute anything, apply it consistently, and put it in the memo. This is more work and produces a more defensible number than reconciling against someone else's dashboard."),
("Discounts and add-ons both move the real amount",
 "The billed amount is the subscription price plus add-ons minus discounts, each with its own quantity and its own number of remaining billing cycles. A discount with a finite duration means the amount will change on a known future date, which matters for any forward projection."),
("Cancellation timing is imprecise",
 "Braintree's subscription records are less explicit about when a cancellation was requested versus when it took effect than purpose-built billing platforms. Where the distinction matters, reconcile against transaction history: the last settled transaction bounds the revenue stop date even when the status timestamp is ambiguous."),
("Number-of-billing-cycles limits create silent endings",
 "A Braintree subscription can be configured with a fixed number of billing cycles, after which it simply expires. Those are scheduled endings, not churn, and they should be identified and reported separately or they will look like a retention problem in whichever month they land."),
],
"ask": "Please export all Braintree subscriptions in every status including canceled, expired and past due, for the full history, with customer ID, status, plan ID, subscription price, every add-on and discount with amount and quantity, billing frequency, first billing date, created-at, and number of billing cycles if any is set. Please also export settled transactions per subscription so payment history can be reconciled, since there is no MRR report to work from.",
"faqs": [
("Does Braintree report MRR or churn?",
 "No. Braintree is a payment gateway with recurring billing, not a subscription analytics platform, so there is no built-in MRR or churn reporting. Both have to be computed from plans, subscriptions, add-ons, discounts and transactions. The upside is that no definitional choices have been made for you."),
("How do I compute the real billed amount for a Braintree subscription?",
 "Start with the subscription price, add every add-on at its own amount and quantity, then subtract every discount at its own amount and quantity. Check each discount's remaining billing cycles too, because a finite discount means the amount changes on a known future date."),
("What does a fixed number of billing cycles mean for churn?",
 "It means the subscription is scheduled to end rather than at risk of churning. Those endings should be identified from the configuration and reported separately, otherwise they appear as churn in whichever month they happen to land and make retention look worse than it is."),
],
"related": ["paypal", "recurly", "chargebee", "gocardless"],
},
{
"slug": "paypal",
"name": "PayPal",
"docs": "https://developer.paypal.com/docs/subscriptions/",
"title": "Export Subscription Data from PayPal for Churn Analysis | ChurnLens",
"description": "PayPal subscription records are the thinnest of any common billing source, and buyers are usually handed transaction lists instead. Here is how to reconstruct a subscription view and what you cannot recover.",
"h1": "Exporting subscription data from PayPal for churn analysis",
"lead": "PayPal is the hardest common source to analyse, for a structural reason: many businesses using it for recurring payments never had a subscription object in the first place, only a series of transactions. Reconstructing subscriptions from transaction history is possible and lossy, and it is worth knowing in advance which parts are unrecoverable.",
"model": "Modern PayPal Subscriptions has products, plans and subscriptions with proper statuses. But a large share of long-running PayPal recurring revenue predates that model or was implemented with older recurring-payment profiles or plain repeated billing agreements. In those cases there is no subscription object to export, and what you receive is an activity or transaction report. The two situations require completely different approaches, so establish which one you are in before requesting anything.",
"mapping": [
["Account identifier", "Payer ID or payer email from the subscription or transaction", "Email is often the only stable link available. It changes, which is a real limitation."],
["Subscription status", "<code>APPROVAL_PENDING</code>, <code>ACTIVE</code>, <code>SUSPENDED</code>, <code>CANCELLED</code>, <code>EXPIRED</code>", "Only available if real subscription objects exist. Otherwise infer from payment gaps."],
["Amount and currency", "Plan billing cycle amount, or the transaction amount", "Transaction amounts are net of PayPal fees; plan amounts are gross."],
["Billing interval and term", "Plan billing cycle frequency", "If reconstructing, infer from the median gap between payments."],
["Start date", "Subscription start time, or the first transaction date", "The first-transaction proxy is usually reliable."],
["Cancellation or end date", "Status update time, or inferred from payment cessation", "This is the field most often unrecoverable. See below."],
["Last successful payment date", "Most recent completed transaction", "Always available, and it is what you build everything else on."],
],
"gotchas": [
("Churn dates usually have to be inferred, not read",
 "Where there are no subscription objects, a cancellation is invisible: all you see is that payments stopped. The workable convention is to treat a payer as churned when their gap since the last payment exceeds roughly 1.5 billing intervals, and to state that convention explicitly in the analysis. It is defensible and it is an estimate, and the difference matters when the number is being used to set a price."),
("Transaction amounts are net of fees",
 "Building revenue from transaction records gives a figure net of PayPal's fees, while a plan-based figure is gross. Decide which basis you are using, apply it throughout, and note it. Mixing the two within one analysis is the most common error on PayPal data."),
("Involuntary churn is invisible and material",
 "PayPal recurring payments fail for expired funding sources and revoked billing agreements, and those failures often look identical to voluntary cancellation. A book with high involuntary churn is more recoverable than one with high voluntary churn, and on PayPal data alone you frequently cannot distinguish them. Say so rather than assuming."),
("Refunds and disputes need separate retrieval",
 "PayPal handles refunds and disputes in their own records rather than as adjustments on the original transaction. A revenue figure built from completed payments alone is gross of both. Request them explicitly."),
],
"ask": "Please confirm first whether recurring revenue runs through PayPal Subscriptions with actual subscription objects, or through older recurring-payment profiles or repeated billing agreements. If subscriptions exist, please export all of them in every status with payer ID, plan, amount, currency, billing cycle, start time and status update time. If they do not, please export the full completed-transaction history with payer ID or email, amount, currency and date, plus refunds and disputes separately.",
"faqs": [
("Can you calculate churn from PayPal data?",
 "Yes, with a stated convention and a wider error bar than any other source. If real subscription objects exist you can read statuses directly. If not, churn has to be inferred from payments stopping, typically treating a gap of more than about 1.5 billing intervals as churn. Either way, write the convention into the analysis, because it is an estimate."),
("Why is PayPal harder to analyse than Stripe or Chargebee?",
 "Because much long-running PayPal recurring revenue was implemented without subscription objects at all, so there is nothing to export except transactions. Cancellation dates, plan changes and the distinction between voluntary and involuntary churn are all absent from a transaction list, and no amount of care recovers information that was never recorded."),
("Are PayPal transaction amounts gross or net?",
 "Net of PayPal's fees. Plan amounts, where they exist, are gross. Pick one basis for the whole analysis and state which, because mixing gross plan amounts with net transaction amounts is the most common error made on PayPal data."),
],
"related": ["braintree", "gumroad", "gocardless", "woocommerce-subscriptions"],
},
{
"slug": "lemon-squeezy",
"name": "Lemon Squeezy",
"docs": "https://docs.lemonsqueezy.com/",
"title": "Export Subscription Data from Lemon Squeezy for Churn Analysis | ChurnLens",
"description": "Lemon Squeezy is a merchant of record with a cancelled-but-still-active status. Here is the status model, the fee and tax treatment, and how one-off products get mixed into subscription revenue.",
"h1": "Exporting subscription data from Lemon Squeezy for churn analysis",
"lead": "Lemon Squeezy is a merchant of record aimed at software and digital products, which means two things for an analysis: revenue arrives net of their fee and of remitted tax, and the store frequently sells one-off products alongside subscriptions in the same order history.",
"model": "The objects are stores, products, variants, orders, subscriptions and subscription invoices. A subscription references a variant and carries a status plus a renewal date. Because the same store can sell one-time licences and recurring plans through the same checkout, the order history is a mixture and the subscription objects are the only reliable way to isolate recurring revenue.",
"mapping": [
["Account identifier", "Customer ID on the subscription", "Email is also present, but the customer ID is stable."],
["Subscription status", "<code>on_trial</code>, <code>active</code>, <code>paused</code>, <code>past_due</code>, <code>unpaid</code>, <code>cancelled</code>, <code>expired</code>", "<code>cancelled</code> runs until <code>ends_at</code>. <code>expired</code> is gone."],
["Amount and currency", "Subscription or variant price, plus store currency", "Displayed amounts may include tax depending on configuration."],
["Billing interval and term", "Variant interval and interval count", "Monthly and annual are both common; check both fields."],
["Start date", "Subscription created-at", "Trials mean paying tenure starts later."],
["Cancellation or end date", "<code>ends_at</code> for the service stop, plus the status change date for the decision", "As with Recurly, two dates with two meanings."],
["Last successful payment date", "Most recent paid subscription invoice", "Subscription invoices are separate from orders. Request both."],
],
"gotchas": [
("<code>cancelled</code> still serves until <code>ends_at</code>",
 "A cancelled Lemon Squeezy subscription remains active until the end of the paid period, at which point it becomes <code>expired</code>. Use the status change for the churn decision date and <code>ends_at</code> for the revenue stop date. Counting only <code>expired</code> lags reality by up to a full billing period."),
("One-off products sit in the same order history",
 "Lifetime licences, one-time purchases and add-on downloads appear alongside subscription renewals. Any revenue figure built from orders rather than from subscriptions blends recurring and non-recurring revenue, and the two carry very different multiples. Isolate subscriptions explicitly."),
("Merchant-of-record fees and tax make gross and net diverge",
 "As with any merchant of record, the amount a customer pays, the amount recognised as revenue and the amount that reaches the bank are three different figures. Establish which one you are working in and keep it consistent."),
("Paused subscriptions retain their renewal date",
 "A pause defers billing without ending the subscription. Count paused revenue separately and ask how many historically resume, because a pause offered as an alternative to cancelling is part of the churn story rather than an aside to it."),
],
"ask": "Please export all Lemon Squeezy subscriptions in every status including cancelled, expired, paused and past-due, for the full history, with customer ID, status, variant, price, currency, interval and interval count, created-at, renews-at and ends-at. Please also export subscription invoices separately from orders, and flag which products are one-time purchases rather than recurring plans.",
"faqs": [
("What is the difference between cancelled and expired in Lemon Squeezy?",
 "A cancelled subscription is still active and still serving until its ends-at date, when it becomes expired. For a churn cohort, use the date the status changed to cancelled, since that is when the customer decided. For MRR, use ends-at, since revenue continues until then."),
("How do I separate one-off sales from subscription revenue in Lemon Squeezy?",
 "Work from subscription objects rather than orders. A Lemon Squeezy store can sell lifetime licences and one-time products through the same checkout, so the order history is a mixture. Ask the seller to flag which products are recurring, and treat one-time revenue at a different multiple."),
("Is Lemon Squeezy revenue reported gross or net?",
 "It depends which figure you are looking at. As a merchant of record, Lemon Squeezy collects a gross amount from the customer, remits tax, deducts its fee, and pays out a net amount. Those are three different numbers and any analysis needs to state which basis it uses."),
],
"related": ["paddle", "gumroad", "freemius", "fastspring"],
},
{
"slug": "gumroad",
"name": "Gumroad",
"docs": "https://gumroad.com/help",
"title": "Export Subscription Data from Gumroad for Churn Analysis | ChurnLens",
"description": "Gumroad sales exports mix one-off purchases with memberships in one file, and that mixture is the main analytical problem. Here is how to isolate recurring revenue and read the membership fields.",
"h1": "Exporting subscription data from Gumroad for churn analysis",
"lead": "Gumroad's export is a sales file rather than a subscription file, and its central difficulty is that one-off product sales and recurring memberships arrive in the same rows. Separating them is most of the work, and getting it wrong produces an MRR figure that is largely one-time revenue.",
"model": "Gumroad is built around products and sales, with memberships layered on as products that recur. A sale row carries the product, the buyer, the amount and a recurrence indicator where applicable. There is no rich subscription state machine of the kind Chargebee or Recurly provides, so subscription status has to be derived from whether membership charges are still arriving.",
"mapping": [
["Account identifier", "Buyer email, and the subscription ID where a membership exists", "Email is usually the only stable identifier. Note the limitation."],
["Subscription status", "Derive from whether recent recurring charges exist", "There is no full status vocabulary. Cancellation is often visible only as charges stopping."],
["Amount and currency", "Sale price, net or gross of Gumroad's fee depending on the report", "Confirm which basis the export uses. It matters and it is not obvious."],
["Billing interval and term", "Recurrence field on membership products: monthly, yearly and others", "One-off sales have no recurrence value. That is your filter."],
["Start date", "First membership charge date for that buyer and product", "Reliable, and easy to compute."],
["Cancellation or end date", "Usually inferred from charges ceasing; sometimes an explicit cancellation date", "Ask for the membership-level report, which carries more than the sales report."],
["Last successful payment date", "Most recent sale row for that membership", "This is the backbone of the whole reconstruction."],
],
"gotchas": [
("One-off sales and memberships share the export",
 "This is the defining problem. Filter on the recurrence field to isolate memberships, then verify by checking that each retained buyer has multiple charges at a consistent interval. A Gumroad business is very often mostly one-time revenue with a membership tail, and that mix determines the multiple more than the churn rate does."),
("Free trials and pay-what-you-want distort the amounts",
 "Gumroad supports pay-what-you-want pricing and discount codes freely, so two buyers on the same membership can pay different amounts indefinitely. Use the actual charge amounts rather than a list price, and expect genuine dispersion rather than a clean price ladder."),
("Cancellation is usually invisible",
 "Without an explicit cancellation field you are inferring churn from charges stopping. Ask for the membership or subscriber report rather than only the sales report, since it carries more status information. Where you still have to infer, state the convention: a gap beyond about 1.5 intervals counts as churned."),
("Fee basis varies between reports",
 "Different Gumroad reports present amounts gross and net of fees. Establish which you have before summing anything, and do not mix reports within one analysis."),
],
"ask": "Please export the full Gumroad sales history and, separately, the membership or subscriber report, for all time. Include buyer email, product, subscription or membership ID, recurrence, amount, currency, date, and any cancellation date available. Please confirm whether the amounts in each report are gross or net of Gumroad's fees, and flag which products are memberships rather than one-time purchases.",
"faqs": [
("Can you calculate MRR from a Gumroad export?",
 "Yes, once memberships are isolated from one-off sales using the recurrence field. The bigger question is usually what share of revenue is recurring at all, because many Gumroad businesses are predominantly one-time sales with a membership tail, and that mix affects valuation more than the churn rate does."),
("How do you detect cancellations in Gumroad data?",
 "Usually by charges ceasing, since the sales export has no cancellation status. Ask for the membership or subscriber report, which carries more. Where inference is unavoidable, adopt an explicit convention such as a gap of more than 1.5 billing intervals and state it in the analysis."),
("Why do two Gumroad customers on the same product pay different amounts?",
 "Because Gumroad supports pay-what-you-want pricing and freely applied discount codes, so paid amounts genuinely disperse for the same product. Build revenue from actual charge amounts rather than a list price, and do not treat the dispersion as a data error."),
],
"related": ["lemon-squeezy", "freemius", "paypal", "fastspring"],
},
{
"slug": "freemius",
"name": "Freemius",
"docs": "https://freemius.com/help/documentation/",
"title": "Export Subscription Data from Freemius for Churn Analysis | ChurnLens",
"description": "Freemius sells WordPress plugins and themes on a licence model, where lifetime deals and non-renewing annual licences behave nothing like SaaS subscriptions. Here is how to read it.",
"h1": "Exporting subscription data from Freemius for churn analysis",
"lead": "Freemius is the billing layer behind a large share of commercial WordPress plugins and themes, and its licence-based model behaves differently from SaaS subscriptions in one decisive way: a meaningful share of revenue is often lifetime licences, which never renew and never churn, and which should not carry a recurring multiple.",
"model": "Freemius models plugins, plans, licences, subscriptions and payments. A licence grants access and has an expiry; a subscription is the recurring payment arrangement behind an auto-renewing licence. Lifetime licences have no subscription at all. Because the WordPress plugin market sells heavily on annual licences with updates and support, the renewal decision is annual and highly visible, which makes renewal-rate analysis unusually informative here.",
"mapping": [
["Account identifier", "User ID, plus licence ID and subscription ID", "One user can hold licences across several plugins. Aggregate by user."],
["Subscription status", "Active, cancelled, or absent entirely for lifetime licences", "The absence of a subscription is itself the key signal. Do not read it as missing data."],
["Amount and currency", "Subscription or licence amount and currency", "Renewal amounts often differ from initial amounts because of renewal discounts."],
["Billing interval and term", "Annual, monthly or lifetime", "Lifetime must be excluded from recurring revenue entirely."],
["Start date", "Licence created date, or first payment date", "Straightforward."],
["Cancellation or end date", "Subscription cancellation date, plus licence expiry", "A cancelled subscription still leaves a licence valid until expiry."],
["Last successful payment date", "Most recent payment on the subscription", "Needed to distinguish an expired licence from a failed renewal."],
],
"gotchas": [
("Lifetime licences are not recurring revenue",
 "Lifetime deals are common in the WordPress market and they are one-time revenue with an ongoing support obligation, which is close to the opposite of a subscription. They should be excluded from MRR, valued separately, and counted as a cost of service going forward. A Freemius business with a large lifetime cohort can look far more recurring than it is."),
("Renewal discounts mean renewal revenue is below initial revenue",
 "Where a renewal is discounted relative to the first year, revenue per customer declines on a known schedule even with perfect retention. Model the renewal amount, not the acquisition amount, and check whether the discount is permanent or first-renewal only."),
("Annual licences make retention lumpy and highly visible",
 "Almost all decisions land in the licence anniversary month, so monthly churn is close to meaningless and the annual renewal rate is close to everything. Build the renewal calendar and compute the observed renewal rate on cohorts that have actually reached an anniversary."),
("An expired licence is not necessarily a cancellation",
 "Licences expire because a subscription was cancelled, because a renewal payment failed, or because the licence was never auto-renewing. Those are voluntary churn, involuntary churn and a scheduled ending respectively, and only the payment history distinguishes them."),
],
"ask": "Please export all Freemius licences, subscriptions and payments for the full history, with user ID, plugin, plan, licence ID, subscription ID where one exists, amount and currency for both initial and renewal, billing period including lifetime, created date, expiry date, cancellation date, and payment history. Please flag lifetime licences explicitly and state whether renewals are discounted relative to first purchase.",
"faqs": [
("How should lifetime licences be valued in a plugin business acquisition?",
 "As one-time revenue with an ongoing support and update obligation, not as recurring revenue. They belong outside MRR and outside the subscription multiple, and the support cost of servicing them should be treated as a going-forward expense. A large lifetime cohort makes a business look more recurring than it is."),
("Why does Freemius revenue per customer fall even with good retention?",
 "Because renewal pricing is frequently discounted relative to the first purchase. Even at a perfect renewal rate, revenue per customer steps down at the first anniversary. Model the renewal amount rather than the acquisition amount, and check whether the discount applies once or to every renewal."),
("What is the right churn metric for an annual licence business?",
 "The observed annual renewal rate on cohorts that have actually reached an anniversary, not a monthly churn rate. With annual licences, almost every decision lands in the anniversary month, so a monthly figure mostly measures the calendar. Build the renewal calendar first."),
],
"related": ["lemon-squeezy", "gumroad", "woocommerce-subscriptions", "fastspring"],
},
{
"slug": "revenuecat",
"name": "RevenueCat",
"docs": "https://www.revenuecat.com/docs/",
"title": "Export Subscription Data from RevenueCat for Churn Analysis | ChurnLens",
"description": "App-store subscriptions churn differently: store commission, billing-retry grace periods and involuntary churn all behave unlike card-on-web. Here is how to read a RevenueCat export.",
"h1": "Exporting subscription data from RevenueCat for churn analysis",
"lead": "Mobile subscription data has three properties that break assumptions carried over from web billing: revenue arrives net of a substantial app-store commission, cancellation and expiry are separated by a grace period the store controls, and a large share of churn is involuntary billing failure rather than a customer decision.",
"model": "RevenueCat sits above the App Store and Google Play, normalising their receipts into customers, entitlements, subscriptions and transactions. The important consequence is that RevenueCat reports what the stores tell it, and the stores control the billing retry and grace-period behaviour. So a subscription's state reflects store mechanics as much as customer intent, and the two need separating before any churn figure means anything.",
"mapping": [
["Account identifier", "App user ID, plus the original transaction or store identifier", "App user IDs can be anonymous and can be reassigned. Confirm the identity model."],
["Subscription status", "Active, in grace period, in billing retry, cancelled but not expired, expired", "Cancelled-not-expired and billing-retry are both still-serving states."],
["Amount and currency", "Price in the customer's local currency; proceeds are net of store commission", "Local pricing tiers mean the same product has many prices. Normalise to one currency with a stated rate."],
["Billing interval and term", "Product duration: weekly, monthly, annual and others", "Weekly subscriptions exist in mobile and churn very differently. Do not blend them."],
["Start date", "Original purchase date", "Distinguish from the current period start."],
["Cancellation or end date", "Unsubscribe-detected-at for intent, expires-at for service end", "These can be weeks apart. Both matter."],
["Last successful payment date", "Most recent renewal transaction", "Combined with billing-retry state, this separates involuntary from voluntary churn."],
],
"gotchas": [
("Store commission means gross price is not revenue",
 "App stores take a substantial commission that varies by programme and by developer size, so the price a customer pays and the proceeds the business receives are materially different figures. Establish the effective commission rate from actual payouts rather than assuming a headline rate, and state which basis your revenue figures use."),
("Involuntary churn is large and separately addressable",
 "A significant share of mobile churn is failed renewal rather than cancellation — expired payment methods, insufficient funds, store account problems. That distinction matters commercially: involuntary churn is partly recoverable through billing retry and win-back, voluntary churn is a product or price problem. Report them separately, always."),
("Cancelled and expired can be weeks apart",
 "A customer who turns off auto-renew keeps access until the period ends, and a customer in billing retry keeps access through a grace period. Use unsubscribe-detected-at for intent and expires-at for revenue, exactly as with the web platforms that separate decision from termination."),
("Weekly and trial-heavy products distort every blended rate",
 "Mobile catalogues often mix weekly, monthly and annual products, and heavy free-trial usage means trial-to-paid conversion matters more than churn. Segment by product duration and report trial conversion separately, or a blended churn rate will describe nothing that exists."),
],
"ask": "Please export the full RevenueCat subscription and transaction history, with app user ID, original transaction ID, product identifier and duration, store, price and currency, original purchase date, current period start and expiry, unsubscribe-detected-at, billing-retry and grace-period status, and renewal transactions. Please also provide actual store payouts for the same period so the effective commission rate can be established rather than assumed.",
"faqs": [
("Why is mobile subscription churn higher than web churn?",
 "Largely because involuntary churn is much more common. Store-managed payment methods expire and fail without the business being able to intervene directly, so a meaningful share of mobile churn is failed renewal rather than a customer decision. Any comparison to web benchmarks needs voluntary and involuntary churn separated first."),
("How much of app-store revenue does the developer actually receive?",
 "Materially less than the price the customer pays, and the exact commission depends on the store's programme and the developer's circumstances. Rather than applying a headline rate, derive the effective rate from actual payouts against gross sales for the same period, then state which basis your revenue figures use."),
("Should trial conversion be analysed separately from churn?",
 "Yes. Mobile catalogues lean heavily on free trials, and trial-to-paid conversion is a different mechanism from post-conversion retention. Blending them produces a churn rate dominated by trial behaviour, which tells you very little about the paying base you would be acquiring."),
],
"related": ["paddle", "lemon-squeezy", "chargebee", "maxio"],
},
{
"slug": "woocommerce-subscriptions",
"name": "WooCommerce Subscriptions",
"docs": "https://woocommerce.com/document/subscriptions/",
"title": "Export Subscription Data from WooCommerce Subscriptions for Churn Analysis | ChurnLens",
"description": "WooCommerce keeps subscriptions in the WordPress database with statuses like pending-cancel and on-hold that do not mean what they sound like. Here is how to export and read them.",
"h1": "Exporting subscription data from WooCommerce Subscriptions for churn analysis",
"lead": "A WooCommerce subscription lives in the site's own database rather than in a hosted billing platform, which means the data is fully available and entirely unnormalised. Its status vocabulary carries two values that mislead: <code>pending-cancel</code> is still serving, and <code>on-hold</code> can mean several different things.",
"model": "WooCommerce Subscriptions stores each subscription as a record in the WordPress database with a status, a parent order, renewal orders and line items. Recurring revenue is on the line items rather than in a single price field, and each renewal produces its own order. Because the store is self-hosted, the export depends on whichever plugin or query produced it, so the provenance of the file matters more here than with a hosted platform.",
"mapping": [
["Account identifier", "WordPress user ID, or billing email for guest checkouts", "Guest checkouts break the user-ID link. Expect both."],
["Subscription status", "<code>wc-active</code>, <code>wc-on-hold</code>, <code>wc-pending-cancel</code>, <code>wc-cancelled</code>, <code>wc-expired</code>, <code>wc-pending</code>", "<code>pending-cancel</code> is still serving to period end. <code>on-hold</code> is ambiguous."],
["Amount and currency", "Sum of recurring line items, plus store currency", "Not a single price field. Shipping and tax lines may be included."],
["Billing interval and term", "Billing period and billing interval", "Interval can be greater than one, e.g. every 3 months."],
["Start date", "Subscription start date, and the parent order date", "Usually the same; check for backdated imports."],
["Cancellation or end date", "End date, cancelled date, and next payment date", "<code>pending-cancel</code> subscriptions have a future end date."],
["Last successful payment date", "Most recent completed renewal order", "Renewal orders are the reliable payment record."],
],
"gotchas": [
("<code>pending-cancel</code> is a decision already made",
 "A subscription in <code>pending-cancel</code> has been cancelled by the customer and continues to serve until the paid period ends. It should count as churn from the cancellation date, not the end date, and it should be excluded from forward MRR. Reports that count it as active overstate the book."),
("<code>on-hold</code> means at least three different things",
 "It can indicate a failed renewal payment, a manual suspension, or a customer-initiated pause depending on how the store is configured and which payment gateway is in use. Ask which, because failed payment is involuntary churn, a manual hold is an operational matter, and a pause is a retention save. They should not share a bucket."),
("Revenue is on line items, with tax and shipping mixed in",
 "There is no single recurring-amount field. Recurring revenue has to be summed from line items, and physical-goods stores may have shipping and tax lines in the same total. Isolate the subscription product lines explicitly."),
("The export's provenance determines what is missing",
 "Because WooCommerce is self-hosted, the file could come from a plugin export, a database query or a REST API call, and each includes different fields. Always ask how the file was produced, and ask specifically whether cancelled and expired subscriptions were included."),
],
"ask": "Please export all WooCommerce subscriptions in every status including cancelled, expired, on-hold and pending-cancel, for the full history, with user ID or billing email, status, recurring line items with amounts, currency, billing period and interval, start date, next payment date, end date and cancellation date. Please also export renewal orders. Please say how the export was produced and what on-hold means on this store.",
"faqs": [
("What does pending-cancel mean in WooCommerce Subscriptions?",
 "The customer has cancelled and the subscription continues to serve until the end of the period already paid for. It is churn from the cancellation date, not from the end date, and it should be excluded from any forward MRR figure. Counting it as active is a common way WooCommerce books get overstated."),
("Why are some WooCommerce subscriptions on-hold?",
 "On-hold covers at least three distinct situations: a failed renewal payment, a manual suspension by the store, and a customer-initiated pause. Which one it means depends on the store's configuration and payment gateway, so it has to be asked rather than inferred. They are involuntary churn, an operational matter and a retention save respectively."),
("How do I get the recurring amount from a WooCommerce subscription?",
 "Sum the recurring line items, since there is no single price field. Be careful to isolate subscription product lines from tax and shipping lines, which appear in the same totals on stores that also ship physical goods."),
],
"related": ["freemius", "paypal", "braintree", "gocardless"],
},
{
"slug": "gocardless",
"name": "GoCardless",
"docs": "https://developer.gocardless.com/",
"title": "Export Subscription Data from GoCardless for Churn Analysis | ChurnLens",
"description": "Bank debit churns differently from cards: mandates outlive subscriptions, failures resolve on a longer cycle, and involuntary churn is lower. Here is how to read a GoCardless export.",
"h1": "Exporting subscription data from GoCardless for churn analysis",
"lead": "GoCardless collects by bank debit rather than card, and that changes the retention arithmetic in a way worth understanding rather than normalising away. Mandates do not expire the way cards do, so involuntary churn is structurally lower, but failures take longer to resolve and the mandate can outlive the subscription it was created for.",
"model": "The objects are customers, bank accounts, mandates, subscriptions and payments. A mandate is the standing authorisation to debit an account; a subscription is a schedule of payments drawn against it. Because a mandate persists independently, a cancelled subscription can leave an active mandate, and one mandate can support several subscriptions. That indirection is where most analytical mistakes come from.",
"mapping": [
["Account identifier", "Customer ID, not the mandate ID", "One customer can hold multiple mandates and subscriptions."],
["Subscription status", "<code>pending_customer_approval</code>, <code>active</code>, <code>finished</code>, <code>cancelled</code>, <code>paused</code>", "<code>finished</code> means a fixed-count schedule completed. Not churn."],
["Amount and currency", "Subscription amount and currency", "Multi-currency is common given GoCardless's geographic spread."],
["Billing interval and term", "Interval unit and interval, plus count if the schedule is finite", "A finite count means a scheduled ending."],
["Start date", "Subscription start date, and mandate created-at", "The mandate can predate the subscription."],
["Cancellation or end date", "Subscription cancelled-at, plus mandate status", "Check both: a cancelled subscription with a live mandate is a different situation from a cancelled mandate."],
["Last successful payment date", "Most recent confirmed or paid-out payment", "Bank debit settles more slowly than cards; allow for it."],
],
"gotchas": [
("<code>finished</code> is not churn",
 "A subscription with a fixed number of payments moves to <code>finished</code> when the schedule completes. That is a planned ending, and counting it as churn makes retention look worse than it is. Identify finite schedules from the count field and report them separately."),
("Mandate status and subscription status are independent",
 "A cancelled subscription on a live mandate means the relationship is intact and the schedule stopped, which is quite different from a cancelled mandate. Conversely, a failed or revoked mandate ends collection regardless of subscription status. Read both fields together or you will misclassify a meaningful share of endings."),
("Failures resolve on a longer cycle than cards",
 "Bank debit failures and their retries take longer than card dunning, so a payment that looks failed today may settle later. Any analysis run close to the present will overstate recent churn. Cut the analysis window back by at least one full settlement cycle before drawing conclusions about recent months."),
("Involuntary churn is genuinely lower, so do not benchmark against card books",
 "Bank mandates do not expire the way cards do, which structurally reduces involuntary churn. That is a real advantage of the payment method and it means a GoCardless book's total churn is more voluntary — and therefore more product- and price-driven — than a card-based book with the same headline rate."),
],
"ask": "Please export all GoCardless subscriptions in every status including cancelled, finished and paused, for the full history, with customer ID, mandate ID and mandate status, subscription status, amount, currency, interval unit and interval, payment count if the schedule is finite, start date, created-at and cancelled-at. Please also export the payment history including failed payments, so settlement timing and involuntary churn can be separated.",
"faqs": [
("Does bank debit reduce SaaS churn compared with cards?",
 "It reduces involuntary churn, because bank mandates do not expire the way payment cards do. That is a genuine structural advantage. It does not change voluntary churn, so a bank-debit book and a card book with the same headline churn rate actually have different underlying retention, with the bank-debit one carrying proportionally more real customer decisions."),
("What does a finished GoCardless subscription mean?",
 "That a subscription with a fixed number of payments completed its schedule. It is a planned ending rather than churn, and counting it as churn understates retention. Identify finite schedules from the payment-count field and report their endings separately."),
("Why should recent months be excluded from GoCardless churn analysis?",
 "Because bank debit failures and retries resolve over a longer cycle than card dunning, so payments that look failed in the most recent period may still settle. Trimming the analysis window back by at least one full settlement cycle avoids overstating churn in exactly the months people look at most closely."),
],
"related": ["braintree", "paypal", "chargebee", "woocommerce-subscriptions"],
},
{
"slug": "fastspring",
"name": "FastSpring",
"docs": "https://developer.fastspring.com/",
"title": "Export Subscription Data from FastSpring for Churn Analysis | ChurnLens",
"description": "FastSpring is a merchant of record with a long tail of legacy software pricing, so exports frequently mix perpetual licences, maintenance plans and true subscriptions. Here is how to separate them.",
"h1": "Exporting subscription data from FastSpring for churn analysis",
"lead": "FastSpring has been selling software for long enough that a mature account often contains three generations of commercial model at once: perpetual licences with maintenance, annual subscriptions, and modern monthly plans. Separating those is the main analytical task, because only one of the three is recurring revenue in the sense a multiple assumes.",
"model": "The objects are accounts, products, subscriptions and orders, with FastSpring acting as merchant of record and therefore handling tax and appearing as the seller. Subscriptions carry a state and a next-charge date; orders record what was actually transacted. As with any merchant of record, gross customer payment, recognised revenue and net payout are three different figures.",
"mapping": [
["Account identifier", "Account ID, with email as a secondary key", "Long-lived accounts may have multiple products across generations."],
["Subscription status", "Active, overdue, cancelled, deactivated, trial", "Cancelled subscriptions may remain in service to the period end."],
["Amount and currency", "Subscription price and currency; payout is net of fees and tax", "Multi-currency and local pricing are common."],
["Billing interval and term", "Interval and interval length", "Annual dominates in legacy software accounts."],
["Start date", "Subscription begin date, plus original order date", "These differ when a perpetual licence later gained a maintenance plan."],
["Cancellation or end date", "Cancellation date and deactivation date", "Two states, two dates, as with several other platforms."],
["Last successful payment date", "Most recent completed order for the subscription", "Needed to distinguish overdue from cancelled."],
],
"gotchas": [
("Perpetual licences and maintenance plans are not subscriptions",
 "A perpetual licence is one-time revenue. A maintenance or support plan attached to it is recurring but usually renews at a low rate and can be declined without losing the product, so its retention behaves nothing like SaaS. Separate all three models before computing anything, and apply different multiples to each."),
("Merchant-of-record accounting separates three figures",
 "The customer's gross payment, the recognised revenue and the net payout all differ, because FastSpring remits tax and deducts its fee. State which basis you are using and be consistent, since reconciling MRR against bank deposits without accounting for both will always show a gap."),
("Legacy pricing tiers persist for years",
 "Long-running accounts accumulate grandfathered prices, and revenue per customer varies widely for the same product. Get the full product and pricing history so a legacy price can be distinguished from a current one, otherwise the pricing analysis will look chaotic rather than historical."),
("Overdue is unresolved, not lost",
 "An overdue subscription has failed to charge and has not yet been cancelled. It is revenue at risk. Count it separately and check the historical recovery rate rather than treating it as either active or churned."),
],
"ask": "Please export all FastSpring subscriptions in every state including cancelled, deactivated and overdue, for the full history, with account ID, product, state, price, currency, interval and interval length, begin date, next charge date, cancellation and deactivation dates. Please also send the full product catalogue and pricing history, and flag which products are perpetual licences, which are maintenance plans and which are true subscriptions.",
"faqs": [
("How should perpetual licences with maintenance be valued?",
 "As two separate things. The licence is one-time revenue and belongs outside MRR entirely. The maintenance or support plan is recurring, but it typically renews at a lower rate than SaaS because the customer keeps the product either way, so it warrants its own retention analysis and its own multiple."),
("Why does FastSpring MRR not reconcile to bank deposits?",
 "Because FastSpring is a merchant of record. It collects a gross amount, remits tax, deducts its fee and pays out the remainder, so gross subscription value, recognised revenue and net payout are three different numbers. Reconcile them once deliberately and then work consistently in one basis."),
("What does an overdue FastSpring subscription mean for churn?",
 "That a charge failed and the subscription has not been cancelled. It is revenue at risk rather than revenue lost or revenue earned. Count it separately, and ask for the historical recovery rate so it can be weighted rather than guessed at."),
],
"related": ["paddle", "freemius", "lemon-squeezy", "zuora"],
},
{
"slug": "zuora",
"name": "Zuora",
"docs": "https://developer.zuora.com/",
"title": "Export Subscription Data from Zuora for Churn Analysis | ChurnLens",
"description": "Zuora models amendments rather than simple subscription states, so the current row does not tell you what changed or when. Here is how to reconstruct history from rate plan charges and amendments.",
"h1": "Exporting subscription data from Zuora for churn analysis",
"lead": "Zuora is built for complex enterprise contracts, and its data model reflects that: a subscription is a versioned object modified by amendments, with revenue held in rate plan charges rather than in a single price. The current subscription row tells you very little about how it got there, which is exactly what a churn analysis needs.",
"model": "Accounts hold subscriptions; subscriptions hold rate plans; rate plans hold rate plan charges, which is where amounts, quantities and effective dates actually live. Changes are recorded as amendments that create new subscription versions, so a single commercial relationship spans multiple rows. Any analysis that reads only the latest version of each subscription will miss every upgrade, downgrade and partial cancellation in the history — which for an enterprise book is most of what matters.",
"mapping": [
["Account identifier", "Account ID, distinct from subscription number and subscription ID", "Enterprise accounts routinely hold many subscriptions."],
["Subscription status", "Draft, active, pending activation, pending acceptance, cancelled, expired, suspended", "Status is per version. Read the latest version per subscription number."],
["Amount and currency", "Sum of rate plan charge amounts &times; quantities, plus currency", "There is no single subscription price. This is the biggest structural difference from other platforms."],
["Billing interval and term", "Charge billing period, plus initial and renewal term on the subscription", "Multi-year terms with annual billing are common."],
["Start date", "Subscription start date and contract effective date", "These differ and both are used in practice. Confirm which the seller means."],
["Cancellation or end date", "Cancelled date, term end date, and any cancellation amendment", "The amendment carries the intent; the term end carries the revenue stop."],
["Last successful payment date", "Most recent paid invoice for the subscription", "Enterprise collections are slower; do not read a lag as churn."],
],
"gotchas": [
("Revenue lives in rate plan charges, not on the subscription",
 "A Zuora subscription has no single price field. Recurring revenue is the sum of its rate plan charges, each with its own amount, quantity, billing period and effective dates. Any export that omits charge-level rows cannot produce an MRR figure at all, and this is the most common reason a Zuora analysis has to be restarted."),
("Amendments are the history, and they are easy to lose",
 "Upgrades, downgrades, quantity changes and partial cancellations are all amendments creating new subscription versions. Reading only the current version gives you the end state with no path, so contraction becomes invisible and expansion looks like it was always there. Request amendment history explicitly."),
("Partial cancellation is contraction, not churn",
 "Enterprise customers frequently cancel some rate plans while keeping others. That is contraction and it will not appear in any status-based churn measure, since the subscription remains active. On an enterprise book, contraction is often larger than outright churn."),
("Multi-year terms defer decisions far out",
 "Where subscriptions carry multi-year initial terms, several years can pass with almost no renewal events. Reported churn over that window describes a period in which leaving was largely unavailable. Build the renewal calendar over the full term structure rather than a twelve-month window."),
],
"ask": "Please export Zuora subscriptions with full amendment history and all rate plan charges, for the full history, including account ID, subscription number and version, status, every rate plan charge with amount, quantity, billing period and effective start and end dates, currency, contract effective date, initial and renewal term, term end date and cancellation date. Charge-level rows and amendment history are both essential; a subscription-level export alone cannot produce MRR.",
"faqs": [
("Why can't you compute MRR from a Zuora subscription export?",
 "Because a Zuora subscription has no price field. Recurring revenue lives in rate plan charges, each with its own amount, quantity, billing period and effective dates. Without charge-level rows there is nothing to sum, which is why a subscription-level export is not enough to start."),
("What are Zuora amendments and why do they matter for churn?",
 "Amendments are how Zuora records changes: upgrades, downgrades, quantity changes and partial cancellations each create a new subscription version. Reading only the current version gives the end state with no history, so contraction disappears entirely and expansion appears to have always been there. Amendment history has to be requested explicitly."),
("How does partial cancellation affect an enterprise churn rate?",
 "It does not appear in one at all, which is the problem. When a customer cancels some rate plans and keeps others, the subscription stays active and no status-based measure records anything. That is contraction, and on enterprise books it is frequently larger than outright logo churn."),
],
"related": ["maxio", "chargebee", "fastspring", "recurly"],
},
]

BY_SLUG = {p["slug"]: p for p in PLATFORMS}

# ---------------------------------------------------------------------------


def build_body(p: dict) -> str:
    o = []
    o.append(f'<p><strong>TL;DR:</strong> {p["description"]}</p>')

    # The full seven-field explainer lives on the hub only. Repeating it verbatim on
    # fourteen pages is exactly the duplication that got the /vs/ family flagged as thin.
    o.append(f'<p>Every churn calculation needs the same seven things: a stable '
             f'<strong>customer identifier</strong>, <strong>subscription status</strong>, '
             f'<strong>recurring amount and currency</strong>, <strong>billing interval and '
             f'term</strong>, <strong>start date</strong>, <strong>cancellation or end '
             f'date</strong>, and ideally the <strong>date of the last successful '
             f'payment</strong>. '
             f'(<a href="{BASE}{HUB}">Why each one, and what breaks without it &rarr;</a>) '
             f'What changes between platforms is where those fields live and which status '
             f'values mislead you.</p>')

    o.append(f"<h2>How {p['name']} models this</h2>")
    o.append(f"<p>{p['model']}</p>")

    o.append(f"<h2>Field mapping for {p['name']}</h2>")
    o.append(table(["Needed", f"Where it lives in {esc(p['name'])}", "Watch out for"], p["mapping"]))

    o.append(f"<h2>{p['name']}-specific traps</h2>")
    o.append("<p>These are the errors we see repeatedly on this platform. Each one is "
             "silent: the analysis completes and returns a number that is wrong.</p>")
    for i, (name, expl) in enumerate(p["gotchas"], 1):
        o.append(f"<h3>{i}. {name}</h3><p>{expl}</p>")

    o.append("<h2>What to ask for, in words you can paste</h2>")
    o.append("<p>Vague requests produce filtered exports. This wording asks for the complete "
             "set in the platform's own vocabulary, which is what gets you a usable file "
             "first time:</p>")
    o.append(f'<blockquote>{p["ask"]}</blockquote>')

    o.append("<h2>Before you trust the file</h2>")
    o.append(f'<p>One check first, and it is the same on every platform: <strong>count the '
             f'rows that carry a cancellation or end date.</strong> If none do across a '
             f'multi-year {p["name"]} export, the file was filtered to active subscriptions '
             f'and every churn figure you compute from it will come out at zero. That single '
             f'defect causes more wrong churn numbers than every definitional argument put '
             f'together, and it is fixed with one email rather than with analysis. '
             f'The <a href="{BASE}{HUB}">three further checks</a> &mdash; row count, MRR '
             f'reconciliation and history length &mdash; take another five minutes.</p>')

    o.append("<h2>What to do with the file</h2>")
    o.append(f'<p>Once you have a clean export, the analysis is the same regardless of where '
             f'it came from: recompute churn in both logo and revenue terms, build the '
             f'renewal calendar, check concentration on parent entities rather than accounts, '
             f'and test whatever the seller has claimed. The '
             f'<a href="{BASE}/seller-claims">seller-claims pages</a> cover the twelve claims '
             f'worth testing and the arithmetic for each, and the '
             f'<a href="{BASE}/saas-due-diligence-checklist">23-point checklist</a> is the '
             f'short version.</p>')
    o.append(f'<p>Official {p["name"]} documentation: <a href="{p["docs"]}" rel="nofollow noopener" '
             f'target="_blank">{p["docs"]}</a>. Export layouts change; the data model and the '
             f'traps above do not.</p>')

    o.append("<h2>Other billing systems</h2>")
    o.append("<ul>" + "".join(
        f'<li><a href="{BASE}{HUB}/{r}">Exporting from {esc(BY_SLUG[r]["name"])}</a></li>'
        for r in p["related"] if r in BY_SLUG) + "</ul>")
    o.append(f'<p><a href="{BASE}{HUB}"><strong>All billing platforms &rarr;</strong></a> '
             f'&nbsp;·&nbsp; Already integrated: '
             f'<a href="{BASE}/integrations/stripe">Stripe</a>, '
             f'<a href="{BASE}/integrations/chartmogul">ChartMogul</a>, '
             f'<a href="{BASE}/integrations/profitwell">ProfitWell</a>, '
             f'<a href="{BASE}/integrations/quickbooks">QuickBooks</a>.</p>')

    return "\n".join(o)


def main() -> None:
    for p in PLATFORMS:
        body = build_body(p)
        page = render(
            url_path=f"{HUB}/{p['slug']}",
            title=p["title"],
            description=p["description"],
            h1=p["h1"],
            lead=p["lead"],
            body=body,
            faqs=p["faqs"],
            hub_name=HUB_NAME,
            hub_path=HUB,
            breadcrumb_name=f"{p['name']} export",
        )
        write(f"export/{p['slug']}", page)

    rows = [[f'<a href="{BASE}{HUB}/{p["slug"]}">{esc(p["name"])}</a>',
             p["gotchas"][0][0]] for p in PLATFORMS]
    hub_body = "\n".join([
        f'<p><strong>TL;DR:</strong> Fourteen billing platforms, the seven fields a churn '
        f'analysis needs from each, and the platform-specific status traps that silently '
        f'produce wrong answers. Four more are covered under '
        f'<a href="{BASE}/integrations/stripe">integrations</a>.</p>',
        "<h2>The seven fields, on every platform</h2>",
        "<p>Every churn, retention and revenue-quality calculation reduces to these. The "
        "platform pages map each one to that system's own field names.</p>",
        "<ul>" + "".join(f"<li><strong>{n}.</strong> {d}</li>" for n, d in NEEDED) + "</ul>",
        "<h2>By platform</h2>",
        "<p>The second column is the trap that most often produces a wrong answer on that "
        "platform. Almost all of them are status values that do not mean what they sound "
        "like.</p>",
        table(["Platform", "Most common silent error"], rows),
        "<h2>Already covered elsewhere on this site</h2>",
        f'<ul><li><a href="{BASE}/integrations/stripe">Stripe</a> and '
        f'<a href="{BASE}/integrations/stripe-analytics">Stripe analytics</a></li>'
        f'<li><a href="{BASE}/integrations/chartmogul">ChartMogul</a></li>'
        f'<li><a href="{BASE}/integrations/profitwell">ProfitWell</a> and '
        f'<a href="{BASE}/integrations/profitwell-api">the ProfitWell API</a></li>'
        f'<li><a href="{BASE}/integrations/quickbooks">QuickBooks</a></li></ul>',
        "<h2>Four sanity checks before you trust any export</h2>",
        "<p>These catch the majority of unusable files in about five minutes, whatever "
        "platform produced them.</p>",
        "<ol>"
        "<li><strong>Does any row have a cancellation or end date?</strong> If none do across "
        "a multi-year file, the export was filtered to active subscriptions and every churn "
        "figure computed from it will be zero. This single defect accounts for more wrong "
        "churn numbers than every definitional argument combined, and it is fixed with one "
        "email rather than with analysis.</li>"
        "<li><strong>Does the row count match what the seller says?</strong> Fewer rows than "
        "the stated customer count means the file is filtered. More rows usually means one "
        "customer holds several subscriptions, which changes how you aggregate before you "
        "count anything.</li>"
        "<li><strong>Does summed normalised monthly revenue match reported MRR?</strong> "
        "Normalise annual amounts to monthly first. A gap beyond a few percent means a "
        "missing component, a currency issue or a different definition &mdash; find out which "
        "before you continue, because everything downstream inherits it.</li>"
        "<li><strong>Is the history long enough?</strong> Twenty-four months is the minimum "
        "for cohort work and thirty-six is better. Seasonality and renewal behaviour are "
        "untestable below that, and it is far easier to ask for more now than to re-open the "
        "request later.</li>"
        "</ol>",
        f'<p>Related: <a href="{BASE}/seller-claims">what sellers say and how to verify it</a>, '
        f'<a href="{BASE}/saas-due-diligence-checklist">the 23-point checklist</a>, and the '
        f'<a href="{BASE}/calculators">free calculators</a>.</p>',
    ])
    hub = render(
        url_path=HUB,
        title="Export Subscription Data for Churn Analysis: 14 Billing Platforms | ChurnLens",
        description="How to get a churn-analysable subscription export out of Paddle, Chargebee, Recurly, Maxio, Braintree, PayPal, Lemon Squeezy, Gumroad, Freemius, RevenueCat, WooCommerce, GoCardless, FastSpring and Zuora — with the status traps on each.",
        h1="Getting a churn-analysable export out of any billing platform",
        lead="Every churn calculation needs the same seven fields. What changes between platforms is where those fields live and which status values lie to you. This is the mapping for fourteen billing systems, plus the four already covered under integrations.",
        body=hub_body,
        faqs=[
            ("What data do you need to calculate SaaS churn?",
             "Seven fields: a stable customer identifier, subscription status, recurring amount and currency, billing interval and term, start date, cancellation or end date, and ideally the date of the last successful payment. Everything else is optional. Without a cancellation date you cannot compute churn at all."),
            ("Why do churn numbers differ between billing platforms?",
             "Mostly because status vocabularies differ and rarely mean what they sound like. Recurly's canceled is still serving while expired is gone; Chargebee's non_renewing is economically churned but counted as active; WooCommerce's pending-cancel is a decision already made. Reading any of these literally produces a wrong rate."),
            ("What is the most common problem with a subscription export?",
             "It was filtered to active subscriptions only, so it contains no cancellation dates and every churn figure computed from it comes out at zero. Count the rows with a cancellation or end date before you do anything else, and request a complete file if there are none."),
        ],
        hub_name="Home",
        hub_path="/",
        breadcrumb_name="Billing Exports",
    )
    write("export", hub)
    print(f"export: wrote {len(PLATFORMS)} pages + hub")


if __name__ == "__main__":
    main()
