# Internal link-graph repair

Regenerates the site's internal link graph. **Run this LAST**, after any content
consolidation, page deletion or redirect change — the link graph is a *derived*
artifact, so running it before the page set is final bakes in links to pages that
are about to disappear.

## Order matters

```bash
cd ~/churnlens
python3 scripts/linkgraph/build_targets.py > /tmp/targets.txt   # indexable page set
python3 scripts/linkgraph/deadlinks.py --root . --apply         # 1. link hygiene
python3 scripts/linkgraph/ilg.py --root . --sitemap /tmp/targets.txt --apply
python3 scripts/linkgraph/rescue.py --root . --targets /tmp/targets.txt --apply
```

Run `ilg.py` until it reports `WROTE 0 files` (it converges in ~3 passes; each
pass sees the links the previous one added).

## What each pass does

| Script | Pass | Effect |
|---|---|---|
| `deadlinks.py` | link hygiene | Retargets links to their terminal `vercel.json` redirect destination (no hops), remaps same-entity slug variants, drops genuinely dead list items, unwraps dead prose links keeping their text. Never invents a destination. |
| `ilg.py` | A | Homepage "Explore ChurnLens" hub directory |
| | B | Each hub links all of its own children |
| | C | Each page gets a "Related" block: its hub + nearest siblings by title/H1/description token overlap, capped at 5 |
| | D | Replaces raw `foo.html` filename anchor text with real page titles |
| `rescue.py` | E | Surfaces any indexable page still holding zero inlinks (e.g. children whose hub was consolidated away) on the homepage |

## Safety properties

- **Idempotent.** Injected markup is wrapped in `<!-- ilg-v1 -->` / `<!-- ilg-rescue-v1 -->`
  and replaced, never appended. Re-running converges to a no-op.
- **Never adds or deletes files.** Verify with
  `git status --porcelain | grep -c '^??\|^ D'` → must be `0`.
- **Twin-aware.** Writes both `slug.html` and `slug/index.html` when both exist.
- **Excludes** `i18n/`, `i18n_out/`, `dist/`, `public/`, `.vercel/`, `assets/`, `scripts/`,
  plus utility, legal, widget and funnel-only pages (see `EXCLUDE_URLS`).

## Verifying a run

```bash
python3 scripts/linkgraph/audit.py     # orphans, median inlinks, dead links, redirect loops
```

Targets: **0 orphans**, **0 dead internal links**, **0 redirect loops**,
median inlinks **≥6**, and zero HTML parse failures.

## Known trap

`vercel.json` has previously been written with **self-referential redirects**
(`/alternatives-to/baremetrics` → itself) after a consolidation deleted the page
file. Deployed, those return infinite redirect loops on indexed URLs. `audit.py`
checks for this — treat a non-zero loop count as a release blocker.
