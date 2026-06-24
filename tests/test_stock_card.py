import json
from pathlib import Path

from stockgod.reports.stock_card import build_read_only_stock_card


def test_read_only_stock_card_renders_provider_context_without_recommendation_language():
    payload = json.loads((Path(__file__).parent / "fixtures" / "stock_card_msft.json").read_text())
    card = build_read_only_stock_card("MSFT", payload)
    assert "STOCK GOD READ-ONLY CARD — MSFT" in card
    assert "Microsoft Corporation" in card
    assert "Latest Close: 450.12" in card
    assert "Earnings Date: 2026-07-28" in card
    assert "Read-only: no score" in card
    forbidden = ["Buy Setup", "Sell Risk", "recommendation:", "rating:"]
    assert not any(term in card for term in forbidden)
