#!/usr/bin/env node
/**
 * Blocking JSON-LD gate on the SHIPPED output.
 *
 * Why this exists alongside scripts/validate_jsonld.py: that one runs at
 * checkout on committed source and skips build directories by design. The
 * corruption that actually reached Google — Search Console "Unparsable
 * structured data / Parsing error: Missing ',' or '}'" on voicelogpro.com,
 * 2026-07-25 — is introduced *between* the repo and the deployed page, by
 * the centrally generated pSEO pages and by build-time post-processors. A
 * source-only lint structurally cannot see that class of bug.
 *
 * Two distinct causes produced that one Search Console message:
 *
 *   "@context":"https://***@type":"WebPage"     <- `schema.org","` clobbered,
 *   "@context":"https://schema.org","@type":…      swallowing @type
 *
 *   "mainEntity":[…]`}                         <- leftover JS template-literal
 *   "mainEntity":[…]}                             backtick closing a FAQPage
 *
 * Both are checked by signature as well as by JSON.parse, because a repair
 * step with no verification after it is worse than no repair: it lets a new
 * variant of the corruption ship silently. Blocks that parse but whose
 * @context was corrupted are caught too, since JSON.parse waves those through.
 *
 * Node, not Python, on purpose: every deploy path runs the build (Vercel cloud
 * builds, and local `vercel build && vercel deploy --prebuilt` alike) and node
 * is guaranteed in all of them, while python3 is not.
 *
 * Self-contained by design — no cross-repo import, so it works in Vercel's
 * shallow clone. Keep the copies in the 10 site repos identical.
 *
 * Usage: node scripts/verify-jsonld.mjs [dir ...]      (default: dist)
 *   Exit 1 on any bad block, or if a named directory does not exist.
 *
 * See ~/.growth-engine/GUARDRAILS.md rule 3 for the portfolio-wide context and
 * ~/.growth-engine/validate-jsonld-live.py for the post-deploy live check.
 */
import { readdirSync, readFileSync, existsSync, statSync } from 'node:fs';
import { join, extname, resolve, relative } from 'node:path';

const dirs = process.argv.slice(2);
if (dirs.length === 0) dirs.push('dist');

// Directories that never contain shippable HTML. `assets` holds hashed bundles
// and is the bulk of a vite dist, so skipping it keeps this fast on large sites.
//
// dist/ i18n/ i18n_out/ are in this repo but are NOT served — all three are
// .vercelignored, so nothing under them can be requested. They are stale
// duplicate copies of the site; linting them reports failures on pages no
// crawler can reach. This mirrors SKIP_DIRS in
// scripts/dedupe_entity_graph.py — keep the two lists in step.
//
// public/ is deliberately NOT skipped. It was, briefly, on the grounds that
// `/public/:path*` redirects it away — but Vercel compiles route sources with
// path-to-regexp `strict: true`, so that source does not match a trailing
// slash. `/public/vs/` was served straight from disk, HTTP 200, with
// `robots: index, follow`, while `/public/vs` correctly 308'd. 77 files and
// 148 duplicate-entity errors sat behind that gap, unlinted and crawlable.
// vercel.json now carries a companion `/public/:path*/` source, and this
// directory stays linted so the gate does not depend on a routing rule being
// exactly right.
const SKIP = new Set([
  'node_modules', '.git', '.next', '.vercel', 'assets',
  '__pycache__', '.venv', 'venv', 'coverage',
  'dist', 'i18n', 'i18n_out',
]);

const BLOCK_RE =
  /<script[^>]*\btype\s*=\s*["']?application\/ld\+json["']?[^>]*>([\s\S]*?)<\/script>/gi;

const SIGNATURES = [
  {
    re: /https:\/\/\*{3}/,
    msg: 'clobbered @context (https://*** — expected https://schema.org)',
  },
  {
    re: /"@context"\s*:\s*"[^"]*@type/,
    msg: '@type swallowed into the @context string',
  },
  {
    re: /\]\s*`\s*\}/,
    msg: 'stray template-literal backtick closing the schema (]`} instead of ]})',
  },
];

// Entity nodes owned by the canonical @graph (scripts/inject_entity_graph.py).
// Duplicate definitions of these parse fine and validate fine — same-@id nodes
// merge — which is why this needed its own check: three generators had each
// injected their own #organization, and the merged result carried two different
// `offers` sets and three different `foundingDate` values. Contradictory
// structured data is not a parse error, so JSON.parse can never catch it.
const CANONICAL_IDS = new Set([
  'https://churnlens.site/#organization',
  'https://churnlens.site/#software',
  'https://churnlens.site/#website',
  'https://churnlens.site/#founder',
]);

// Properties the canonical @graph states. A node adding only *other* keys
// (e.g. {"@id": …/#organization, "isRelatedTo": […]}) is a legitimate merge and
// is not counted; only restatements can drift apart.
const CANONICAL_PROPS = new Set([
  'name', 'alternateName', 'url', 'description', 'disambiguatingDescription',
  'foundingDate', 'knowsAbout', 'sameAs', 'logo', 'image', 'contactPoint',
  'publisher', 'author', 'offers', 'featureList', 'applicationCategory',
  'operatingSystem', 'inLanguage', 'potentialAction',
]);

