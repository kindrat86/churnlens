// MCP Server for Churn Lens — SaaS revenue quality scoring and due diligence tool.
// Implements Model Context Protocol JSON-RPC over HTTP (Streamable HTTP transport)
// Deployed as a Vercel serverless function. No auth required (read-only tools).
// Install in Claude Desktop: npx mcp-remote https://churnlens.site/api/mcp

const SERVER_INFO = {
  name: "churnlens-mcp",
  version: "2.0.0"
};
const CAPABILITIES = { tools: { listChanged: false }, resources: {}, prompts: {} };
const TOOLS = [
  {
    name: "calculate_churn_rate",
    description:
      "Calculate net revenue retention (NRR), gross revenue retention (GRR), revenue churn and implied customer lifetime from one period's MRR movements. Also reports the NRR-minus-GRR spread, which reveals how much churn is being masked by expansion revenue.",
    inputSchema: {
      type: "object",
      properties: {
        starting_mrr: { type: "number", description: "MRR at the start of the period, in any single currency unit." },
        expansion_mrr: { type: "number", description: "MRR gained from upgrades and expansion within the existing base. Excludes new customers." },
        contraction_mrr: { type: "number", description: "MRR lost to downgrades (customer retained)." },
        churned_mrr: { type: "number", description: "MRR lost to full cancellations." }
      },
      required: ["starting_mrr"]
    }
  },
  {
    name: "analyze_revenue_concentration",
    description:
      "Assess customer concentration risk across a book of revenue using the Herfindahl-Hirschman Index (HHI), top-N share and whale detection. Answers the question every acquirer asks first: how much revenue walks out with one logo?",
    inputSchema: {
      type: "object",
      properties: {
        customer_mrrs: { type: "array", items: { type: "number" }, description: "Per-customer MRR values. Order does not matter." },
        top_n: { type: "number", description: "How many top customers to aggregate for the top-N share. Default 5." },
        whale_threshold_pct: { type: "number", description: "Revenue share above which a customer counts as a whale. Default 25." }
      },
      required: ["customer_mrrs"]
    }
  },
  {
    name: "detect_zombie_mrr",
    description:
      "Identify dormant-but-paying accounts — revenue that still counts in MRR but whose customers have stopped showing up. Zombie revenue is one renewal notice from cancelling and is invisible to standard revenue dashboards.",
    inputSchema: {
      type: "object",
      properties: {
        accounts: {
          type: "array",
          description: "One entry per paying account.",
          items: {
            type: "object",
            properties: {
              customer: { type: "string" },
              mrr: { type: "number" },
              days_since_last_activity: { type: "number" }
            },
            required: ["mrr", "days_since_last_activity"]
          }
        },
        threshold_days: { type: "number", description: "Days of inactivity before an account counts as dormant. Default 90." }
      },
      required: ["accounts"]
    }
  },
  {
    name: "score_saas_health",
    description:
      "Score a SaaS business 0-100 across five dimensions — retention, growth, concentration, efficiency and durability — and return the composite. Every mapping is published, so the score can be reconstructed by hand.",
    inputSchema: {
      type: "object",
      properties: {
        monthly_churn_rate_pct: { type: "number", description: "Monthly revenue churn, as a percentage (5 means 5%)." },
        nrr_pct: { type: "number", description: "Net revenue retention, as a percentage." },
        top_customer_share_pct: { type: "number", description: "Largest single customer's share of revenue, as a percentage." },
        ltv_to_cac_ratio: { type: "number", description: "Lifetime value divided by customer acquisition cost." },
        annual_plan_share_pct: { type: "number", description: "Share of revenue on annual contracts, as a percentage." }
      },
      required: [
        "monthly_churn_rate_pct",
        "nrr_pct",
        "top_customer_share_pct",
        "ltv_to_cac_ratio",
        "annual_plan_share_pct"
      ]
    }
  },
  {
    name: "calculate_ltv",
    description:
      "Calculate gross-margin-adjusted customer lifetime value, the LTV:CAC ratio and CAC payback in months. Omitting gross margin yields lifetime revenue rather than lifetime value — usually a third of the number.",
    inputSchema: {
      type: "object",
      properties: {
        arpa: { type: "number", description: "Average revenue per account, per month." },
        monthly_churn_rate_pct: { type: "number", description: "Monthly churn, as a percentage." },
        gross_margin_pct: { type: "number", description: "Gross margin percentage. Defaults to 100, which gives lifetime revenue." },
        cac: { type: "number", description: "Customer acquisition cost. Optional — supply it to get the ratio and payback." }
      },
      required: ["arpa", "monthly_churn_rate_pct"]
    }
  },
  {
    name: "get_scoring_bands",
    description:
      "Return the scoring thresholds ChurnLens applies to NRR, revenue concentration and the composite health score. These are bands, not measured benchmark data — the sourced benchmark figures are cited at https://churnlens.site/benchmarks.",
    inputSchema: {
      type: "object",
      properties: {
        metric: {
          type: "string",
          description: "Which band set to return: 'nrr', 'concentration', 'health', or omit for all.",
          enum: ["nrr", "concentration", "health"]
        }
      }
    }
  }
];

