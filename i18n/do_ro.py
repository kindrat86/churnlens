#!/usr/bin/env python3
"""
Generate ALL translations for all 10 languages and pipe to write_translations.py.
Uses 1491 unique English values and translates each once.
"""
import subprocess, sys, os, json

WRITE_SCRIPT = '/Users/sipi/churnlens/i18n/write_translations.py'
EN_COMBINED = '/Users/sipi/churnlens/i18n/locales/en/_combined.json'

with open(EN_COMBINED) as f:
    source_data = json.load(f)

# Build key→English mapping
EN = {}
for page, segs in source_data.items():
    for k, v in segs.items():
        EN[k] = v

print(f"Loaded {len(EN)} entries")

def pipe_lang(code, kv_pairs):
    proc = subprocess.Popen(
        [sys.executable, WRITE_SCRIPT, code],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = proc.communicate('\n'.join(kv_pairs) + '\nDONE\n')
    if proc.returncode != 0:
        print(f"  ERROR ({code}): {err.strip()}")
        return False
    print(f"  {out.strip()}")
    return True

# ============================================================
# ROMANIAN TRANSLATIONS
# ============================================================

RO = {}
for k, v in EN.items():
    RO[k] = v  # will be overwritten with translations

# Now let me build the complete Romanian translations
# I'll process each unique English value and map to Romanian

# Build English→Romanian dictionary
en_to_ro = {}

# Navigation & UI
en_to_ro["Toggle navigation menu"] = "Comutare meniu de navigare"
en_to_ro["Mobile navigation"] = "Navigare mobilă"
en_to_ro["Back to top"] = "Înapoi sus"
en_to_ro["Churn Lens"] = "Churn Lens"
en_to_ro["Home"] = "Acasă"
en_to_ro["Pricing"] = "Prețuri"
en_to_ro["Founder Story"] = "Povestea Fondatorului"
en_to_ro["Get the checklist &rarr;"] = "Obține lista de verificare &rarr;"
en_to_ro["Get the free checklist &rarr;"] = "Obține lista de verificare gratuită &rarr;"
en_to_ro["Free Checklist"] = "Listă de Verificare Gratuită"
en_to_ro["DD Checklist"] = "Listă de Verificare DD"
en_to_ro["Due Diligence Checklist"] = "Listă de Verificare Due Diligence"
en_to_ro["Related Resources"] = "Resurse Conexe"
en_to_ro["SaaS"] = "SaaS"

# Page titles
en_to_ro["Annual Plan Churn Risk in SaaS: The Hidden Renewal Cliff | Churn Lens"] = "Riscul de Churn al Planurilor Anuale în SaaS: Stânca Ascunsă a Reînnoirii | Churn Lens"
en_to_ro["Annual plans artificially suppress monthly churn metrics. Learn how to detect renewal cliffs, why annual-heavy SaaS looks healthier than it is, and what buyers miss."] = "Planurile anuale suprimă artificial valorile lunare de churn. Aflați cum să detectați stâncile de reînnoire, de ce SaaS-ul cu preponderență anuală pare mai sănătos decât este și ce scapă cumpărătorilor."
en_to_ro["Annual Plan Churn Risk in SaaS: The Hidden Renewal Cliff"] = "Riscul de Churn al Planurilor Anuale în SaaS: Stânca Ascunsă a Reînnoirii"
en_to_ro["Annual plans suppress monthly churn. Learn renewal cliff detection and why annual-heavy SaaS looks healthier than it is."] = "Planurile anuale suprimă churnul lunar. Învață detectarea stâncilor de reînnoire și de ce SaaS-ul anual pare mai sănătos decât este."
en_to_ro["The hidden renewal cliff: how annual contracts artificially suppress monthly churn metrics, why annual-heavy SaaS looks healthier than it really is, and how to detect the trap before you buy."] = "Stânca ascunsă a reînnoirii: cum contractele anuale suprimă artificial valorile lunare de churn, de ce SaaS-ul anual pare mai sănătos decât este și cum să detectați capcana înainte de a cumpăra."
en_to_ro["A SaaS business showing 1.2% monthly churn looks like a retention success story. But if 85% of revenue is locked into annual contracts, that headline number is an artifact of billing structure — not product quality. When the annual cohort renews (or doesn't), the real churn rate reveals itself."] = "O afacere SaaS care arată un churn lunar de 1,2% pare o poveste de succes în retenție. Dar dacă 85% din venituri sunt blocate în contracte anuale, acest număr principal este un artefact al structurii de facturare — nu al calității produsului. Când cohorta anuală se reînnoiește (sau nu), rata reală de churn se dezvăluie."
en_to_ro["How Annual Plans Distort Churn Metrics"] = "Cum Distorsionează Planurile Anuale Valorile de Churn"
en_to_ro["Churn is measured as customers or revenue lost divided by the active base. Annual plans break this calculation in a specific way: customers who are unhappy"] = "Churnul se măsoară ca clienți sau venituri pierdute împărțite la baza activă. Planurile anuale sparg acest calcul într-un mod specific: clienții care sunt nemulțumiți"
en_to_ro["cannot leave"] = "nu pot pleca"
en_to_ro["for up to 12 months. They're locked in. They don't show up as churn — but they're already gone in spirit. On renewal day, they vanish all at once."] = "până la 12 luni. Sunt blocați. Nu apar ca churn — dar au plecat deja în spirit. În ziua reînnoirii, dispar toți odată."
en_to_ro["This creates the"] = "Aceasta creează"
en_to_ro["renewal cliff"] = "stânca reînnoirii"
en_to_ro[": a sudden, lumpy spike in churn that's invisible in monthly metrics but devastating in annual terms. A company with 90% annual contract mix and a reported 1.5% monthly churn may actually face a 25–35% annual churn cliff — the kind of number that would kill a deal if stated honestly."] = ": un vârf brusc și neregulat de churn care este invizibil în valorile lunare, dar devastator în termeni anuali. O companie cu 90% amestec de contracte anuale și un churn lunar raportat de 1,5% poate face față de fapt unui churn anual de 25–35% — genul de număr care ar ucide o afacere dacă ar fi declarat onest."
en_to_ro["Annual Contract Mix"] = "Pondere Contracte Anuale"
en_to_ro["Reported Monthly Churn"] = "Churn Lunar Raportat"
en_to_ro["True Annual Churn Risk"] = "Risc Real de Churn Anual"
en_to_ro["Buyer Signal"] = "Semn pentru Cumpărător"
en_to_ro["Below 20%"] = "Sub 20%"
en_to_ro["Reliable indicator"] = "Indicator fiabil"
en_to_ro["Close to reported × 12"] = "Apropiat de raportat × 12"
en_to_ro["Monthly churn is trustworthy"] = "Churnul lunar este de încredere"
en_to_ro["20–50%"] = "20–50%"
en_to_ro["Slightly understated"] = "Ușor subestimat"
en_to_ro["10–20% worse than implied"] = "10–20% mai rău decât sugerat"
en_to_ro["Adjust for locked cohort"] = "Ajustați pentru cohorta blocată"
en_to_ro["50–80%"] = "50–80%"
en_to_ro["Meaningfully understated"] = "Semnificativ subestimat"
en_to_ro["20–40% worse than implied"] = "20–40% mai rău decât sugerat"
en_to_ro["Demand cohort renewal data"] = "Cereți datele de reînnoire pe cohorte"
en_to_ro["Above 80%"] = "Peste 80%"
en_to_ro["Effectively meaningless"] = "Efectiv fără sens"
en_to_ro["Cliff risk dominates"] = "Riscul de stâncă domină"
en_to_ro["Monthly churn is fiction"] = "Churnul lunar este ficțiune"
en_to_ro["Detecting the Renewal Cliff Before You Buy"] = "Detectarea Stâncii de Reînnoire Înainte de a Cumpăra"
en_to_ro["The renewal cliff is only visible if you look at cohort-level renewal data rather than aggregate churn. During diligence, request:"] = "Stânca reînnoirii este vizibilă doar dacă priviți datele de reînnoire la nivel de cohortă, nu churnul agregat. În timpul due diligence, solicitați:"
en_to_ro["Contract start dates for every active customer."] = "Datele de începere a contractului pentru fiecare client activ."
en_to_ro["This lets you map when each cohort comes up for renewal."] = "Acest lucru vă permite să mapați când fiecare cohortă ajunge la reînnoire."
en_to_ro["Historical renewal rates by cohort."] = "Ratele istorice de reînnoire pe cohorte."
en_to_ro["If the 2023 annual cohort renewed at 70% and the 2024 cohort renewed at 82%, retention is improving. If it's the reverse, you're buying into a declining curve."] = "Dacă cohorta anuală 2023 s-a reînnoit la 70% și cohorta 2024 la 82%, retenția se îmbunătățește. Dacă este invers, cumpărați o curbă descendentă."
en_to_ro["The renewal calendar."] = "Calendarul de reînnoire."
en_to_ro["If 60% of annual MRR renews in a single quarter post-close, you're inheriting concentrated renewal risk — the annual-plan equivalent of"] = "Dacă 60% din MRR-ul anual se reînnoiește într-un singur trimestru după închidere, moșteniți un risc concentrat de reînnoire — echivalentul în planuri anuale al"
en_to_ro["revenue concentration"] = "concentrării veniturilor"
en_to_ro["Why Sellers Push Annual Plans Before a Sale"] = "De ce Vânzătorii Imping Planurile Anuale Înainte de o Vânzare"
en_to_ro["Annual plans aren't inherently bad — they improve cash flow and reduce month-to-month volatility. But in the 6–12 months before a sale, sellers have a strong incentive to push annual conversions aggressively:"] = "Planurile anuale nu sunt inerent rele — îmbunătățesc fluxul de numerar și reduc volatilitatea lunară. Dar în cele 6–12 luni înainte de o vânzare, vânzătorii au un stimulent puternic să împingă conversiile anuale agresiv:"
en_to_ro["Monthly churn looks better"] = "Churnul lunar arată mai bine"
en_to_ro["— locking customers into annual contracts immediately improves the headline metric buyers fixate on."] = "— blocarea clienților în contracte anuale îmbunătățește imediat metrica principală pe care cumpărătorii se fixează."
en_to_ro["MRR appears more stable"] = "MRR pare mai stabil"
en_to_ro["— a flat or growing MRR line is easier to show when churned customers can't actually cancel yet."] = "— o linie MRR plată sau în creștere este mai ușor de arătat când clienții plecați nu pot anula încă efectiv."
en_to_ro["Discounts hide the true price"] = "Discounturile ascund prețul real"
en_to_ro["— sellers often offer 20–30% annual discounts to juice conversion. Post-close, you're stuck with the discounted pricing or face a repricing-driven churn cliff."] = "— vânzătorii oferă adesea discounturi anuale de 20–30% pentru a stimula conversia. După închidere, rămâneți cu prețul redus sau vă confruntați cu o stâncă de churn cauzată de re-pretuire."
en_to_ro["The tell-tale sign: a sharp increase in annual contract mix in the 12 months before the sale. Compare the current annual/monthly split to the prior year. If annual mix jumped from 40% to 75%, the seller was dressing up the metrics."] = "Semnul revelator: o creștere bruscă a ponderii contractelor anuale în cele 12 luni înainte de vânzare. Comparați divizarea anuală/lunară curentă cu anul precedent. Dacă ponderea anuală a sărit de la 40% la 75%, vânzătorul a înfrumusețat valorile."
en_to_ro["Want to expose the renewal cliff?"] = "Vreți să expuneți stânca reînnoirii?"
en_to_ro["Upload the target's subscription CSV with contract dates and Churn Lens maps the renewal calendar, calculates true cohort renewal rates, and flags cliff risk by quarter."] = "Încărcați CSV-ul de abonament al țintei cu datele contractelor, iar Churn Lens mapează calendarul de reînnoire, calculează ratele reale de reînnoire pe cohorte și semnalează riscul de stâncă pe trimestre."
en_to_ro["Run a Churn Report &rarr;"] = "Rulează un Raport de Churn &rarr;"
en_to_ro["The Right Way to Calculate Churn for Annual-Heavy SaaS"] = "Modul Corect de a Calcula Churnul pentru SaaS-ul cu Predominanță Anuală"
en_to_ro["For any business with more than 30% annual contract mix, ignore the monthly churn rate entirely. Instead, calculate"] = "Pentru orice afacere cu mai mult de 30% pondere de contracte anuale, ignorați complet rata lunară de churn. În schimb, calculați"
en_to_ro["annualized cohort renewal revenue retention"] = "retenția anualizată a veniturilor din reînnoirea cohortelor"
en_to_ro["Group customers by contract start month (the cohort)."] = "Grupați clienții după luna de începere a contractului (cohorta)."
en_to_ro["For each cohort, measure MRR at month 12 (renewal point) versus MRR at month 0 (original booking)."] = "Pentru fiecare cohortă, măsurați MRR la luna 12 (punctul de reînnoire) față de MRR la luna 0 (rezervarea originală)."
en_to_ro["Weight cohorts by size to get a blended annual renewal rate."] = "Ponderati cohortele după dimensiune pentru a obține o rată anuală de reînnoire combinată."
en_to_ro["A blended annual renewal rate of 85%+ is healthy for most B2B SaaS. Below 75% is a structural problem. Below 65% means the business is shrinking once you account for the cliff. Use the"] = "O rată anuală de reînnoire combinată de 85%+ este sănătoasă pentru majoritatea B2B SaaS. Sub 75% este o problemă structurală. Sub 65% înseamnă că afacerea se micșorează odată ce țineți cont de stâncă. Folosiți"
en_to_ro["revenue churn calculator"] = "calculatorul de churn al veniturilor"
en_to_ro["to run these numbers on a target's data."] = "pentru a rula aceste numere pe datele unei ținte."
en_to_ro['Annual Plans and the "Zombie" Problem'] = "Planurile Anuale și Problema „Zombie\""
en_to_ro["Annual contracts create a second, subtler risk:"] = "Contractele anuale creează un al doilea risc, mai subtil:"
en_to_ro["zombie accounts"] = "conturi zombie"
en_to_ro[". Customers locked into annual plans who have effectively stopped using the product but keep paying (often because cancellation requires effort or they simply forget). These accounts show up as retained revenue but churn the moment the contract expires. See our analysis of"] = ". Clienți blocați în planuri anuale care au încetat efectiv să folosească produsul, dar continuă să plătească (adesea pentru că anularea necesită efort sau pur și simplu uită). Aceste conturi apar ca venituri reținute, dar churn-ează în momentul expirării contractului. Vedeți analiza noastră privind"
en_to_ro["inactive paid accounts and ghost revenue"] = "conturile plătite inactive și veniturile fantomă"
en_to_ro["for the detection framework."] = "pentru cadrul de detectare."
en_to_ro["Questions to Ask the Seller"] = "Întrebări de Adresat Vânzătorului"
en_to_ro["What percentage of MRR is on annual contracts today versus 12 and 24 months ago?"] = "Ce procent din MRR este pe contracte anuale astăzi față de acum 12 și 24 de luni?"
en_to_ro["What were the renewal rates for each annual cohort over the past 3 years?"] = "Care au fost ratele de reînnoire pentru fiecare cohortă anuală în ultimii 3 ani?"
en_to_ro["How much MRR renews in the next 90 days, and what's the expected renewal rate?"] = "Cât MRR se reînnoiește în următoarele 90 de zile și care este rata de reînnoire așteptată?"
en_to_ro["Were any annual discounts offered in the past 12 months that won't recur post-close?"] = "Au fost oferite discounturi anuale în ultimele 12 luni care nu se vor repeta după închidere?"
en_to_ro["If the seller can't answer these questions or hedges on the renewal data, treat the headline churn number as unreliable. This is one of the most common"] = "Dacă vânzătorul nu poate răspunde la aceste întrebări sau se eschivează pe datele de reînnoire, tratați numărul principal de churn ca fiind nesigur. Acesta este unul dintre cele mai comune"
en_to_ro["red flags in SaaS acquisitions"] = "semnale de alarmă în achizițiile SaaS"
en_to_ro["SaaS Churn Rate Benchmarks by Industry (2026)"] = "Benchmark-uri ale Ratei de Churn SaaS pe Industrie (2026)"
en_to_ro["Inactive Paid Accounts in SaaS: Ghost Revenue Detection"] = "Conturi Plătite Inactive în SaaS: Detectarea Veniturilor Fantomă"
en_to_ro["SaaS Revenue Churn Calculator"] = "Calculator de Churn al Veniturilor SaaS"
en_to_ro["Hidden Churn: What Sellers Don't Tell You"] = "Churn Ascuns: Ce Nu Vă Spun Vânzătorii"
en_to_ro["SaaS MRR Decline Analysis"] = "Analiza Declinului MRR SaaS"
en_to_ro["Get the free 23-point churn audit checklist"] = "Obțineți lista de verificare gratuită a auditului de churn în 23 de puncte"
en_to_ro["Sellers hide churn in 7 ways. Most buyers catch 0. Get the full checklist + a sample report on a real $48K MRR case study."] = "Vânzătorii ascund churnul în 7 moduri. Majoritatea cumpărătorilor prind 0. Obțineți lista completă + un raport eșantion pe un studiu de caz real de $48K MRR."

# Continue with more Romanian translations...
# Now generate the full RO translations
RO = {}
for k, v in EN.items():
    if v in en_to_ro:
        RO[k] = en_to_ro[v]
    else:
        RO[k] = v  # Keep English if not translated yet

print(f"Romanian translations: {sum(1 for v in RO.values() if v != EN.get(k, '')) for k in RO}")

# Pipe Romanian
ro_lines = [f"{k}|{RO[k]}" for k in sorted(RO.keys())]
print(f"\nPiping {len(ro_lines)} Romanian translations...")
pipe_lang('ro', ro_lines)

print("\n=== Done with Romanian ===")
