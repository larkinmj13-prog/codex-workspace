from stockgod.reports.daily_pop import build_daily_pop_report


def base_signal(**overrides):
    signal = {
        "ticker": "BASE",
        "risk_gate": "none",
        "confidence": "High",
        "technical_levels_available": True,
        "reward_risk": 2.0,
        "min_reward_risk": 1.5,
        "market_regime": "Green",
        "why_now": "No urgent trigger; watch only.",
        "why_not": "No major caveat identified.",
    }
    signal.update(overrides)
    return signal


def test_excludes_stale_already_good_names_with_no_material_change():
    report = build_daily_pop_report([base_signal(ticker="STALE")], {"date": "2026-06-23"})
    assert "No qualifying pops today." in report
    assert "STALE" not in report


def test_includes_ticker_with_signal_label_change():
    report = build_daily_pop_report([base_signal(ticker="NVDA", signal_label_changed=True)], {"date": "2026-06-23"})
    assert "NVDA" in report
    assert "Why Now:" in report
    assert "Why Not:" in report


def test_includes_danger_despite_failing_buy_setup_review():
    report = build_daily_pop_report([
        base_signal(ticker="RISK", risk_gate="capped44", risk_gate_changed=True, confidence="Low")
    ], {"date": "2026-06-23"})
    assert "6. DANGER / RISK-GATE CHANGES" in report
    assert "RISK" in report


def test_requires_why_now_and_why_not():
    report = build_daily_pop_report([base_signal(ticker="BO", breakout_confirmed=True)], {"date": "2026-06-23"})
    assert "Why Now:" in report
    assert "Why Not:" in report


def test_respects_max_names_preference():
    signals = [base_signal(ticker=f"T{i}", signal_label_changed=True) for i in range(3)]
    report = build_daily_pop_report(signals, {"date": "2026-06-23", "max_names": 2})
    assert "T0" in report and "T1" in report
    assert "T2" not in report


def test_returns_no_qualifying_pops_when_nothing_qualifies():
    report = build_daily_pop_report([], {"date": "2026-06-23"})
    assert "No qualifying pops today." in report
