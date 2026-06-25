import json
from datetime import date
from pathlib import Path

from stockgod.evidence.build_input import (
    build_evidence_read,
    snapshot_to_engine_input,
)
from stockgod.evidence.snapshot import build_evidence_snapshot

FIXTURES = Path(__file__).parent / "fixtures"
TODAY = date(2026, 6, 24)


def _payload():
    return json.loads((FIXTURES / "stock_card_msft.json").read_text())


def test_snapshot_records_facts_and_data_quality():
    snap = build_evidence_snapshot(_payload(), today=TODAY)
    assert snap["ticker"] == "MSFT"
    assert snap["evidence_only"] is True
    assert snap["identity"]["company_name"] == "Microsoft Corporation"
    assert snap["price"]["latest_close"] == 450.12
    # bar dated 2026-06-23 vs today 2026-06-24 -> fresh
    assert snap["data_quality"]["price"] == "fresh"
    assert snap["data_quality"]["fundamentals"] == "fresh"
    assert snap["data_quality"]["earnings"] == "confirmed"
    # earnings 2026-07-28 is far out -> not within 5 days
    assert snap["earnings"]["within_5_days"] is False
    assert snap["missing_key_data"] is False


def test_snapshot_does_not_fabricate_levels_or_scores():
    snap = build_evidence_snapshot(_payload(), today=TODAY)
    blob = json.dumps(snap).lower()
    for forbidden in ["score", "rating", "buy", "sell", "target", "support", "resistance", "technical_level"]:
        assert forbidden not in blob


def test_stale_price_when_bar_is_old():
    snap = build_evidence_snapshot(_payload(), today=date(2026, 7, 30))
    assert snap["data_quality"]["price"] == "stale"


def test_missing_data_marks_no_action_and_missing_key_data():
    snap = build_evidence_snapshot({"ticker": "GAP"}, today=TODAY)
    assert snap["data_quality"]["price"] == "missing"
    assert snap["missing_key_data"] is True
    signal = snapshot_to_engine_input(snap)
    assert signal["confidence"] == "No Action"


def test_engine_input_leaves_judgment_fields_unset_and_levels_false():
    signal = snapshot_to_engine_input(build_evidence_snapshot(_payload(), today=TODAY))
    assert signal["technical_levels_available"] is False
    assert signal["single_stock_thesis"] is True
    # judgment fields the spec does not define a mapping for must be absent
    for invented in ["thesis_strength", "entry_quality", "reward_risk", "risk_gate", "market_regime", "severe_contradiction"]:
        assert invented not in signal


def test_evidence_read_is_conservative_no_recommendation():
    read = build_evidence_read(build_evidence_snapshot(_payload(), today=TODAY))
    # full fresh data (fixture has macro) -> High data-quality confidence
    assert read["confidence"]["confidence"] == "High"
    # no technical levels computed -> review is conditional / watch_only, never a buy
    assert read["review"]["result"] == "conditional"
    assert read["review"]["actionability"] == "watch_only"
