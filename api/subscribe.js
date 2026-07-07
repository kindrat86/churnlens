// Vercel serverless function — email capture for Churn Lens funnel
// Captures lead, stores to KV if configured, and sends the checklist via Resend.

const CHECKLIST_HTML = `<!doctype html>
<html><body style="font-family:Inter,Arial,sans-serif;background:#0f172a;color:#f8fafc;padding:2rem;">
<div style="max-width:560px;margin:0 auto;background:#1e293b;border:1px solid #334155;border-radius:12px;padding:2rem;">
<h1 style="font-family:'Space Grotesk',sans-serif;color:#3b82f6;">&#10003; Your Churn Audit Checklist</h1>
<p style="color:#cbd5e1;line-height:1.6;">Here's everything you asked for. Bookmark this email — you'll reference it on your next deal.</p>
<h2 style="color:#fff;font-size:1.1rem;">What's inside:</h2>
<ul style="color:#94a3b8;line-height:1.8;">
<li><strong style="color:#e2e8f0;">The 23-Point Checklist</strong> — already shown to you on the thank-you page</li>
<li><strong style="color:#e2e8f0;">Sample Risk Report</strong> — Churn Lens output on a real $48K MRR SaaS (below)</li>
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
<p style="color:#64748b;font-size:0.85rem;">Tomorrow: "The $48K MRR target where headline churn hid 47% revenue decay" — a full walk-through of the sample report. Look out for it.</p>
<p style="color:#64748b;font-size:0.8rem;margin-top:1.5rem;">Churn Lens &middot; <a href="https://churnlens.site" style="color:#3b82f6;">churnlens.site</a></p>
</div>
</body></html>`;

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  const email = (req.body?.email || '').toString().trim().toLowerCase();
  const source = (req.body?.source || 'unknown').toString();

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ ok: false, error: 'Valid email required' });
  }

  console.log(JSON.stringify({
    event: 'email_capture',
    email,
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
          from: 'Churn Lens <checklist@churnlens.site>',
          to: email,
          subject: '✓ Your 23-point churn audit checklist + sample report',
          html: CHECKLIST_HTML
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

  return res.status(200).json({ ok: true, message: 'Subscribed successfully', email_sent });
}