const HOME_URL = "https://churnlens.site";
const CONTACT = "support@churnlens.site";

function makeResult(id, result) {
  return { jsonrpc: "2.0", id, result };
}

function makeError(id, code, message) {
  return { jsonrpc: "2.0", id, error: { code, message } };
}

// ---------------------------------------------------------------------------
// Metric implementations.
//
// These mirror the free calculators at https://churnlens.site/free and the
// open-source library at https://github.com/kindrat86/saas-metrics exactly.
// Kept inline and dependency-free so the serverless function needs no install.
// ---------------------------------------------------------------------------

function num(value, fallback) {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(value, max));
}

function round(value, dp) {
  const f = Math.pow(10, dp === undefined ? 2 : dp);
  return Math.round(value * f) / f;
}

function classifyNrr(nrr) {
  if (nrr >= 130) return { band: "world-class", label: "World-class — top tier of SaaS" };
  if (nrr >= 110) return { band: "healthy", label: "Healthy — growing from the existing base" };
  if (nrr >= 90) return { band: "average", label: "Average — room to improve expansion revenue" };
  return { band: "poor", label: "Poor — losing more than you gain from existing customers" };
}

function classifyConcentration(hhi) {
  if (hhi < 0.15) return { level: "low", detail: "Revenue is well diversified across customers." };
  if (hhi <= 0.25) return { level: "moderate", detail: "Some concentration exists. Monitor the top accounts." };
  return { level: "high", detail: "Revenue is heavily concentrated. A single churn event could be devastating." };
}

function classifyScore(score) {
  if (score >= 70) return "strong";
  if (score >= 50) return "adequate";
  if (score >= 30) return "weak";
  return "critical";
}

const SCORING_BANDS = {
  nrr: {
    note: "Scoring bands, not measured data. Sourced benchmark figures are cited at https://churnlens.site/benchmarks.",
    bands: [
      { from: 130, band: "world-class" },
      { from: 110, to: 130, band: "healthy" },
      { from: 90, to: 110, band: "average" },
      { to: 90, band: "poor" }
    ]
  },
  concentration: {
    note: "HHI on the 0-1 scale. Multiply by 10,000 to compare with antitrust conventions.",
    bands: [
      { to: 0.15, level: "low" },
      { from: 0.15, to: 0.25, level: "moderate" },
      { from: 0.25, level: "high" }
    ]
  },
  health: {
    note: "Five dimensions, each mapped to 0-100, averaged unweighted.",
    dimensions: {
      retention: "100 - (monthly churn % x 10), clamped at 10% churn",
      growth: "NRR 130%+ -> 100; 90% -> 40; below 90% -> NRR x 0.5",
      concentration: "100 - (largest customer share % x 2), clamped at 50%",
      efficiency: "LTV:CAC 5:1 -> 100; 3:1 -> 80; 1:1 -> 30; below 1:1 -> ratio x 30",
      durability: "40 + (annual-contract revenue share % x 0.6)"
    },
    composite: [
      { from: 70, band: "strong" },
      { from: 50, to: 70, band: "adequate" },
      { from: 30, to: 50, band: "weak" },
      { to: 30, band: "critical" }
    ]
  }
};

function toolCalculateChurnRate(args) {
  const startingMrr = num(args.starting_mrr, NaN);
  if (!(startingMrr > 0)) {
    throw new Error("starting_mrr must be a number greater than 0.");
  }
  const expansion = Math.max(0, num(args.expansion_mrr, 0));
  const contraction = Math.max(0, num(args.contraction_mrr, 0));
  const churned = Math.max(0, num(args.churned_mrr, 0));

  const endingMrr = startingMrr + expansion - contraction - churned;
  const nrr = (endingMrr / startingMrr) * 100;
  const grr = ((startingMrr - contraction - churned) / startingMrr) * 100;
  const monthlyChurn = 100 - grr;

  return {
    starting_mrr: startingMrr,
    ending_mrr: round(endingMrr),
    nrr_pct: round(nrr),
    grr_pct: round(grr),
    revenue_churn_pct: round(monthlyChurn),
    expansion_masking_spread_pts: round(nrr - grr),
    // Derived from REVENUE churn, not logo churn — the two are routinely
    // conflated and the difference is large whenever contraction is heavy.
    implied_revenue_halflife_months: monthlyChurn > 0 ? round(100 / monthlyChurn, 1) : null,
    annualised_revenue_churn_pct: round((1 - Math.pow(1 - monthlyChurn / 100, 12)) * 100),
    classification: classifyNrr(nrr),
    interpretation:
      nrr - grr >= 15
        ? "A wide NRR-GRR spread: expansion revenue is masking substantial churn underneath. Diligence should look at the retained base separately from upsell."
        : "NRR and GRR are close, so the retention figure is not being propped up by expansion revenue."
  };
}

