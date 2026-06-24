from stockgod.cli import main


def test_provider_check_cli_handles_missing_keys_gracefully(capsys, monkeypatch):
    monkeypatch.delenv("FMP_API_KEY", raising=False)
    assert main(["provider-check", "fmp", "--ticker", "MSFT"]) == 1
    output = capsys.readouterr().out
    assert "Provider check failed:" in output
    assert "FMP_API_KEY" in output


def test_provider_check_cli_does_not_dump_full_raw_payload(capsys, monkeypatch):
    monkeypatch.setenv("FMP_API_KEY", "key")

    class Response:
        status_code = 200
        def json(self):
            return {"very_large_raw_payload": "hidden"}

    class Session:
        def get(self, url, params=None, headers=None, timeout=20):
            return Response()

    from stockgod.data import fmp
    monkeypatch.setattr(fmp, "UrlLibSession", lambda: Session())
    assert main(["provider-check", "fmp", "--ticker", "MSFT"]) == 0
    output = capsys.readouterr().out
    assert "Provider: fmp" in output
    assert "Fields:" in output
    assert "very_large_raw_payload" not in output
