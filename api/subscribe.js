import { createHmac } from 'node:crypto';

// Vercel serverless function — email capture for the ChurnLens funnel
// Captures lead, stores to KV if configured, adds the contact to the ChurnLens
// Resend audience (the daily drip engine reads that audience — without this step
// the promised 5-day sequence never fires), and sends the checklist immediately.

// Resend audience "ChurnLens". The drip engine at ~/.hermes/email-engine/engine.py
// resolves this audience by NAME and derives each contact's drip day from its
// created_at, so simply creating the contact here is what starts the sequence.
const CHURNLENS_AUDIENCE_ID = process.env.RESEND_AUDIENCE_ID || '54ff48b1-45bf-4d7e-8ecf-e0df909176d5';

const SITE = 'https://churnlens.site';

/** Matches api/unsubscribe.js, so the emailed link can be true one-click. */
function unsubUrl(email) {
  const q = new URLSearchParams({ email });
  const secret = process.env.UNSUB_SECRET;
  if (secret) {
    q.set('t', createHmac('sha256', secret)
      .update(email.trim().toLowerCase()).digest('base64url').slice(0, 32));
  }
  return `${SITE}/api/unsubscribe?${q.toString()}`;
}

// Takes the unsubscribe URL because it is per-recipient. This email previously
// shipped with no unsubscribe path of any kind — no link and no List-Unsubscribe
// header — to cold captures, from an EU-based sender.
const checklistHtml = (unsub) => `<!doctype html>
<html><body style="font-family:Inter,Arial,sans-serif;background:#0f172a;color:#f8fafc;padding:2rem;">
<div style="max-width:560px;margin:0 auto;background:#1e293b;border:1px solid #334155;border-radius:12px;padding:2rem;">
<h1 style="font-family:'Space Grotesk',sans-serif;color:#3b82f6;">&#10003; Your Churn Audit Checklist</h1>
<p style="color:#cbd5e1;line-height:1.6;">Here's everything you asked for. Bookmark this email — you'll reference it on your next deal.</p>
<h2 style="color:#fff;font-size:1.1rem;">What's inside:</h2>
<ul style="color:#94a3b8;line-height:1.8;">
<li><strong style="color:#e2e8f0;">The 23-Point Checklist</strong> — already shown to you on the thank-you page</li>
<li><strong style="color:#e2e8f0;">Sample Risk Report</strong> — a full ChurnLens output on a synthetic $48K MRR target: <a href="https://churnlens.site/sample-churn-risk-report" style="color:#3b82f6;">read it here</a></li>
<li><strong style="color:#e2e8f0;">Hidden Churn Cheat Sheet</strong> — the 7 tricks sellers use</li>
</ul>
<h2 style="color:#fff;font-size:1.1rem;">The 7 Hidden Churn Tricks (Cheat Sheet)</h2>
<ol style="color:#94a3b8;line-height:1.9;">
<li><strong>Trial churn reclassification</strong> — trials counted as "new" but excluded from churn</li>
<li><strong>Cohort selection bias</strong> — best month shown as "representative"</li>
<li><strong>Downgrade exclusion</strong> — plan drops not counted as churn</li>
<li><strong>Annualization trick</strong> — linear instead of compounded annual rate</li>
<li><strong>Excluding involuntary churn</strong> — failed payments not counted</li>
<li><strong>Reactivation smoothing</strong> — serial churners counted as one event</li>
<li><strong>"Growing out of churn" illusion</strong> — new sales mask the denominator</li>
</ol>
<hr style="border-color:#334155;margin:1.5rem 0;">
<p style="color:#64748b;font-size:0.85rem;">Over the next five days you'll get one email a day from me: the $340K deal that started ChurnLens, the three claims that make buyers trust a seller's churn number, how each of the five risks is actually computed, and what to do when a seller refuses to hand over the export. One a day, then I get out of your inbox.</p>
<p style="color:#64748b;font-size:0.8rem;margin-top:1.5rem;">— Maryan, founder, ChurnLens &middot; <a href="https://churnlens.site" style="color:#3b82f6;">churnlens.site</a></p>
<p style="color:#64748b;font-size:0.75rem;margin-top:0.75rem;">You are receiving this because you requested the churn audit checklist on churnlens.site. <a href="${unsub}" style="color:#64748b;text-decoration:underline;">Unsubscribe</a>.</p>
</div>
</body></html>`;

// --- Abuse protection -------------------------------------------------------
const RL_LIMIT = 5;               // max requests per IP per window
const RL_WINDOW_SECONDS = 3600;   // 1 hour

// Best-effort per-instance fallback when KV is not configured.
const memHits = new Map(); // ip -> { count, reset }

function memRateLimited(ip) {
  const now = Date.now();
  const entry = memHits.get(ip);
  if (!entry || now > entry.reset) {
    if (memHits.size > 5000) memHits.clear();
    memHits.set(ip, { count: 1, reset: now + RL_WINDOW_SECONDS * 1000 });
    return false;
  }
  entry.count += 1;
  return entry.count > RL_LIMIT;
}

