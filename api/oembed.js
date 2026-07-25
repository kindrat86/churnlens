// oEmbed provider for the free ChurnLens calculators.
//
// WordPress, Ghost, Discourse, Notion and most CMSs auto-embed a pasted URL if
// the target site advertises an oEmbed endpoint. That turns "someone pasted our
// link" into "someone published our widget, with attribution, on their domain".
//
// Spec: https://oembed.com — this implements the `rich` type, JSON format.

const BASE = "https://churnlens.site";

const TOOLS = {
  "churn-calculator": { title: "SaaS Churn Cost Calculator", height: 620 },
  "nrr-calculator": { title: "Net Revenue Retention (NRR) Calculator", height: 700 },
  "ltv-calculator": { title: "Customer LTV Calculator", height: 620 },
  "mrr-health-check": { title: "MRR Health Check", height: 640 },
  "saas-health-score": { title: "SaaS Revenue Health Score", height: 760 },
  "revenue-concentration-analyzer": { title: "Revenue Concentration Risk Analyzer", height: 700 },
  "zombie-mrr-detector": { title: "Zombie MRR Detector", height: 700 },
  "due-diligence-simulator": { title: "SaaS Due Diligence Simulator", height: 760 }
};

const MAX_WIDTH = 1200;
const MIN_WIDTH = 280;

function slugFromUrl(raw) {
  let parsed;
  try {
    parsed = new URL(raw);
  } catch (err) {
    return null;
  }
  // Only our own canonical host — an open oEmbed provider is an abuse vector.
  if (parsed.hostname !== "churnlens.site" && parsed.hostname !== "www.churnlens.site") {
    return null;
  }
  const parts = parsed.pathname.split("/").filter(Boolean);
  if (parts.length < 2 || parts[0] !== "free") return null;
  const slug = parts[1].replace(/\.html$/, "");
  return Object.prototype.hasOwnProperty.call(TOOLS, slug) ? slug : null;
}

function clampWidth(value) {
  const n = Number.parseInt(value, 10);
  if (!Number.isFinite(n)) return 640;
  return Math.max(MIN_WIDTH, Math.min(n, MAX_WIDTH));
}

export default function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Cache-Control", "public, max-age=3600, s-maxage=86400");

  const query = req.query || {};
  const format = (query.format || "json").toLowerCase();

  if (format !== "json") {
    // The spec requires 501 for a format the provider does not support.
    return res.status(501).json({ error: "Only the json format is supported." });
  }

  const slug = slugFromUrl(query.url || "");
  if (!slug) {
    return res.status(404).json({
      error: "Not an embeddable ChurnLens tool URL.",
      hint: "Expected a URL of the form " + BASE + "/free/<tool>",
      embeddable: Object.keys(TOOLS).map((s) => BASE + "/free/" + s)
    });
  }

  const tool = TOOLS[slug];
  const pageUrl = BASE + "/free/" + slug;
  const width = clampWidth(query.maxwidth);
  // maxheight is a ceiling the consumer may impose; absent it, use the tool's own.
  const maxHeight = Number.parseInt(query.maxheight, 10);
  const height = Number.isFinite(maxHeight) ? Math.min(tool.height, maxHeight) : tool.height;

  const iframe =
    '<iframe src="' + pageUrl + '?embed=1" width="100%" height="' + height + '" ' +
    'frameborder="0" style="border:0;border-radius:8px" loading="lazy" ' +
    'title="' + tool.title + ' by ChurnLens" data-churnlens></iframe>';

  const credit =
    '<p style="font:13px/1.5 system-ui,sans-serif;margin:8px 0 0">' +
    '<a href="' + pageUrl + '">' + tool.title + '</a> by ' +
    '<a href="' + BASE + '">ChurnLens</a> — buyer-side SaaS due diligence</p>';

  return res.json({
    version: "1.0",
    type: "rich",
    provider_name: "ChurnLens",
    provider_url: BASE,
    title: tool.title + " — ChurnLens",
    author_name: "ChurnLens",
    author_url: BASE,
    thumbnail_url: BASE + "/og.png",
    thumbnail_width: 1200,
    thumbnail_height: 630,
    width: width,
    height: height,
    cache_age: 86400,
    html: iframe + credit
  });
}
