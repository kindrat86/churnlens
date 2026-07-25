#!/usr/bin/env python3
"""Orphan rescue: any indexable page still holding 0 contextual inlinks after
ilg.py runs gets surfaced in a 'More from ChurnLens' line inside the homepage
Explore block. Own marker, so it is idempotent and survives ilg re-runs."""
import os,re,html,json,argparse,collections
SKIP=("i18n","i18n_out","dist",".vercel","public","node_modules",".git","assets","scripts","schema","embed","widgets","api")
EXCLUDE={"/404","/thank-you","/oto","/badge","/related-tools","/network-widget","/network/widget",
"/striking-distance","/index","/affiliate","/affiliates","/masterclass","/dream100","/dream-100",
"/citations","/calculator","/free/embed-widget","/embed","/embed/tools/portfolio-network",
"/terms","/privacy","/contact","/partners","/walkthrough","/network"}
M0,M1="<!-- ilg-rescue-v1 -->","<!-- /ilg-rescue-v1 -->"
ap=argparse.ArgumentParser(); ap.add_argument("--root",required=True); ap.add_argument("--targets",required=True)
ap.add_argument("--apply",action="store_true"); a=ap.parse_args()
root=a.root.rstrip("/"); os.chdir(root)
tgt={l.strip() for l in open(a.targets) if l.strip()}
pages={}
for dp,dn,fn in os.walk("."):
    dn[:]=[d for d in dn if d not in SKIP and not d.startswith(".")]
    for f in fn:
        if not f.endswith(".html"): continue
        rel=os.path.relpath(os.path.join(dp,f),".")
        if any(p in SKIP for p in rel.split(os.sep)): continue
        u="/"+rel.replace(os.sep,"/"); u=u[:-11] if u.endswith("/index.html") else u[:-5]
        pages.setdefault(u or "/",[]).append(os.path.join(dp,f))
def ctx(h):
    b=re.sub(r'(?is)<nav.*?</nav>',' ',h); b=re.sub(r'(?is)<footer.*?</footer>',' ',b)
    o=set()
    for m in re.findall(r'href="(/[^"]*)"',b):
        t=m.split('#')[0].split('?')[0]
        t=t[:-5] if t.endswith('.html') else t
        t=t[:-6] if t.endswith('/index') else t
        t=t[:-1] if len(t)>1 and t.endswith('/') else t
        o.add(t or "/")
    return o
inl=collections.Counter(); titles={}
for u,fs in pages.items():
    h=open(fs[0],encoding='utf-8',errors='ignore').read()
    m=re.search(r"(?is)<title[^>]*>(.*?)</title>",h)
    t=html.unescape(re.sub(r"\s+"," ",m.group(1) if m else u)).strip()
    t=re.sub(r"\s*[|–—-]\s*Churn\s?Lens.*$","",t,flags=re.I).strip(" -–—|·") or u
    titles[u]=re.split(r"\s+[—–:|]\s+",t)[0][:52]
    for x in ctx(h): inl[x]+=1
orph=sorted(u for u in pages if u in tgt and u not in EXCLUDE and inl[u]==0)
print(f"orphans needing rescue: {len(orph)}")
for u in orph: print("   ",u)
if not orph: raise SystemExit
links=" · ".join(f'<a href="{u}">{html.escape(titles[u])}</a>' for u in orph)
blk=f'{M0}<p style="margin:.45rem 0"><strong>More from ChurnLens:</strong> {links}</p>{M1}'
hp=pages.get("/",[])
n=0
for fp in hp:
    h=open(fp,encoding='utf-8',errors='ignore').read()
    if re.search(re.escape(M0)+r".*?"+re.escape(M1),h,re.S):
        h=re.sub(re.escape(M0)+r".*?"+re.escape(M1),lambda _:blk,h,count=1,flags=re.S)
    elif "<!-- /ilg-v1 -->" in h:
        h=h.replace("</section>\n<!-- /ilg-v1 -->",blk+"\n</section>\n<!-- /ilg-v1 -->",1)
    else: continue
    if a.apply: open(fp,"w",encoding='utf-8').write(h); n+=1
print(f"homepage files updated: {n}")
