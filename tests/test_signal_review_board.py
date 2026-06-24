from stockgod.analysis.signal_review_board import review_signal


def base_signal(**overrides):
    signal = {
        "risk_gate": "none",
        "confidence": "High",
        "missing_key_data": False,
        "earnings_within_5_days": False,
        "event_risk_caveat": False,
        "reward_risk": 2.0,
        "min_reward_risk": 1.5,
        "technical_levels_available": True,
        "data_conflict_unresolved": False,
        "classification_uncertain": False,
        "severe_contradiction": False,
        "market_regime": "Green",
        "why_now": "Breakout confirmed.",
    }
    signal.update(overrides)
    return signal


def test_clean_setup_returns_pass():
    assert review_signal(base_signal())["result"] == "pass"


def test_risk_gate_active_returns_fail():
    result = review_signal(base_signal(risk_gate="capped59"))
    assert result["result"] == "fail"
    assert result["actionability"] == "avoid"


def test_no_action_risk_gate_returns_no_action():
    result = review_signal(base_signal(risk_gate="no_action"))
    assert result["result"] == "no_action"
    assert result["actionability"] == "do_nothing"


def test_low_confidence_with_missing_key_data_returns_no_action():
    result = review_signal(base_signal(confidence="Low", missing_key_data=True))
    assert result["result"] == "no_action"


def test_earnings_without_caveat_blocks_clean_pass():
    result = review_signal(base_signal(earnings_within_5_days=True, event_risk_caveat=False))
    assert result["result"] == "conditional"


def test_low_reward_risk_prevents_pass():
    result = review_signal(base_signal(reward_risk=1.0, min_reward_risk=1.5))
    assert result["result"] == "conditional"
