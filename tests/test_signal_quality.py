from stockgod.analysis.signal_quality import TIER_RANK, assign_signal_quality


def base_signal(**overrides):
    signal = {
        "risk_gate": "none",
        "confidence": "High",
        "reward_risk": 2.0,
        "min_reward_risk": 1.5,
        "earnings_within_5_days": False,
        "event_risk_caveat": False,
        "severe_contradiction": False,
        "technical_levels_available": True,
        "market_regime": "Green",
        "thesis_strength": "strong",
        "entry_quality": "strong",
        "meaningful_caveats": 0,
    }
    signal.update(overrides)
    return signal


def test_clean_high_quality_setup_returns_a_or_a_plus():
    result = assign_signal_quality(base_signal())
    assert result["tier"] in {"A", "A+"}


def test_low_confidence_caps_tier_at_b():
    result = assign_signal_quality(base_signal(confidence="Low"))
    assert TIER_RANK[result["tier"]] >= TIER_RANK["B"]


def test_risk_gate_caps_tier_at_d_or_f():
    result = assign_signal_quality(base_signal(risk_gate="capped44"))
    assert result["tier"] in {"D", "F"}


def test_low_reward_risk_caps_tier_at_c():
    result = assign_signal_quality(base_signal(reward_risk=1.0, min_reward_risk=1.5))
    assert TIER_RANK[result["tier"]] >= TIER_RANK["C"]


def test_severe_contradiction_caps_tier_at_c():
    result = assign_signal_quality(base_signal(severe_contradiction=True))
    assert TIER_RANK[result["tier"]] >= TIER_RANK["C"]
