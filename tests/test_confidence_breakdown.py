from stockgod.analysis.confidence_breakdown import build_confidence_breakdown


def test_missing_price_data_returns_no_action():
    result = build_confidence_breakdown({"data_quality": {"price": "missing"}})
    assert result["confidence"] == "No Action"


def test_missing_options_not_penalized_when_not_applicable():
    result = build_confidence_breakdown({"uses_options": False, "data_quality": {"options": "missing"}})
    assert result["breakdown"]["options"] == "not_applicable"
    assert result["confidence"] == "High"


def test_data_disagreement_lowers_confidence():
    result = build_confidence_breakdown({"material_data_disagreement": True})
    assert result["confidence"] == "Medium"
    assert "material data disagreement" in result["why_not_high"]


def test_unverified_insider_reduces_only_when_affects_score():
    ignored = build_confidence_breakdown({"insider_affects_score": False, "data_quality": {"insider": "unverified"}})
    reduced = build_confidence_breakdown({"insider_affects_score": True, "data_quality": {"insider": "unverified"}})
    assert ignored["confidence"] == "High"
    assert reduced["confidence"] == "Medium"


def test_missing_or_stale_earnings_reduces_confidence():
    missing = build_confidence_breakdown({"data_quality": {"earnings": "missing"}})
    estimated = build_confidence_breakdown({"data_quality": {"earnings": "estimated"}})
    assert missing["confidence"] == "Medium"
    assert estimated["confidence"] == "Medium"
