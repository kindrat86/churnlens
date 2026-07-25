#!/usr/bin/env bash
# IndexNow ping for churnlens.site — notifies Bing, Yandex, Seznam, Naver of new/changed URLs.
# Usage: bash scripts/indexnow-ping.sh [--dry-run]
#
# Why this filters instead of submitting the raw sitemap:
#   Submitting 404s or URLs that self-canonicalize elsewhere is a negative quality
#   signal and burns the daily quota. As of 2026-07-25 the sitemap held 9 URLs
#   returning 404, 15 that canonicalize to a different variant, and 10 with no
#   canonical tag at all — 34 of 230. The previous version submitted the first 50
#   sitemap entries unfiltered (22% coverage, and it included a known 404: /badge).
#
# Submits only URLs that are HTTP 200 AND self-canonical (canonical == the URL itself).

set -euo pipefail

HOST="churnlens.site"
KEY="7f721f8f993f40d6806af92a355154b0"
KEY_FILE="${KEY}.txt"
DRY_RUN="${1:-}"

echo "=== IndexNow ping for ${HOST} ==="

# 0. The key file must be reachable or IndexNow cannot validate the key.
KEY_STATUS=$(curl -sS -o /dev/null -w '%{http_code}' "https://${HOST}/${KEY_FILE}")
if [ "$KEY_STATUS" != "200" ]; then
  echo "FATAL: key file https://${HOST}/${KEY_FILE} returned ${KEY_STATUS}, expected 200." >&2
  echo "       Deploy the key file before pinging." >&2
  exit 1
fi
echo "key file: OK (200)"

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

# 1. All sitemap URLs.
curl -sS "https://${HOST}/sitemap.xml" | grep -oE "<loc>[^<]+" | sed 's/<loc>//' | sort -u > "$WORK/all.txt"
echo "sitemap URLs: $(wc -l < "$WORK/all.txt" | tr -d ' ')"

# 2. Keep only HTTP 200 + self-canonical.
check_url() {
  u="$1"
  body=$(curl -sS --max-time 20 "$u" || true)
  code=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 20 "$u" || echo 000)
  can=$(printf '%s' "$body" | grep -o 'rel="canonical" href="[^"]*"' | head -1 | sed 's/.*href="//;s/"//')
  [ "$code" = "200" ] && [ -n "$can" ] && [ "$can" = "$u" ] && echo "$u"
}
export -f check_url
xargs -P 16 -I{} bash -c 'check_url "$@"' _ {} < "$WORK/all.txt" > "$WORK/clean.txt" 2>/dev/null || true
sort -u -o "$WORK/clean.txt" "$WORK/clean.txt"

TOTAL=$(wc -l < "$WORK/all.txt" | tr -d ' ')
CLEAN=$(wc -l < "$WORK/clean.txt" | tr -d ' ')
echo "submittable (200 + self-canonical): ${CLEAN} of ${TOTAL}  (skipping $((TOTAL - CLEAN)))"

if [ "$CLEAN" -eq 0 ]; then echo "Nothing to submit." >&2; exit 1; fi

if [ "$DRY_RUN" = "--dry-run" ]; then
  echo "--dry-run: would submit ${CLEAN} URLs. Skipped:"
  comm -23 "$WORK/all.txt" "$WORK/clean.txt" | sed 's/^/  /'
  exit 0
fi

# 3. Submit in batches of 100 to both endpoints.
KEY="$KEY" HOST="$HOST" KEY_FILE="$KEY_FILE" python3 - "$WORK/clean.txt" <<'PY'
import json, os, sys, time, urllib.request, urllib.error

key, host, key_file = os.environ["KEY"], os.environ["HOST"], os.environ["KEY_FILE"]
urls = [u.strip() for u in open(sys.argv[1]) if u.strip()]
meaning = {
    200: "OK — URLs submitted",
    202: "Accepted — key validation pending",
    400: "Bad request — invalid format",
    403: "Forbidden — key not valid",
    422: "Unprocessable — URL/host or key mismatch",
    429: "Rate limited — too many requests",
}

def post(endpoint, batch):
    payload = json.dumps({
        "host": host, "key": key,
        "keyLocation": f"https://{host}/{key_file}",
        "urlList": batch,
    }).encode()
    req = urllib.request.Request(
        endpoint, data=payload,
        headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.status, r.read().decode()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]
    except Exception as e:
        return "ERR", str(e)[:200]

failed = False
for endpoint in ("https://api.indexnow.org/IndexNow", "https://www.bing.com/IndexNow"):
    print(f"--- {endpoint} ---")
    for i in range(0, len(urls), 100):
        batch = urls[i:i + 100]
        code, body = post(endpoint, batch)
        print(f"  batch {i//100+1} ({len(batch)} urls): HTTP {code}  "
              f"{meaning.get(code, '')}  {body.strip()[:80]}")
        if code not in (200, 202):
            failed = True
        time.sleep(2)
sys.exit(1 if failed else 0)
PY

echo "=== Done. Submission != indexing; Bing/Yandex typically act within 24-48h. ==="
