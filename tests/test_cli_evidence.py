import json

from stockgod.cli import main

FIXTURE = "tests/fixtures/stock_card_msft.json"
WATCHLIST = "tests/fixtures/evidence/watchlist_payloads.json"


def test_build_input_emits_engine_input_json(capsys):
    assert main(["build-input", "MSFT", "--input", FIXTURE, "--as-of", "2026-06-24"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["ticker"] == "MSFT"
    assert out["technical_levels_available"] is False
    assert out["single_stock_thesis"] is True
    assert "confidence" in out


def test_build_input_snapshot_flag_emits_snapshot(capsys):
    assert main(["build-input", "MSFT", "--input", FIXTURE, "--as-of", "2026-06-24", "--snapshot"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["evidence_only"] is True
    assert out["data_quality"]["price"] == "fresh"


def test_analyze_renders_read_only_evidence(capsys):
    assert main(["analyze", "MSFT", "--input", FIXTURE, "--as-of", "2026-06-24"]) == 0
    out = capsys.readouterr().out
    assert "STOCK GOD EVIDENCE READ — MSFT" in out
    assert "Confidence (data quality): High" in out
    assert "Review: conditional" in out
    assert "no score" in out.lower()
    # the read must not emit an actual signal label / recommendation
    for forbidden in ["Buy Setup", "Elite Buy Setup", "Sell Risk", "Recommendation:"]:
        assert forbidden not in out


def test_watchlist_digest_is_bounded_to_supplied_tickers(capsys):
    assert main(["watchlist-digest", "--input", WATCHLIST, "--as-of", "2026-06-24"]) == 0
    out = capsys.readouterr().out
    assert "WATCHLIST EVIDENCE DIGEST" in out
    assert "MSFT:" in out
    assert "GAP:" in out
    assert "missing key data" in out  # the GAP ticker has no provider data
    assert "Bounded to the supplied tickers" in out


def test_analyze_live_missing_keys_fails_cleanly(monkeypatch, capsys):
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    monkeypatch.delenv("MASSIVE_API_KEY", raising=False)
    assert main(["analyze", "MSFT", "--live", "--no-macro"]) == 1
    out = capsys.readouterr().out
    assert "analyze failed:" in out
    assert "FMP_API_KEY" in out


def test_watchlist_digest_requires_input_or_tickers(capsys):
    import pytest
    with pytest.raises(SystemExit):
        main(["watchlist-digest", "--as-of", "2026-06-24"])
    assert "requires --tickers" in capsys.readouterr().err
