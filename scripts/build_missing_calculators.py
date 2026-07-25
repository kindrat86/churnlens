#!/usr/bin/env python3
"""Give /free/ltv-calculator and /free/mrr-health-check the calculators they promise.

Both pages tell the visitor "Enter your details below — no signup required" and
"Get instant results calculated in real-time", and neither contains a single
form control. They are prose wearing a tool's clothes.

Rather than relabel them as guides, this builds the tools. The maths is the
same as the open-source library at github.com/kindrat86/saas-metrics, so a
result here can be reproduced independently.

Styling note: these two pages render on a light background while the other
calculators are dark, and this site's theme layer overrides `body` but not
every descendant. So the widget uses explicit colours on its own surface and
inherits nothing — it reads correctly whichever way the page is themed.

Idempotent via the cl-calc-v1 marker.
"""

import pathlib
import re

MARKER = "<!-- cl-calc-v1 -->"
ROOT = pathlib.Path(__file__).resolve().parent.parent

CSS = """<style>
/* Self-contained: explicit colours, nothing inherited from the page theme. */
.cl-calc{background:#f8fafc;border:1px solid #cbd5e1;border-radius:12px;padding:22px;margin:22px 0;
  color:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
.cl-calc .cl-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:18px}
@media(max-width:600px){.cl-calc .cl-grid{grid-template-columns:1fr}}
.cl-calc label{display:block;font-size:.74rem;color:#475569;margin-bottom:5px;font-weight:700;
  text-transform:uppercase;letter-spacing:.5px}
.cl-calc label .hint{text-transform:none;letter-spacing:0;font-weight:500;color:#64748b}
.cl-calc input{width:100%;background:#fff;border:1px solid #cbd5e1;color:#0f172a;padding:10px 12px;
  border-radius:8px;font-size:1rem;outline:none;box-sizing:border-box}
.cl-calc input:focus{border-color:#4f46e5}
.cl-calc .cl-hero{text-align:center;padding:24px 16px;border-radius:10px;border:2px solid #cbd5e1;
  background:#fff;margin-bottom:16px}
.cl-calc .cl-hero.good{border-color:#15803d;background:#f0fdf4}
.cl-calc .cl-hero.avg{border-color:#a16207;background:#fefce8}
.cl-calc .cl-hero.poor{border-color:#b91c1c;background:#fef2f2}
.cl-calc .cl-hero .cl-lab{font-size:.75rem;color:#475569;text-transform:uppercase;letter-spacing:1px;font-weight:700}
.cl-calc .cl-hero .cl-val{font-size:2.6rem;font-weight:800;margin:6px 0;color:#0f172a}
.cl-calc .cl-hero.good .cl-val{color:#15803d}
.cl-calc .cl-hero.avg .cl-val{color:#a16207}
.cl-calc .cl-hero.poor .cl-val{color:#b91c1c}
.cl-calc .cl-hero .cl-sub{font-size:.92rem;font-weight:600;color:#334155}
.cl-calc .cl-rows{display:grid;grid-template-columns:1fr 1fr;gap:10px}
@media(max-width:600px){.cl-calc .cl-rows{grid-template-columns:1fr}}
.cl-calc .cl-row{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:12px}
.cl-calc .cl-row .k{font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.5px;font-weight:700}
.cl-calc .cl-row .v{font-size:1.25rem;font-weight:700;color:#0f172a;margin-top:3px}
.cl-calc .cl-row .n{font-size:.78rem;color:#475569;margin-top:3px}
.cl-calc .cl-note{margin-top:14px;font-size:.82rem;color:#475569;line-height:1.55}
.cl-calc .cl-note a{color:#4338ca}
.cl-calc .cl-formula{background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 12px;
  font:.78rem/1.5 'SF Mono','Fira Code',Consolas,monospace;color:#334155;margin-bottom:16px;overflow-x:auto}
</style>"""

