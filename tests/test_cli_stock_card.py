from stockgod.cli import main


def test_stock_card_cli_with_fixture_renders_read_only_card(capsys):
    assert main(["stock-card", "MSFT", "--input", "tests/fixtures/stock_card_msft.json"]) == 0
    output = capsys.readouterr().out
    assert "STOCK GOD READ-ONLY CARD — MSFT" in output
    assert "no buy/sell signal" in output


def test_stock_card_live_missing_keys_fails_cleanly(monkeypatch, capsys):
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    monkeypatch.delenv("MASSIVE_API_KEY", raising=False)
    assert main(["stock-card", "MSFT", "--live", "--no-macro"]) == 1
    output = capsys.readouterr().out
    assert "Stock card failed:" in output
    assert "FMP_API_KEY" in output