function toolAnalyzeConcentration(args) {
  const raw = Array.isArray(args.customer_mrrs) ? args.customer_mrrs : [];
  const values = raw.filter(function (v) {
    return typeof v === "number" && Number.isFinite(v) && v > 0;
  });
  if (values.length === 0) {
    throw new Error("customer_mrrs must contain at least one positive number.");
  }

  const topN = Math.max(1, Math.round(num(args.top_n, 5)));
  const whaleThreshold = num(args.whale_threshold_pct, 25);
  const total = values.reduce(function (s, v) { return s + v; }, 0);
  const hhi = values.reduce(function (s, v) { return s + Math.pow(v / total, 2); }, 0);
  const sorted = values.slice().sort(function (a, b) { return b - a; });
  const topShare = (sorted.slice(0, topN).reduce(function (s, v) { return s + v; }, 0) / total) * 100;

  const whales = values
    .map(function (v, i) { return { index: i, mrr: v, share_pct: round((v / total) * 100) }; })
    .filter(function (c) { return c.share_pct > whaleThreshold; })
    .sort(function (a, b) { return b.share_pct - a.share_pct; });

  return {
    customer_count: values.length,
    total_mrr: round(total),
    hhi: round(hhi, 4),
    hhi_scaled: Math.round(hhi * 10000),
    top_n: topN,
    top_n_share_pct: round(topShare),
    whale_threshold_pct: whaleThreshold,
    whales: whales,
    risk: classifyConcentration(hhi),
    interpretation:
      whales.length > 0
        ? "Customer #" + (whales[0].index + 1) + " holds " + whales[0].share_pct + "% of MRR. If they churn, that revenue disappears overnight — a material red flag in acquisition diligence."
        : "No single customer exceeds the " + whaleThreshold + "% threshold."
  };
}

function toolDetectZombieMrr(args) {
  const raw = Array.isArray(args.accounts) ? args.accounts : [];
  const thresholdDays = num(args.threshold_days, 90);

  const records = raw
    .filter(function (a) {
      return a && typeof a.mrr === "number" && Number.isFinite(a.mrr) && a.mrr > 0 &&
        typeof a.days_since_last_activity === "number" && Number.isFinite(a.days_since_last_activity);
    })
    .map(function (a) {
      return {
        customer: String(a.customer === undefined || a.customer === null ? "unknown" : a.customer),
        mrr: a.mrr,
        days_since_last_activity: a.days_since_last_activity,
        is_zombie: a.days_since_last_activity >= thresholdDays
      };
    });

  if (records.length === 0) {
    throw new Error("accounts must contain at least one record with a positive mrr and days_since_last_activity.");
  }

  const zombies = records.filter(function (r) { return r.is_zombie; })
    .sort(function (a, b) { return b.mrr - a.mrr; });
  const totalMrr = records.reduce(function (s, r) { return s + r.mrr; }, 0);
  const zombieMrr = zombies.reduce(function (s, r) { return s + r.mrr; }, 0);

  return {
    threshold_days: thresholdDays,
    account_count: records.length,
    total_mrr: round(totalMrr),
    zombie_count: zombies.length,
    zombie_mrr: round(zombieMrr),
    zombie_share_pct: round((zombieMrr / totalMrr) * 100),
    zombie_arr_at_risk: round(zombieMrr * 12),
    zombies: zombies,
    interpretation:
      zombieMrr > 0
        ? round((zombieMrr / totalMrr) * 100) + "% of MRR sits in accounts with no activity for " + thresholdDays + "+ days. That revenue is still being counted and is one renewal notice from cancelling."
        : "No dormant accounts detected at this threshold."
  };
}