LTV_HTML = """__MARKER__
__CSS__
<div class="cl-calc" id="clLtv">
  <div class="cl-formula">LTV = ARPA &times; gross margin &times; (1 &divide; monthly churn rate)</div>
  <div class="cl-grid">
    <div><label for="ltvArpa">ARPA ($ / month) <span class="hint">avg revenue per account</span></label>
      <input id="ltvArpa" type="number" min="0" step="any" value="200"></div>
    <div><label for="ltvChurn">Monthly churn rate (%)</label>
      <input id="ltvChurn" type="number" min="0" max="100" step="any" value="2"></div>
    <div><label for="ltvMargin">Gross margin (%) <span class="hint">omit and you get lifetime revenue</span></label>
      <input id="ltvMargin" type="number" min="0" max="100" step="any" value="80"></div>
    <div><label for="ltvCac">CAC ($) <span class="hint">optional</span></label>
      <input id="ltvCac" type="number" min="0" step="any" value="2000"></div>
  </div>
  <div class="cl-hero" id="ltvHero">
    <div class="cl-lab">Customer lifetime value</div>
    <div class="cl-val" id="ltvValue">&mdash;</div>
    <div class="cl-sub" id="ltvVerdict">Enter your numbers above.</div>
  </div>
  <div class="cl-rows">
    <div class="cl-row"><div class="k">Expected lifetime</div><div class="v" id="ltvLife">&mdash;</div>
      <div class="n">1 &divide; monthly churn</div></div>
    <div class="cl-row"><div class="k">LTV : CAC</div><div class="v" id="ltvRatio">&mdash;</div>
      <div class="n">3:1 is the common rule of thumb</div></div>
    <div class="cl-row"><div class="k">CAC payback</div><div class="v" id="ltvPayback">&mdash;</div>
      <div class="n">months of gross profit</div></div>
    <div class="cl-row"><div class="k">Lifetime revenue</div><div class="v" id="ltvGross">&mdash;</div>
      <div class="n">before gross margin</div></div>
  </div>
  <p class="cl-note"><strong>A caution on lifetime.</strong> 1 &divide; churn assumes churn stays constant
  forever. Real cohorts churn hardest early and then flatten, so treat this as a ceiling rather than a
  forecast. The same maths is open source at <a href="/open-source">saas-metrics</a>.</p>
</div>
<script>
(function(){
  var ids=['ltvArpa','ltvChurn','ltvMargin','ltvCac'];
  function money(n){return '$'+Math.round(n).toLocaleString('en-US');}
  function calc(){
    var arpa=parseFloat(document.getElementById('ltvArpa').value);
    var churn=parseFloat(document.getElementById('ltvChurn').value);
    var margin=parseFloat(document.getElementById('ltvMargin').value);
    var cac=parseFloat(document.getElementById('ltvCac').value);
    var hero=document.getElementById('ltvHero');
    hero.classList.remove('good','avg','poor');
    if(!(arpa>0)||!(churn>0)){
      document.getElementById('ltvValue').innerHTML='&mdash;';
      document.getElementById('ltvVerdict').textContent=
        churn===0?'Zero churn implies an infinite lifetime — enter a real churn rate.':'Enter ARPA and a monthly churn rate above 0.';
      ['ltvLife','ltvRatio','ltvPayback','ltvGross'].forEach(function(i){document.getElementById(i).innerHTML='&mdash;';});
      return;
    }
    if(!(margin>=0&&margin<=100))margin=100;
    var life=100/churn;
    var grossRev=arpa*life;
    var ltv=grossRev*(margin/100);
    document.getElementById('ltvValue').textContent=money(ltv);
    document.getElementById('ltvLife').textContent=life.toFixed(1)+' months';
    document.getElementById('ltvGross').textContent=money(grossRev);
    if(cac>0){
      var ratio=ltv/cac;
      var payback=cac/(arpa*(margin/100));
      document.getElementById('ltvRatio').textContent=ratio.toFixed(2)+' : 1';
      document.getElementById('ltvPayback').textContent=payback.toFixed(1)+' months';
      hero.classList.add(ratio>=3?'good':ratio>=1?'avg':'poor');
      document.getElementById('ltvVerdict').textContent=
        ratio>=3?'At or above the 3:1 rule of thumb.':
        ratio>=1?'Below 3:1, but still recovering acquisition cost.':
        'Below 1:1 — every customer acquired loses money.';
    } else {
      document.getElementById('ltvRatio').innerHTML='&mdash;';
      document.getElementById('ltvPayback').innerHTML='&mdash;';
      document.getElementById('ltvVerdict').textContent=
        margin===100?'This is lifetime REVENUE — add your gross margin for lifetime value.':'Add a CAC to see the ratio and payback.';
    }
  }
  ids.forEach(function(i){var el=document.getElementById(i);if(el)el.addEventListener('input',calc);});
  calc();
})();
</script>"""

