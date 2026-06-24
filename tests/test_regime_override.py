from stockgod.analysis.regime_override import build_regime_override


def test_vix_12_5_returns_complacency_context_but_no_sell_signal():
    result = build_regime_override({"vix": 12.5})
    assert result["regime_adjustment"] == "complacency_watch"
    assert result["standalone_signal"] is False
    assert result["final_signal"] != "sell_risk"


def test_vix_35_returns_panic_context_but_no_strong_buy_signal():
    result = build_regime_override({"vix": 35})
    assert result["regime_adjustment"] == "black_ice"
    assert result["standalone_signal"] is False
    assert result["final_signal"] != "buy_setup"


def test_vix_35_raises_confirmation_requirements():
    result = build_regime_override({"vix": 35})
    assert result["requires_confirmation"] is True
    assert result["min_confidence_required"] == "High"


def test_vix_above_20_raises_requirements():
    result = build_regime_override({"vix": 22})
    assert result["regime_adjustment"] == "raise_rr_threshold"
    assert result["min_rr_required"] == 2.0


def test_vix_above_25_suppresses_marginal_buys():
    result = build_regime_override({"vix": 27})
    assert result["regime_adjustment"] == "suppress_marginal_buys"


def test_vix_above_30_context_only_not_standalone_buy_sell():
    result = build_regime_override({"vix": 31})
    assert result["regime_adjustment"] == "black_ice"
    assert result["standalone_signal"] is False
    assert result["final_signal"] == "none"


def test_missing_vix_term_structure_does_not_infer_inversion():
    result = build_regime_override({"vix": 35})
    assert result["term_structure"] == "missing"


def test_no_vix_only_input_can_produce_final_buy_or_sell():
    for vix in [12.5, 18, 22, 27, 35, 45]:
        result = build_regime_override({"vix": vix})
        assert result["final_signal"] not in {"buy_setup", "sell_risk"}