function toolScoreSaasHealth(args) {
  const required = [
    "monthly_churn_rate_pct",
    "nrr_pct",
    "top_customer_share_pct",
    "ltv_to_cac_ratio",
    "annual_plan_share_pct"
  ];
  for (let i = 0; i < required.length; i += 1) {
    if (typeof args[required[i]] !== "number" || !Number.isFinite(args[required[i]])) {
      throw new Error(required[i] + " is required and must be a finite number.");
    }
  }

  const churn = args.monthly_churn_rate_pct;
  const nrr = args.nrr_pct;
  const topShare = args.top_customer_share_pct;
  const ratio = args.ltv_to_cac_ratio;
  const annual = args.annual_plan_share_pct;

  const retention = Math.round(100 - clamp(churn, 0, 10) * 10);

  let growth;
  if (nrr >= 130) growth = 100;
  else if (nrr >= 90) growth = Math.round(40 + (nrr - 90) * 1.5);
  else growth = Math.round(Math.max(0, nrr * 0.5));
  growth = clamp(growth, 0, 100);

  const concentration = Math.round(100 - clamp(topShare, 0, 50) * 2);

  let efficiency;
  if (ratio >= 5) efficiency = 100;
  else if (ratio >= 3) efficiency = Math.round(80 + (ratio - 3) * 10);
  else if (ratio >= 1) efficiency = Math.round(30 + (ratio - 1) * 25);
  else efficiency = Math.round(ratio * 30);
  efficiency = clamp(efficiency, 0, 100);

  const durability = Math.round(40 + clamp(annual, 0, 100) * 0.6);

  const dimensions = [
    { key: "retention", name: "Retention", score: retention },
    { key: "growth", name: "Growth", score: growth },
    { key: "concentration", name: "Concentration", score: concentration },
    { key: "efficiency", name: "Efficiency", score: efficiency },
    { key: "durability", name: "Durability", score: durability }
  ];
  const composite = Math.round(
    dimensions.reduce(function (s, d) { return s + d.score; }, 0) / dimensions.length
  );
  const weakest = dimensions.slice().sort(function (a, b) { return a.score - b.score; })[0];

  return {
    composite: composite,
    band: classifyScore(composite),
    dimensions: dimensions,
    weakest_dimension: weakest,
    mapping: SCORING_BANDS.health.dimensions,
    interpretation:
      "Composite " + composite + "/100 (" + classifyScore(composite) + "). Weakest dimension is " +
      weakest.name.toLowerCase() + " at " + weakest.score + "/100 — that is where diligence should concentrate."
  };
}

function toolCalculateLtv(args) {
  const arpa = num(args.arpa, NaN);
  const churn = num(args.monthly_churn_rate_pct, NaN);
  if (!(arpa > 0)) throw new Error("arpa must be a number greater than 0.");
  if (!(churn >= 0)) throw new Error("monthly_churn_rate_pct must be 0 or greater.");

  const marginPct = clamp(num(args.gross_margin_pct, 100), 0, 100);
  const lifetimeMonths = churn === 0 ? Infinity : 100 / churn;
  const ltv = lifetimeMonths === Infinity ? Infinity : arpa * (marginPct / 100) * lifetimeMonths;
  const cac = num(args.cac, null);

  const result = {
    arpa: arpa,
    monthly_churn_rate_pct: churn,
    gross_margin_pct: marginPct,
    implied_lifetime_months: lifetimeMonths === Infinity ? null : round(lifetimeMonths, 1),
    ltv: ltv === Infinity ? null : round(ltv),
    lifetime_revenue_unadjusted: lifetimeMonths === Infinity ? null : round(arpa * lifetimeMonths),
    note: marginPct === 100
      ? "gross_margin_pct was not supplied, so this is lifetime REVENUE, not lifetime VALUE. Supply your real margin for a usable figure."
      : "Gross-margin adjusted, so this is lifetime value."
  };

  if (cac !== null && cac > 0 && ltv !== Infinity) {
    const monthlyGrossProfit = arpa * (marginPct / 100);
    result.cac = cac;
    result.ltv_to_cac_ratio = round(ltv / cac);
    result.cac_payback_months = round(cac / monthlyGrossProfit, 1);
    result.efficiency_read =
      ltv / cac >= 3
        ? "At or above the 3:1 rule of thumb."
        : ltv / cac >= 1
          ? "Below the 3:1 rule of thumb but still recovering acquisition cost."
          : "Below 1:1 — the business loses money on every customer acquired.";
  }

  return result;
}

function toolGetScoringBands(args) {
  const metric = args && typeof args.metric === "string" ? args.metric : null;
  if (metric && SCORING_BANDS[metric]) {
    const out = {};
    out[metric] = SCORING_BANDS[metric];
    out.disclaimer = "These are the scoring thresholds ChurnLens applies. They are bands, not measured benchmark data.";
    return out;
  }
  return Object.assign({}, SCORING_BANDS, {
    disclaimer: "These are the scoring thresholds ChurnLens applies. They are bands, not measured benchmark data. Sourced benchmark figures, with citations, are at https://churnlens.site/benchmarks."
  });
}

