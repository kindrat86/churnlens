from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYMENT_LINK = "https://buy.stripe.com/14AcN4eNl7xmfQW8E00x20w"
CANONICAL_CAPTURE = "posthog.capture('checkout_clicked'"
LEGACY_CAPTURE = "posthog.capture('analysis_checkout_clicked'"


def test_pricing_ctas_emit_canonical_checkout_event() -> None:
    failures = []
    for relative in ("pricing.html", "pricing/index.html"):
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        link_at = text.index(PAYMENT_LINK)
        context = text[link_at : link_at + 500]
        if CANONICAL_CAPTURE not in context:
            failures.append(relative)

    assert not failures, "Pricing CTA does not emit checkout_clicked in: " + ", ".join(failures)


def test_legacy_analysis_checkout_event_is_absent() -> None:
    offenders = []
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        if LEGACY_CAPTURE in path.read_text(encoding="utf-8"):
            offenders.append(str(path.relative_to(ROOT)))

    assert not offenders, "Legacy checkout event remains in: " + ", ".join(sorted(offenders))
