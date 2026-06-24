from stockgod.analysis.why_now import generate_why_now_why_not


def test_breakout_trigger_appears_in_why_now():
    result = generate_why_now_why_not({"breakout_confirmed": True})
    assert "Breakout confirmed" in result["why_now"]


def test_no_trigger_returns_fallback():
    result = generate_why_now_why_not({})
    assert result["why_now"] == "No urgent trigger; watch only."


def test_earnings_within_five_days_appears_in_why_not():
    result = generate_why_now_why_not({"earnings_within_5_days": True})
    assert "Earnings within 5 days" in result["why_not"]


def test_missing_technical_levels_appears_in_why_not():
    result = generate_why_now_why_not({"missing_technical_levels": True})
    assert "Missing technical levels" in result["why_not"]