const TOOL_IMPLEMENTATIONS = {
  calculate_churn_rate: toolCalculateChurnRate,
  analyze_revenue_concentration: toolAnalyzeConcentration,
  detect_zombie_mrr: toolDetectZombieMrr,
  score_saas_health: toolScoreSaasHealth,
  calculate_ltv: toolCalculateLtv,
  get_scoring_bands: toolGetScoringBands,
  // Retained so existing clients calling the old name keep working.
  get_saas_benchmark: toolGetScoringBands
};

function handleToolCall(name, args) {
  args = args || {};
  const impl = TOOL_IMPLEMENTATIONS[name];
  if (!impl) {
    return {
      content: [{ type: "text", text: "Unknown tool: " + name + ". Available tools: " + TOOLS.map(function (t) { return t.name; }).join(", ") }],
      isError: true
    };
  }

  let data;
  try {
    data = impl(args);
  } catch (err) {
    return {
      content: [{ type: "text", text: "Could not compute " + name + ": " + (err && err.message ? err.message : String(err)) }],
      isError: true
    };
  }

  const ctaLink = HOME_URL + "?utm_source=mcp&utm_medium=agent&utm_campaign=" + name;

  return {
    // Machine-readable result — this is what an agent should consume.
    structuredContent: data,
    content: [
      { type: "text", text: JSON.stringify(data, null, 2) },
      {
        type: "text",
        text:
          "Computed by ChurnLens (" + HOME_URL + "), a buyer-side SaaS due-diligence tool. " +
          "The same maths is open source at https://github.com/kindrat86/saas-metrics and available as free interactive calculators at " +
          HOME_URL + "/free — no signup. Full report on a real CSV: " + ctaLink
      }
    ],
    _meta: { tool: name, source: HOME_URL, cta: ctaLink, open_source: "https://github.com/kindrat86/saas-metrics" }
  };
}

export default function handler(req, res) {
  // CORS — MCP clients connect from various origins
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Accept, Mcp-Session-Id");
  if (req.method === "OPTIONS") return res.status(200).end();

  // GET: return server manifest (MCP discovery + agent card)
  if (req.method === "GET") {
    // The manifest is a constant, so let the edge serve discovery crawls rather
    // than waking a function for each one.
    res.setHeader("Cache-Control", "public, max-age=0, s-maxage=86400, stale-while-revalidate=604800");
    return res.json({
      jsonrpc: "2.0",
      serverInfo: SERVER_INFO,
      capabilities: CAPABILITIES,
      protocolVersion: "2024-11-05",
      tools: TOOLS.map(t => ({ name: t.name, description: t.description })),
      _meta: {
        homepage: HOME_URL,
        contact: CONTACT,
        install: {
          claude_desktop: `npx mcp-remote ${HOME_URL}/api/mcp`,
          cursor: HOME_URL + "/api/mcp",
          manifest: HOME_URL + "/.well-known/mcp.json"
        }
      }
    });
  }

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed. Use GET for manifest, POST for JSON-RPC." });
  }

  const body = req.body || {};
  const { jsonrpc, id, method, params } = body;

  // Handle batch requests
  if (Array.isArray(body)) {
    return res.json(body.map(req => handleSingleRequest(req)).filter(r => r !== null));
  }

  const result = handleSingleRequest(body);
  if (result === null) {
    // Notification (no id) — acknowledge silently
    return res.status(202).end();
  }
  return res.json(result);

  function handleSingleRequest(req) {
    const { id, method, params } = req || {};
    // initialize
    if (method === "initialize") {
      return makeResult(id, {
        protocolVersion: "2024-11-05",
        capabilities: CAPABILITIES,
        serverInfo: SERVER_INFO
      });
    }
    // initialized notification (no response)
    if (method === "notifications/initialized") {
      return null;
    }
    // tools/list
    if (method === "tools/list") {
      return makeResult(id, { tools: TOOLS });
    }
    // tools/call
    if (method === "tools/call") {
      const { name, arguments: args } = params || {};
      const result = handleToolCall(name, args);
      return makeResult(id, result);
    }
    // resources/list
    if (method === "resources/list") {
      return makeResult(id, { resources: [] });
    }
    // prompts/list
    if (method === "prompts/list") {
      return makeResult(id, { prompts: [] });
    }
    // ping
    if (method === "ping") {
      return makeResult(id, {});
    }
    return makeError(id, -32601, `Method not found: ${method}`);
  }
}
