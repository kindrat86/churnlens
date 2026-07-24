// One-click unsubscribe endpoint for ChurnLens subscribers.
// GET /api/unsubscribe?email=X
// Requires RESEND_API_KEY in Vercel project env.

const CHURNLENS_AUDIENCE_ID = '54ff48b1-45bf-4d7e-8ecf-e0df909176d5';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }

  const key = process.env.RESEND_API_KEY;
  if (!key) {
    return sendPage(res, 'Unsubscribe service not configured');
  }

  const email = (req.query.email || '').trim();

  if (!email) {
    return sendPage(res, 'Missing email parameter');
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return sendPage(res, 'Invalid email address');
  }

  const encodedEmail = encodeURIComponent(email);

  try {
    await fetch(
      `https://api.resend.com/audiences/${CHURNLENS_AUDIENCE_ID}/contacts/${encodedEmail}`,
      {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${key}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ unsubscribed: true }),
      }
    );
  } catch (err) {
    console.error('Unsubscribe PATCH failed', err);
  }

  return sendPage(res, email);
}

function sendPage(res, email) {
  const esc = String(email || '').replace(/[&<>"']/g, c =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])
  );

  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.status(200).send(`<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Unsubscribed — ChurnLens</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0f172a;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh; padding: 24px; color: #f8fafc;
  }
  .card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 48px 40px;
    max-width: 480px;
    width: 100%;
    text-align: center;
  }
  .check {
    width: 64px; height: 64px;
    background: rgba(37,99,235,.12);
    border-radius: 50%;
    display: inline-flex;
    align-items: center; justify-content: center;
    font-size: 28px;
    color: #3b82f6;
    margin-bottom: 20px;
  }
  h1 { font-size: 22px; color: #f8fafc; margin-bottom: 8px; }
  p { font-size: 15px; color: #94a3b8; line-height: 1.6; }
  .email { font-weight: 600; color: #f8fafc; }
  .footer { margin-top: 24px; font-size: 12px; color: #64748b; }
  a { color: #3b82f6; text-decoration: none; }
</style>
</head>
<body>
<div class="card">
  <div class="check">&#10003;</div>
  <h1>You have been unsubscribed</h1>
  <p><span class="email">${esc}</span> has been removed from ChurnLens emails.</p>
  <p class="footer"><a href="https://churnlens.site">churnlens.site</a></p>
</div>
</body>
</html>`);
}
