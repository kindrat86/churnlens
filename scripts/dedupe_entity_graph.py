#!/usr/bin/env python3
"""
dedupe_entity_graph.py — collapse duplicate entity nodes down to the single
canonical @graph emitted by inject_entity_graph.py.

WHY
---
Several generators have injected entity nodes into these pages over time
(seo-fixer.py, aeo-boost-inject.py, the pSEO rounds, and finally
inject_entity_graph.py). They all use the same @ids, so every page ended up
shipping two or three *full* definitions of #organization / #website /
#software in separate <script> blocks.

Same-@id nodes do merge in JSON-LD, so this was never a parse error — which is
exactly why it survived: `scripts/verify-jsonld.mjs` and Google's validator
both wave it through. The damage is that the merged nodes *disagree*:

  - #software carried two different `offers` sets on the homepage —
    a single "price: 0" Offer and the real Starter/Pro/Dealmaker set.
    Contradictory pricing in structured data is a rich-result risk and
    gives answer engines two different answers to "what does it cost".
  - #organization carried three different `foundingDate` values
    (2024 / 2026 / 2026-01-15) and two different `description` strings.
  - `url` appeared both with and without a trailing slash.

The merge order across blocks is not defined, so which value wins is luck.

WHAT IT DOES
------------
The canonical block is the one inject_entity_graph.py writes, identified by the
`<!-- entity-graph -->` marker. In every OTHER block on the page:

  - a *full* entity node (an object with a canonical @id and real properties)
    is removed when it is a member of a list (e.g. an @graph array), and
  - collapsed to a bare {"@id": …} reference when it is a property value
    (e.g. `publisher`, `author`, `mainEntity`) — so page schema keeps pointing
    at the entity instead of losing the link.

Bare {"@id": …} references are left alone. Page-specific schema (Article,
FAQPage, BreadcrumbList, WebPage, HowTo, …) is never touched. A block that is
left with nothing meaningful has its whole <script> tag removed.

Idempotent: running it twice is a no-op. Only blocks that actually changed are
re-serialized, so untouched blocks keep their original formatting.

Usage: python3 scripts/dedupe_entity_graph.py [--check]
  --check  report only, exit 1 if any duplicate remains (used by CI)
"""
import json
import os
import re
import sys

ROOT = os.getcwd()
MARKER = "<!-- entity-graph -->"
E = json.load(open(os.path.join(ROOT, "entity.json"), encoding="utf-8"))
BASE = E["url"]

# The entity nodes the canonical @graph owns. Nothing else may define these.
CANONICAL_IDS = {
    BASE + "/#organization",
    BASE + "/#software",
    BASE + "/#website",
    BASE + "/#founder",
}

# Not served (vercelignored, redirected, or dead) — leave them out so the diff
# stays on shipping pages and we don't collide with the i18n pipeline.
SKIP_DIRS = {
    "node_modules", ".git", ".vercel", ".well-known",
    "i18n", "i18n_out", "dist", "public", "__pycache__",
}

BLOCK_RE = re.compile(
    r'(?is)(<script[^>]*\btype\s*=\s*["\']?application/ld\+json["\']?[^>]*>)(.*?)(</script>)'
)

DROP = object()

# An @id-less Organization/WebSite/SoftwareApplication that is plainly us is a
# *separate* entity as far as Google is concerned — worse than a same-@id
# duplicate, because same-@id nodes at least merge. These get the canonical @id
# so they fold into the one entity instead of fragmenting it.
TYPE_TO_ID = {
    "Organization": BASE + "/#organization",
    "WebSite": BASE + "/#website",
    "SoftwareApplication": BASE + "/#software",
}

# Everything the canonical @graph already states. Re-stating any of it is how
# the descriptions and prices drifted apart in the first place, so these are
# dropped from the node being folded in; anything else is genuinely extra and
# is carried over onto the reference.
CANONICAL_PROPS = {
    "@context", "@type", "name", "alternateName", "url", "description",
    "disambiguatingDescription", "foundingDate", "knowsAbout", "sameAs", "logo",
    "image", "contactPoint", "publisher", "author", "offers", "featureList",
    "applicationCategory", "operatingSystem", "inLanguage", "potentialAction",
}


def canonical_id_of(node):
    """The canonical @id this node represents, or None if it isn't our entity."""
    if not isinstance(node, dict):
        return None

    node_id = node.get("@id")
    if isinstance(node_id, str):
        if node_id in CANONICAL_IDS:
            # A bare reference (@id/@type/@context only) is already correct.
            if not [k for k in node if k not in ("@id", "@type", "@context")]:
                return None
            return node_id
        return None

    # No @id: ours only if it names the brand or points at the site root.
    # `url` must match the root exactly — https://churnlens.site/some-page is a
    # different thing (e.g. the standalone calculator app), not the site entity.
    node_type = node.get("@type")
    # @type may legitimately be a list (multi-typed node); those are left alone
    # rather than guessed at.
    #
    # No minimum size here on purpose: {"@type":"Organization","name":"ChurnLens"}
    # sitting in an `author` slot is the *worst* fragment, not a harmless one —
    # it is an anonymous second ChurnLens with no @id to merge on.
    if not isinstance(node_type, str) or node_type not in TYPE_TO_ID:
        return None
    if node.get("name") == E["brand"] or (node.get("url") or "").rstrip("/") == BASE.rstrip("/"):
        return TYPE_TO_ID[node_type]
    return None


