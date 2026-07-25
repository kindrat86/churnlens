// Unsubscribe endpoint for ChurnLens subscribers.
//
//   GET  /api/unsubscribe?email=X          -> confirmation page with a POST button
//   GET  /api/unsubscribe?email=X&t=<sig>  -> unsubscribes immediately (true one-click)
//   POST /api/unsubscribe  (email in query or body) -> unsubscribes
//
// Requires RESEND_API_KEY in Vercel project env. UNSUB_SECRET is optional and
// only enables the signed one-click GET form.
//
// Why GET alone no longer mutates state (changed 2026-07-25):
//   The previous version unsubscribed on any bare GET. Two consequences:
//   (1) anyone could unsubscribe any address they could guess — unauthenticated
//       list sabotage; (2) mail-security link scanners, Outlook SafeLinks and
//       link prefetchers fetch URLs in email bodies automatically, silently
//       unsubscribing real subscribers who never clicked.
//   Emails already in the wild carry untokenized `?email=` links (see
//   ~/.hermes/email-engine/engine.py), so requiring a token outright would
//   strand real recipients with no way to opt out — worse than the bug. Hence:
//   unsigned GET degrades to a one-click confirmation page, signed GET and POST
//   act directly. RFC 8058 one-click (List-Unsubscribe-Post) uses POST and works.

import { createHmac, timingSafeEqual } from 'node:crypto';

const CHURNLENS_AUDIENCE_ID = '54ff48b1-45bf-4d7e-8ecf-e0df909176d5';
const SUPPORT = 'support@churnlens.site';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/** Signature for one-click GET links: base64url, truncated to 32 chars. */
function sign(email, secret) {
  return createHmac('sha256', secret)
    .update(email.trim().toLowerCase())
    .digest('base64url')
    .slice(0, 32);
}

function validToken(email, token, secret) {
  if (!secret || !token) return false;
  const expected = Buffer.from(sign(email, secret));
  const given = Buffer.from(String(token));
  // timingSafeEqual throws on length mismatch — compare lengths first.
  return expected.length === given.length && timingSafeEqual(expected, given);
}

export default async function handler(req, res) {
  // HEAD must be allowed wherever GET is, and mail-security scanners routinely
  // HEAD the links in a message — answering 405 makes them report the
  // unsubscribe link as broken, which is a deliverability problem. HEAD is
  // treated as never-mutating, so even a signed token does not act on one.
  const isHead = req.method === 'HEAD';
  if (req.method !== 'GET' && req.method !== 'POST' && !isHead) {
    res.setHeader('Allow', 'GET, HEAD, POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Never index or cache any variant of this page.
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');

  const email = String(req.query?.email ?? req.body?.email ?? '').trim();
  const token = String(req.query?.t ?? req.body?.t ?? '').trim();

  if (!email) return page(res, 'error', 'This unsubscribe link is missing an email address.');
  if (!EMAIL_RE.test(email)) return page(res, 'error', 'That does not look like a valid email address.');

  // Unsigned GET must not mutate state — offer an explicit confirmation instead.
  const signed = validToken(email, token, process.env.UNSUB_SECRET);
  if (isHead || (req.method === 'GET' && !signed)) return confirmPage(res, email);

  const key = process.env.RESEND_API_KEY;
  if (!key) {
    return page(res, 'error',
      `The unsubscribe service is temporarily unavailable. Email ${SUPPORT} and we will remove you by hand.`);
  }

  let ok = false;
  try {
    const resp = await fetch(
      `https://api.resend.com/audiences/${CHURNLENS_AUDIENCE_ID}/contacts/${encodeURIComponent(email)}`,
      {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ unsubscribed: true }),
      }
    );
    // 404 = not on this audience. Treat as success: the outcome the person asked
    // for already holds, and saying so avoids confirming who is on the list.
    ok = resp.ok || resp.status === 404;
    if (!ok) console.error('Unsubscribe PATCH failed', resp.status, await resp.text());
  } catch (err) {
    console.error('Unsubscribe PATCH threw', err?.message);
  }

  // Report what actually happened. The old version always claimed success, so a
  // Resend outage silently produced people who believed they had opted out.
  return ok
    ? page(res, 'ok', email)
    : page(res, 'error',
        `We could not complete that just now. Email ${SUPPORT} and we will remove you by hand.`);
}

const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const SHELL = (title, icon, heading, bodyHtml) => `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>${title} — ChurnLens</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0f172a;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh; padding: 24px; color: #f8fafc;
  }
  .card {
    background: #1e293b; border: 1px solid #334155; border-radius: 16px;
    padding: 48px 40px; max-width: 480px; width: 100%; text-align: center;
  }
  .check {
    width: 64px; height: 64px; background: rgba(37,99,235,.12); border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 28px; color: #3b82f6; margin-bottom: 20px;
  }
  h1 { font-size: 22px; color: #f8fafc; margin-bottom: 8px; }
  p { font-size: 15px; color: #94a3b8; line-height: 1.6; }
  p + p { margin-top: 12px; }
  .email { font-weight: 600; color: #f8fafc; }
  button {
    margin-top: 24px; width: 100%; padding: 14px 20px; font: inherit; font-weight: 600;
    color: #fff; background: #2563eb; border: 0; border-radius: 10px; cursor: pointer;
  }
  button:hover { background: #1d4ed8; }
  .footer { margin-top: 24px; font-size: 12px; color: #64748b; }
  a { color: #3b82f6; text-decoration: none; }
</style>
</head>
<body>
<div class="card">
  <div class="check">${icon}</div>
  <h1>${heading}</h1>
  ${bodyHtml}
  <p class="footer"><a href="https://churnlens.site">churnlens.site</a></p>
</div>
</body>
</html>`;

function send(res, status, html) {
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  return res.status(status).send(html);
}

/** Explicit confirmation for unsigned GETs — still one click, but a human's. */
function confirmPage(res, email) {
  return send(res, 200, SHELL('Confirm unsubscribe', '&#9993;', 'Confirm you want to unsubscribe',
    `<p>Click below and <span class="email">${esc(email)}</span> will stop receiving ChurnLens emails.</p>
  <form method="POST" action="/api/unsubscribe">
    <input type="hidden" name="email" value="${esc(email)}">
    <button type="submit">Unsubscribe me</button>
  </form>`));
}

function page(res, kind, detail) {
  if (kind === 'ok') {
    return send(res, 200, SHELL('Unsubscribed', '&#10003;', 'You have been unsubscribed',
      `<p><span class="email">${esc(detail)}</span> will no longer receive ChurnLens emails.</p>`));
  }
  return send(res, 200, SHELL('Unsubscribe', '&#9888;', 'We hit a problem',
    `<p>${esc(detail)}</p>`));
}