MRR_HTML = """__MARKER__
__CSS__
<div class="cl-calc" id="clMrr">
  <div class="cl-formula">NRR = (start + expansion &minus; contraction &minus; churned) &divide; start &nbsp;&bull;&nbsp; GRR excludes expansion</div>
  <div class="cl-grid">
    <div><label for="mrrStart">Starting MRR ($)</label>
      <input id="mrrStart" type="number" min="0" step="any" value="100000"></div>
    <div><label for="mrrExp">Expansion MRR ($) <span class="hint">upgrades, existing customers</span></label>
      <input id="mrrExp" type="number" min="0" step="any" value="12000"></div>
    <div><label for="mrrCon">Contraction MRR ($) <span class="hint">downgrades</span></label>
      <input id="mrrCon" type="number" min="0" step="any" value="4000"></div>
    <div><label for="mrrChurn">Churned MRR ($) <span class="hint">cancellations</span></label>
      <input id="mrrChurn" type="number" min="0" step="any" value="9000"></div>
    <div><label for="mrrTop">Largest customer share (%)</label>
      <input id="mrrTop" type="number" min="0" max="100" step="any" value="12"></div>
    <div><label for="mrrAnnual">Revenue on annual plans (%)</label>
      <input id="mrrAnnual" type="number" min="0" max="100" step="any" value="40"></div>
  </div>
  <div class="cl-hero" id="mrrHero">
    <div class="cl-lab">MRR quality score</div>
    <div class="cl-val" id="mrrScore">&mdash;</div>
    <div class="cl-sub" id="mrrVerdict">Enter your numbers above.</div>
  </div>
  <div class="cl-rows">
    <div class="cl-row"><div class="k">Net revenue retention</div><div class="v" id="mrrNrr">&mdash;</div>
      <div class="n">expansion counted</div></div>
    <div class="cl-row"><div class="k">Gross revenue retention</div><div class="v" id="mrrGrr">&mdash;</div>
      <div class="n">expansion excluded</div></div>
    <div class="cl-row"><div class="k">Masked by expansion</div><div class="v" id="mrrSpread">&mdash;</div>
      <div class="n">NRR &minus; GRR, in points</div></div>
    <div class="cl-row"><div class="k">Concentration</div><div class="v" id="mrrConc">&mdash;</div>
      <div class="n">largest single account</div></div>
  </div>
  <p class="cl-note" id="mrrNote"></p>
</div>
<script>
(function(){
  var ids=['mrrStart','mrrExp','mrrCon','mrrChurn','mrrTop','mrrAnnual'];
  function num(id){return parseFloat(document.getElementById(id).value);}
  function clamp(v,a,b){return Math.max(a,Math.min(v,b));}
  function calc(){
    var start=num('mrrStart'),exp=num('mrrExp'),con=num('mrrCon'),ch=num('mrrChurn');
    var top=num('mrrTop'),annual=num('mrrAnnual');
    var hero=document.getElementById('mrrHero');
    hero.classList.remove('good','avg','poor');
    if(!(start>0)){
      document.getElementById('mrrScore').innerHTML='&mdash;';
      document.getElementById('mrrVerdict').textContent='Enter a starting MRR above 0.';
      ['mrrNrr','mrrGrr','mrrSpread','mrrConc'].forEach(function(i){document.getElementById(i).innerHTML='&mdash;';});
      document.getElementById('mrrNote').textContent='';
      return;
    }
    exp=exp>0?exp:0;con=con>0?con:0;ch=ch>0?ch:0;
    top=isNaN(top)?0:clamp(top,0,100);annual=isNaN(annual)?0:clamp(annual,0,100);
    var nrr=((start+exp-con-ch)/start)*100;
    var grr=((start-con-ch)/start)*100;
    var spread=nrr-grr;
    var revChurn=100-grr;
    document.getElementById('mrrNrr').textContent=nrr.toFixed(1)+'%';
    document.getElementById('mrrGrr').textContent=grr.toFixed(1)+'%';
    document.getElementById('mrrSpread').textContent=spread.toFixed(1)+' pts';
    document.getElementById('mrrConc').textContent=top.toFixed(1)+'%';
    /* Three dimensions of MRR quality, each 0-100, averaged unweighted —
       the same mapping the ChurnLens health score uses. */
    var retention=Math.round(100-clamp(revChurn,0,10)*10);
    var growth=nrr>=130?100:nrr>=90?Math.round(40+(nrr-90)*1.5):Math.round(Math.max(0,nrr*0.5));
    growth=clamp(growth,0,100);
    var conc=Math.round(100-clamp(top,0,50)*2);
    var dur=Math.round(40+annual*0.6);
    var score=Math.round((retention+growth+conc+dur)/4);
    document.getElementById('mrrScore').textContent=score+' / 100';
    hero.classList.add(score>=70?'good':score>=50?'avg':'poor');
    document.getElementById('mrrVerdict').textContent=
      score>=70?'Strong — recurring revenue looks durable.':
      score>=50?'Adequate — one or two dimensions need work.':
      score>=30?'Weak — material revenue-quality risk.':'Critical — revenue quality is the headline problem.';
    var weak=[['retention',retention],['growth',growth],['concentration',conc],['durability',dur]]
      .sort(function(a,b){return a[1]-b[1];})[0];
    var note='Weakest dimension: <strong>'+weak[0]+'</strong> at '+weak[1]+'/100. ';
    if(spread>=15)note+='A '+spread.toFixed(0)+'-point gap between NRR and GRR means expansion revenue is masking substantial churn underneath — look at the retained base separately from upsell. ';
    if(top>25)note+='One customer holds '+top.toFixed(0)+'% of revenue; losing them removes that much overnight. ';
    note+='Same maths, open source, at <a href="/open-source">saas-metrics</a>.';
    document.getElementById('mrrNote').innerHTML=note;
  }
  ids.forEach(function(i){var el=document.getElementById(i);if(el)el.addEventListener('input',calc);});
  calc();
})();
</script>"""


def render(tpl: str) -> str:
    return tpl.replace("__MARKER__", MARKER).replace("__CSS__", CSS)


def insert(path: pathlib.Path, block: str) -> str:
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        return "skip (already built)"

    # Sit directly beneath the intro paragraph, above "How It Works" — which is
    # the copy telling the reader to enter their details.
    m = re.search(r"<h2[^>]*>\s*Free [^<]*</h2>", html)
    if m:
        # Skip the short blurb that follows that heading.
        after = html.find("</p>", m.end())
        pos = after + 4 if after != -1 else m.end()
    else:
        m = re.search(r"</h1>", html)
        if not m:
            return "SKIP (no anchor)"
        pos = m.end()

    path.write_text(html[:pos] + "\n" + block + "\n" + html[pos:], encoding="utf-8")
    return "built"


def main() -> int:
    jobs = [
        ("free/ltv-calculator/index.html", render(LTV_HTML)),
        ("free/mrr-health-check/index.html", render(MRR_HTML)),
    ]
    for rel, block in jobs:
        p = ROOT / rel
        if not p.is_file():
            print("%-42s MISSING" % rel)
            continue
        print("%-42s %s" % (rel, insert(p, block)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
