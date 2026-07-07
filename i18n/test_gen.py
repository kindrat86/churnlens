#!/usr/bin/env python3
import subprocess, sys

WRITE_SCRIPT = '/Users/sipi/churnlens/i18n/write_translations.py'

def pipe_lang(lang_code, kv_pairs):
    proc = subprocess.Popen(
        [sys.executable, WRITE_SCRIPT, lang_code],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = proc.communicate('
'.join(kv_pairs) + '
DONE
')
    print(err or out.strip())
    return proc.returncode == 0

TRANS = {
    '__TR_annual-plan-churn-risk_0__': '''Annual Plan Churn Risk in SaaS: The Hidden Renewal Cliff | Churn Lens''',
    '__TR_annual-plan-churn-risk_1__': '''Annual plans artificially suppress monthly churn metrics. Learn how to detect renewal cliffs, why annual-heavy SaaS looks healthier than it is, and what buyers miss.''',
    '__TR_annual-plan-churn-risk_2__': '''Annual Plan Churn Risk in SaaS: The Hidden Renewal Cliff''',
    '__TR_annual-plan-churn-risk_3__': '''Annual plans suppress monthly churn. Learn renewal cliff detection and why annual-heavy SaaS looks healthier than it is.''',
    '__TR_annual-plan-churn-risk_4__': '''Annual Plan Churn Risk in SaaS: The Hidden Renewal Cliff''',
    '__TR_annual-plan-churn-risk_5__': '''Annual plans suppress monthly churn. Learn renewal cliff detection and why annual-heavy SaaS looks healthier than it is.''',
    '__TR_annual-plan-churn-risk_6__': '''Toggle navigation menu''',
    '__TR_annual-plan-churn-risk_7__': '''Mobile navigation''',
    '__TR_annual-plan-churn-risk_8__': '''Back to top''',
    '__TR_annual-plan-churn-risk_9__': '''Churn Lens''',
    '__TR_annual-plan-churn-risk_10__': '''Home''',
    '__TR_annual-plan-churn-risk_11__': '''Pricing''',
    '__TR_annual-plan-churn-risk_12__': '''Founder Story''',
    '__TR_annual-plan-churn-risk_13__': '''Get the checklist &rarr;''',
    '__TR_annual-plan-churn-risk_14__': '''Get the free checklist &rarr;''',
    '__TR_annual-plan-churn-risk_15__': '''Annual Plan Churn Risk in SaaS''',
    '__TR_annual-plan-churn-risk_16__': '''The hidden renewal cliff: how annual contracts artificially suppress monthly churn metrics, why annual-heavy SaaS looks healthier than it really is, and how to detect the trap before you buy.''',
    '__TR_annual-plan-churn-risk_17__': '''A SaaS business showing 1.2% monthly churn looks like a retention success story. But if 85% of revenue is locked into annual contracts, that headline number is an artifact of billing structure — not product quality. When the annual cohort renews (or doesn\'t), the real churn rate reveals itself.''',
    '__TR_annual-plan-churn-risk_18__': '''How Annual Plans Distort Churn Metrics''',
    '__TR_annual-plan-churn-risk_19__': '''Churn is measured as customers or revenue lost divided by the active base. Annual plans break this calculation in a specific way: customers who are unhappy''',
    '__TR_annual-plan-churn-risk_20__': '''cannot leave''',
    '__TR_annual-plan-churn-risk_21__': '''for up to 12 months. They\'re locked in. They don\'t show up as churn — but they\'re already gone in spirit. On renewal day, they vanish all at once.''',
    '__TR_annual-plan-churn-risk_22__': '''This creates the''',
    '__TR_annual-plan-churn-risk_23__': '''renewal cliff''',
    '__TR_annual-plan-churn-risk_24__': ''': a sudden, lumpy spike in churn that\'s invisible in monthly metrics but devastating in annual terms. A company with 90% annual contract mix and a reported 1.5% monthly churn may actually face a 25–35% annual churn cliff — the kind of number that would kill a deal if stated honestly.''',
    '__TR_annual-plan-churn-risk_25__': '''Annual Contract Mix''',
    '__TR_annual-plan-churn-risk_26__': '''Reported Monthly Churn''',
    '__TR_annual-plan-churn-risk_27__': '''True Annual Churn Risk''',
    '__TR_annual-plan-churn-risk_28__': '''Buyer Signal''',
    '__TR_annual-plan-churn-risk_29__': '''Below 20%''',
    '__TR_annual-plan-churn-risk_30__': '''Reliable indicator''',
    '__TR_annual-plan-churn-risk_31__': '''Close to reported × 12''',
    '__TR_annual-plan-churn-risk_32__': '''Monthly churn is trustworthy''',
    '__TR_annual-plan-churn-risk_33__': '''20–50%''',
    '__TR_annual-plan-churn-risk_34__': '''Slightly understated''',
    '__TR_annual-plan-churn-risk_35__': '''10–20% worse than implied''',
    '__TR_annual-plan-churn-risk_36__': '''Adjust for locked cohort''',
    '__TR_annual-plan-churn-risk_37__': '''50–80%''',
    '__TR_annual-plan-churn-risk_38__': '''Meaningfully understated''',
    '__TR_annual-plan-churn-risk_39__': '''20–40% worse than implied''',
    '__TR_annual-plan-churn-risk_40__': '''Demand cohort renewal data''',
    '__TR_annual-plan-churn-risk_41__': '''Above 80%''',
    '__TR_annual-plan-churn-risk_42__': '''Effectively meaningless''',
    '__TR_annual-plan-churn-risk_43__': '''Cliff risk dominates''',
    '__TR_annual-plan-churn-risk_44__': '''Monthly churn is fiction''',
    '__TR_annual-plan-churn-risk_45__': '''Detecting the Renewal Cliff Before You Buy''',
    '__TR_annual-plan-churn-risk_46__': '''The renewal cliff is only visible if you look at cohort-level renewal data rather than aggregate churn. During diligence, request:''',
    '__TR_annual-plan-churn-risk_47__': '''Contract start dates for every active customer.''',
    '__TR_annual-plan-churn-risk_48__': '''This lets you map when each cohort comes up for renewal.''',
    '__TR_annual-plan-churn-risk_49__': '''Historical renewal rates by cohort.''',
}

# Generate translations
lines = []
for k, v in TRANS.items():
    lines.append(f'{k}|{v.replace(chr(10), \n)}')

print(f'Piping {len(lines)} translations...')
pipe_lang('ro', lines)
print('Done!')