const TYPE_TO_ID = {
  Organization: 'https://churnlens.site/#organization',
  WebSite: 'https://churnlens.site/#website',
  SoftwareApplication: 'https://churnlens.site/#software',
};
const SITE_ROOT = 'https://churnlens.site';

/** The canonical @id a node defines, or null if it is not our entity. */
function canonicalIdOf(node) {
  if (!node || typeof node !== 'object' || Array.isArray(node)) return null;
  const id = node['@id'];
  if (typeof id === 'string') return CANONICAL_IDS.has(id) ? id : null;
  // No @id: ours only if it names the brand or points at the site root exactly.
  const type = node['@type'];
  if (typeof type !== 'string' || !(type in TYPE_TO_ID)) return null;
  const url = typeof node.url === 'string' ? node.url.replace(/\/+$/, '') : '';
  if (node.name === 'ChurnLens' || url === SITE_ROOT) return TYPE_TO_ID[type];
  return null;
}

function restatesCanonical(node) {
  return Object.keys(node).some((k) => CANONICAL_PROPS.has(k));
}

const errors = [];
let files = 0;
let blocks = 0;

function walk(dir) {
  let entries;
  try {
    entries = readdirSync(dir, { withFileTypes: true });
  } catch {
    return;
  }
  for (const e of entries) {
    if (e.isDirectory()) {
      if (!SKIP.has(e.name)) walk(join(dir, e.name));
      continue;
    }
    if (extname(e.name) !== '.html') continue;
    check(join(dir, e.name));
  }
}

function check(path) {
  const rel = relative(process.cwd(), path) || path;
  let html;
  try {
    html = readFileSync(path, 'utf8');
  } catch {
    return;
  }
  files++;

  BLOCK_RE.lastIndex = 0;
  let m;
  let i = -1;
  // Entity definitions accumulate across every block on the page, because the
  // duplicates live in *separate* <script> tags.
  const entityCounts = new Map();
  const countEntities = (node) => {
    if (Array.isArray(node)) {
      for (const item of node) countEntities(item);
      return;
    }
    if (!node || typeof node !== 'object') return;
    const canon = canonicalIdOf(node);
    if (canon && restatesCanonical(node)) {
      entityCounts.set(canon, (entityCounts.get(canon) ?? 0) + 1);
    }
    for (const value of Object.values(node)) countEntities(value);
  };

  while ((m = BLOCK_RE.exec(html)) !== null) {
    i++;
    const raw = m[1].trim();
    if (!raw) continue;
    blocks++;

    for (const { re, msg } of SIGNATURES) {
      if (re.test(raw)) errors.push(`${rel} [block ${i}]: ${msg}`);
    }

    let parsed;
    try {
      parsed = JSON.parse(raw);
    } catch (err) {
      errors.push(`${rel} [block ${i}]: invalid JSON — ${err.message}`);
      continue;
    }

    for (const node of Array.isArray(parsed) ? parsed : [parsed]) {
      if (!node || typeof node !== 'object') continue;
      const ctx = node['@context'];
      if (ctx === undefined) {
        errors.push(`${rel} [block ${i}]: missing @context`);
      } else if (typeof ctx === 'string' && !ctx.includes('schema.org')) {
        errors.push(`${rel} [block ${i}]: suspect @context ${JSON.stringify(ctx.slice(0, 80))}`);
      }
      if (!('@type' in node) && !('@graph' in node)) {
        errors.push(`${rel} [block ${i}]: missing @type (and no @graph)`);
      }
    }

    countEntities(parsed);
  }

  for (const [id, n] of entityCounts) {
    if (n > 1) {
      errors.push(
        `${rel}: ${id.split('#')[1]} defined ${n}x on one page — ` +
          'duplicate entity definitions merge unpredictably (run ' +
          'python3 scripts/dedupe_entity_graph.py)'
      );
    }
  }
}

const scanned = [];
for (const d of dirs) {
  const root = resolve(process.cwd(), d);
  if (!existsSync(root)) {
    console.error(`❌ verify-jsonld: ${d} not found — run the build first.`);
    process.exit(1);
  }
  if (!statSync(root).isDirectory()) {
    console.error(`❌ verify-jsonld: ${d} is not a directory.`);
    process.exit(1);
  }
  walk(root);
  scanned.push(d);
}

console.log(
  `[verify-jsonld] scanned ${files} HTML file(s), ${blocks} JSON-LD block(s) in ${scanned.join(', ')}`
);

if (errors.length) {
  console.error(
    `\n❌ verify-jsonld: ${errors.length} error(s) — refusing to ship broken structured data:`
  );
  for (const e of errors) console.error(`  - ${e}`);
  console.error(
    '\nFix the generator or post-processor that emitted this, not the page — ' +
      'regeneration will re-introduce a hand-patched file.'
  );
  process.exit(1);
}

console.log('[verify-jsonld] OK — all shipped JSON-LD parses');
