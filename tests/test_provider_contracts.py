import json
from pathlib import Path

from stockgod.data.edgar import normalize_edgar_form4_filings
from stockgod.data.fmp import normalize_fmp_company_profile
from stockgod.data.fred import normalize_fred_series
from stockgod.data.massive import normalize_massive_daily_bars
from stockgod.data.yahoo import normalize_yahoo_quote_snapshot

FIXTURES = Path(__file__).parent / "fixtures" / "providers"


def load(name):
    return json.loads((FIXTURES / name).read_text())


def test_provider_envelope_contract_for_all_normalizers():
    results = [
        normalize_fmp_company_profile(load("fmp_company_profile_msft.json"), "MSFT"),
        normalize_massive_daily_bars(load("massive_daily_bars_spy.json"), "SPY"),
        normalize_edgar_form4_filings(load("edgar_form4_filings_msft.json"), "MSFT"),
        normalize_fred_series(load("fred_dgs10.json"), "DGS10"),
        normalize_yahoo_quote_snapshot(load("yahoo_quote_snapshot_msft.json"), "MSFT"),
    ]
    for result in results:
        assert result["provider"]
        assert result["as_of"]
        assert isinstance(result["data"], dict)
        assert result["raw"] is not None
        assert result.get("symbol") or result.get("series_id")