def strip(node, in_list):
    """Fold duplicate/fragmented entity nodes into the canonical one."""
    if isinstance(node, dict):
        canon = canonical_id_of(node)
        if canon:
            extra = {k: strip(v, in_list=False) for k, v in node.items()
                     if k not in CANONICAL_PROPS and k != "@id"}
            extra = {k: v for k, v in extra.items() if v is not DROP}
            if extra:
                # Carries real data the canonical node lacks (e.g. isRelatedTo).
                # Keep it, but under the canonical @id so it merges in.
                return {"@id": canon, **extra}
            # Pure restatement. Redundant in a list, load-bearing as a property
            # value (publisher / author / isPartOf) — keep the link there.
            return DROP if in_list else {"@id": canon}
        out = {}
        for key, value in node.items():
            new = strip(value, in_list=False)
            if new is not DROP:
                out[key] = new
        return out
    if isinstance(node, list):
        out = []
        for item in node:
            new = strip(item, in_list=True)
            if new is not DROP:
                out.append(new)
        return out
    return node


def is_empty(doc):
    """True if a block no longer says anything worth shipping."""
    if isinstance(doc, list):
        return all(is_empty(d) for d in doc)
    if not isinstance(doc, dict):
        return False
    if "@graph" in doc:
        graph = doc["@graph"]
        return isinstance(graph, list) and len(graph) == 0
    return len([k for k in doc if k not in ("@context", "@id", "@type")]) == 0


def process(html):
    """Returns (new_html, blocks_changed, blocks_removed)."""
    marker_at = html.find(MARKER)
    out = []
    cursor = 0
    changed = removed = 0

    for match in BLOCK_RE.finditer(html):
        # Leave the canonical block exactly as inject_entity_graph.py wrote it.
        is_canonical = (
            marker_at >= 0
            and marker_at <= match.start(1) <= marker_at + len(MARKER) + 2
        )
        raw = match.group(2).strip()
        if is_canonical or not raw:
            continue
        try:
            doc = json.loads(raw)
        except ValueError:
            continue  # verify-jsonld.mjs owns malformed blocks; don't guess here
        stripped = strip(doc, in_list=False)
        if stripped == doc:
            continue

        out.append(html[cursor:match.start(0)])
        if is_empty(stripped):
            removed += 1  # drop the entire <script> tag
        else:
            out.append(match.group(1))
            out.append(json.dumps(stripped, separators=(",", ":"), ensure_ascii=False))
            out.append(match.group(3))
            changed += 1
        cursor = match.end(0)

    if cursor == 0:
        return html, 0, 0
    out.append(html[cursor:])
    return "".join(out), changed, removed


def restates_canonical(node):
    """True if the node re-declares properties the canonical @graph owns.

    A node like {"@id": …/#organization, "isRelatedTo": […]} is *not* a
    duplicate — it merges into the canonical entity and adds a fact. Only nodes
    that restate canonical properties (name/url/description/offers/…) can drift
    out of sync, so those are what the gate counts.
    """
    return any(
        k in CANONICAL_PROPS and k not in ("@context", "@type")
        for k in node
    )


def audit(html):
    """Count conflicting definitions per canonical @id across the whole page."""
    counts = {}
    for match in BLOCK_RE.finditer(html):
        raw = match.group(2).strip()
        if not raw:
            continue
        try:
            doc = json.loads(raw)
        except ValueError:
            continue

        def walk(node):
            if isinstance(node, dict):
                canon = canonical_id_of(node)
                if canon and restates_canonical(node):
                    counts[canon] = counts.get(canon, 0) + 1
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(doc)
    # The canonical block defines each entity once; anything beyond that is a
    # duplicate definition or a fragment, so >1 (not >0) is the failure line.
    return {k: v for k, v in counts.items() if v > 1}


def main():
    check_only = "--check" in sys.argv
    files_changed = blocks_changed = blocks_removed = 0
    offenders = []

    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            if not name.endswith(".html"):
                continue
            path = os.path.join(dirpath, name)
            try:
                html = open(path, encoding="utf-8").read()
            except OSError:
                continue

            if check_only:
                dupes = audit(html)
                if dupes:
                    offenders.append((os.path.relpath(path, ROOT), dupes))
                continue

            new, changed, removed = process(html)
            if new != html:
                open(path, "w", encoding="utf-8").write(new)
                files_changed += 1
                blocks_changed += changed
                blocks_removed += removed

    if check_only:
        if offenders:
            print(f"❌ dedupe-entity-graph: {len(offenders)} page(s) still define an entity twice:")
            for rel, dupes in offenders[:20]:
                detail = ", ".join(f"{k.split('#')[-1]} x{v}" for k, v in sorted(dupes.items()))
                print(f"  - {rel}: {detail}")
            if len(offenders) > 20:
                print(f"  … and {len(offenders) - 20} more")
            print("\nRun: python3 scripts/dedupe_entity_graph.py")
            return 1
        print("✓ dedupe-entity-graph: every canonical entity is defined exactly once per page")
        return 0

    print(
        f"✓ deduped {files_changed} page(s): "
        f"{blocks_changed} block(s) rewritten, {blocks_removed} empty block(s) removed"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
