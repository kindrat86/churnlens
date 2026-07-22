#!/usr/bin/env bash
# IndexNow ping script for churnlens.site
# Run after deploy to notify Bing, Yandex, etc. of new/changed URLs.
# Usage: bash scripts/indexnow-ping.sh

set -euo pipefail

HOST="churnlens.site"
KEY="7f721f8f993f40d6806af92a355154b0"
KEY_FILE="${KEY}.txt"
ENDPOINTS=(
  "https://www.bing.com/indexnow"
  "https://api.indexnow.org/indexnow"
)

# Verify key file exists at site root
echo "=== IndexNow Ping for ${HOST} ==="

# Collect URLs from sitemap
URLS=$(curl -s "https://${HOST}/sitemap.xml" | grep -oE "<loc>[^<]+" | sed 's/<loc>//' | head -50)

# Build JSON payload
PAYLOAD=$(python3 -c "
import json, sys
urls = sys.stdin.read().strip().split('\n')
print(json.dumps({
    'host': '${HOST}',
    'key': '${KEY}',
    'keyLocation': 'https://${HOST}/${KEY_FILE}',
    'urlList': urls
}))
" <<< "$URLS")

for endpoint in "${ENDPOINTS[@]}"; do
  echo "--- Pinging ${endpoint} ---"
  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$endpoint" \
    -H "Content-Type: application/json; charset=utf-8" \
    -d "$PAYLOAD")
  HTTP_CODE=$(echo "$RESPONSE" | tail -1)
  BODY=$(echo "$RESPONSE" | head -n -1)
  echo "Status: $HTTP_CODE"
  echo "Response: $BODY"
  echo ""
done

echo "=== Done ==="