async function kvRateLimited(ip) {
  const url = process.env.KV_REST_API_URL;
  const token = process.env.KV_REST_API_TOKEN;
  const key = `rl:subscribe:${ip}`;
  const resp = await fetch(`${url}/incr/${encodeURIComponent(key)}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (!resp.ok) throw new Error(`KV incr failed: ${resp.status}`);
  const { result: count } = await resp.json();
  if (count === 1) {
    await fetch(`${url}/expire/${encodeURIComponent(key)}/${RL_WINDOW_SECONDS}`, {
      headers: { Authorization: `Bearer ${token}` }
    }).catch(() => {});
  }
  return count > RL_LIMIT;
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  // This endpoint sends ChurnLens-branded mail to whatever address it is given,
  // so it is a spam relay if left fully open — and the bounces land on OUR
  // sending domain's reputation. Reject browser-originated cross-site posts.
  // `Origin` is absent on same-origin form posts and on server-to-server calls,
  // so only an explicitly foreign origin is refused.
  const origin = (req.headers.origin || '').toString();
  if (origin && !/^https:\/\/(www\.)?churnlens\.site$/.test(origin)) {
    return res.status(403).json({ ok: false, error: 'Forbidden' });
  }

  const ip = (req.headers['x-forwarded-for'] || '').toString().split(',')[0].trim() || 'unknown';

  // Per-IP rate limit: durable via KV when configured, per-instance fallback otherwise.
  try {
    const limited = (process.env.KV_REST_API_URL && process.env.KV_REST_API_TOKEN)
      ? await kvRateLimited(ip)
      : memRateLimited(ip);
    if (limited) {
      return res.status(429).json({ ok: false, error: 'Too many requests, try again later' });
    }
  } catch (e) {
    console.error('Rate-limit check failed (failing open):', e.message);
  }

  // Honeypot — hidden field humans never fill; answer like a success, send nothing.
  const honeypot = ((req.body?.website || req.body?.company || '')).toString().trim();
  if (honeypot) {
    return res.status(200).json({ ok: true, message: 'Subscribed successfully', email_sent: true });
  }

  const email = (req.body?.email || '').toString().trim().toLowerCase();
  const source = (req.body?.source || 'unknown').toString().slice(0, 64);

  if (!email || email.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ ok: false, error: 'Valid email required' });
  }

  // Log a masked address only — full address goes to KV/Resend, not the logs.
  console.log(JSON.stringify({
    event: 'email_capture',
    email: email.replace(/^(..).*(@.*)$/, '$1***$2'),
    source,
    timestamp: new Date().toISOString()
  }));

  // Persist to KV if configured
  if (process.env.KV_REST_API_URL && process.env.KV_REST_API_TOKEN) {
    try {
      await fetch(`${process.env.KV_REST_API_URL}/lpush/leads/${encodeURIComponent(JSON.stringify({ email, source, ts: Date.now() }))}`, {
        headers: { Authorization: `Bearer ${process.env.KV_REST_API_TOKEN}` }
      });
    } catch (e) {
      console.error('KV write failed:', e.message);
    }
  }

  // Add the contact to the ChurnLens Resend audience. This is what enrols the
  // lead in the 5-day sequence promised on the squeeze page — the drip engine
  // only ever looks at audience members. Failure here must not fail the opt-in,
  // so it is logged and swallowed.
  let audience_added = false;
  if (process.env.RESEND_API_KEY) {
    try {
      const resp = await fetch(`https://api.resend.com/audiences/${CHURNLENS_AUDIENCE_ID}/contacts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, unsubscribed: false })
      });
      if (resp.ok) {
        audience_added = true;
      } else {
        // A duplicate contact is a 4xx and is entirely expected on a re-subscribe.
        console.error('Resend audience add failed:', resp.status, await resp.text());
      }
    } catch (e) {
      console.error('Resend audience add threw:', e.message);
    }
  }

  // Send the checklist email via Resend if configured
  let email_sent = false;
  if (process.env.RESEND_API_KEY) {
    try {
      const resp = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          from: 'Maryan at ChurnLens <checklist@churnlens.site>',
          to: email,
          subject: '✓ Your 23-point churn audit checklist + sample report',
          html: checklistHtml(unsubUrl(email)),
          // RFC 8058 one-click unsubscribe. Gmail and Yahoo require this on bulk
          // mail; without it recipients reach for "report spam" instead, which is
          // what actually damages a sending domain.
          headers: {
            'List-Unsubscribe': `<${unsubUrl(email)}>`,
            'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click'
          }
        })
      });
      if (resp.ok) {
        email_sent = true;
      } else {
        console.error('Resend error:', await resp.text());
      }
    } catch (e) {
      console.error('Resend send failed:', e.message);
    }
  } else {
    console.log('RESEND_API_KEY not set — skipping email send');
  }

  return res.status(200).json({ ok: true, message: 'Subscribed successfully', email_sent, audience_added });
}
