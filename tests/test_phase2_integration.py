import pytest

from stockgod.analysis.confidence_breakdown import build_confidence_breakdown
from stockgod.analysis.data_disagreements import detect_data_disagreements
from stockgod.analysis.regime_override import build_regime_override
from stockgod.cli import load_json_input, main
from stockgod.reports.daily_pop import build_daily_pop_report


def test_confidence_data_disagreement_lowers_confidence():
    alerts = detect_data_disagreements(
        {"provider": "fmp", "forward_pe": 22.5},
        {"provider": "yahoo", "forward_pe": 34.0},
        "fundamentals",
    )
    result = build_confidence_breakdown({"confidence": "High", "material_data_disagreement": bool(alerts)})

    assert alerts
    assert result["confidence"] == "Medium"
    assert "material data disagreement" in result["why_not_high"]


def test_confidence_daily_pop_excludes_low_and_includes_high():
    report = build_daily_pop_report(
        [
            {
                "ticker": "LOWQ",
                "material_change": True,
                "confidence": "Low",
                "risk_gate": "none",
                "technical_levels_available": True,
                "why_now": "Signal changed.",
                "why_not": "Low confidence.",
            },
            {
                "ticker": "HIGHQ",
                "material_change": True,
                "confidence": "High",
                "risk_gate": "none",
                "technical_levels_available": True,
                "reward_risk": 2.0,
                "min_reward_risk": 1.5,
                "why_now": "Signal changed.",
                "why_not": "No major caveat identified.",
            },
        ],
        {"date": "2026-06-23"},
    )

    assert "HIGHQ" in report
    assert "LOWQ" not in report


def test_regime_override_daily_pop_suppresses_marginal_but_allows_elite():
    override = build_regime_override({"vix": 27})
    report = build_daily_pop_report(
        [
            {
                "ticker": "MARG",
                "material_change": True,
                "marginal_buy_setup": True,
                "confidence": "Medium",
                "risk_gate": "none",
                "technical_levels_available": True,
                "why_now": "Buy setup appeared.",
                "why_not": "VIX suppresses marginal buys.",
            },
            {
                "ticker": "ELITE",
                "material_change": True,
                "marginal_buy_setup": True,
                "elite_setup": True,
                "confidence": "High",
                "risk_gate": "none",
                "technical_levels_available": True,
                "reward_risk": 3.0,
                "min_reward_risk": 2.0,
                "why_now": "Elite setup held up in stress.",
                "why_not": "Confirmation still required.",
            },
        ],
        {"date": "2026-06-23", "regime_override": override},
    )

    assert "ELITE" in report
    assert "MARG" not in report


def test_vix_extremes_rule_remains_contextual():
    low = build_regime_override({"vix": 12.5})
    high = build_regime_override({"vix": 35})

    assert low["regime_adjustment"] == "complacency_watch"
    assert low["final_signal"] != "sell_risk"
    assert high["regime_adjustment"] == "black_ice"
    assert high["final_signal"] != "buy_setup"
    assert low["standalone_signal"] is False
    assert high["standalone_signal"] is False


def test_data_disagreement_insider_edgar_wins():
    alerts = detect_data_disagreements(
        {"provider": "fmp", "transaction_code": "P"},
        {"provider": "edgar", "transaction_code": "M"},
        "insider_verification",
    )

    assert alerts[0]["resolved_value_source"] == "edgar"
    assert "Insider signal ignored" in alerts[0]["message"]


def test_cli_json_fixtures_run(capsys):
    assert main(["pop", "--input", "tests/fixtures/phase2_pop_input.json"]) == 0
    assert "MSFT" in capsys.readouterr().out

    assert main(["confidence", "--input", "tests/fixtures/phase2_confidence_input.json"]) == 0
    assert "Conf: H" in capsys.readouterr().out

    assert main(["data-check", "--input", "tests/fixtures/phase2_data_check_input.json"]) == 0
    assert "confidence reduced" in capsys.readouterr().out

    assert main(["regime-override", "--input", "tests/fixtures/phase2_regime_override_input.json"]) == 0
    assert "Standalone signal: False" in capsys.readouterr().out


def test_load_json_input_missing_path_fails_gracefully(tmp_path):
    with pytest.raises(ValueError, match="Input JSON not found"):
        load_json_input(tmp_path / "missing.json")


def test_load_json_input_invalid_json_fails_gracefully(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_json_input(path)


def test_cli_missing_json_path_exits_with_clear_error(tmp_path, capsys):
    with pytest.raises(SystemExit):
        main(["confidence", "--input", str(tmp_path / "missing.json")])
    captured = capsys.readouterr()
    assert "Input JSON not found" in captured.err


def test_cli_invalid_json_exits_with_clear_error(tmp_path, capsys):
    path = tmp_path / "bad.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(SystemExit):
        main(["confidence", "--input", str(path)])
    captured = capsys.readouterr()
    assert "Invalid JSON" in captured.err
