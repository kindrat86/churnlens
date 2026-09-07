"""Keep the NRR calculator's page identity consistent across crawler signals."""
import json
from html.parser import HTMLParser
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class PageSignals(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.og_urls = []
        self.schemas = []
        self.schema_text = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs["href"])
        if tag == "meta" and attrs.get("property") == "og:url":
            self.og_urls.append(attrs["content"])
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.schema_text = ""

    def handle_data(self, data):
        if self.schema_text is not None:
            self.schema_text += data

    def handle_endtag(self, tag):
        if tag == "script" and self.schema_text is not None:
            self.schemas.append(json.loads(self.schema_text))
            self.schema_text = None


class NrrCanonicalTests(unittest.TestCase):
    def test_application_identity_matches_canonical_and_sitemap(self):
        page = PageSignals()
        page.feed((ROOT / "free/nrr-calculator/index.html").read_text())
        self.assertEqual(len(page.canonicals), 1)
        canonical = page.canonicals[0]
        self.assertEqual(page.og_urls, [canonical])
        applications = [s for s in page.schemas if s.get("@type") == "WebApplication"]
        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0]["url"], canonical)
        # Trusted repository XML, not arbitrary user-supplied XML.
        urls = [loc.text for loc in ET.parse(ROOT / "sitemap.xml").iter(
            "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertIn(canonical, urls)
        self.assertNotIn(canonical + "/", urls)
        self.assertFalse(json.loads((ROOT / "vercel.json").read_text())["trailingSlash"])

    def test_copy_results_shares_canonical_url(self):
        html = (ROOT / "free/nrr-calculator/index.html").read_text()
        page = PageSignals()
        page.feed(html)
        shared_text = html.split("const text=`Net Revenue Retention (ChurnLens)")[1].split("`", 1)[0]
        self.assertIn(page.canonicals[0], shared_text)
        self.assertNotIn(page.canonicals[0] + "/", shared_text)


if __name__ == "__main__":
    unittest.main()
