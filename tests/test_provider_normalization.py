import json
from pathlib import Path

import pytest

from stockgod.data.edgar import normalize_edgar_company_submissions, normalize_edgar_form4_filings
from stockgod.data.errors import ProviderResponseError
from stockgod.data.fmp import (
    normalize_fmp_company_profile,
    normalize_fmp_earnings_calendar,
    normalize_fmp_financial_ratios,
    normalize_fmp_key_metrics,
)
from stockgod.data.fred import normalize_fred_series
from stockgod.data.massive import normalize_massive_daily_bars, normalize_massive_quote_snapshot
from stockgod.data.yahoo import normalize_yahoo_quote_snapshot

FIXTURES = Path(__file__).parent / "fixtures" / "providers"


def load(name):
    return json.loads((FIXTURES / name).read_text())


def assert_symbol_envelope(envelope, provider, symbol):
    assert envelope["provider"] == provider
    assert envelope["symbol"] == symbol
    assert envelope["as_of"]
    assert isinstance(envelope["data"], dict)
    assert envelope["raw"] is not None


def test_fmp_company_profile_normalizes_core_fields():
    result = normalize_fmp_company_profile(load("fmp_company_profile_msft.json"), "MSFT")
    assert_symbol_envelope(result, "fmp", "MSFT")
    assert result["data"]["company_name"] == "Microsoft Corporation"
    assert result["data"]["sector"] == "Technology"
    assert result["data"]["market_cap"] == 3000000000000


def test_fmp_key_metrics_and_ratios_normalize_core_fields():
    metrics = normalize_fmp_key_metrics(load("fmp_key_metrics_msft.json"), "MSFT")
    ratios = normalize_fmp_financial_ratios(load("fmp_financial_ratios_msft.json"), "MSFT")
    assert metrics["data"]["pe_ratio"] == 34.2
    assert ratios["data"]["gross_profit_margin"] == 0.69


def test_fmp_earnings_calendar_normalizes_dates():
    result = normalize_fmp_earnings_calendar(load("fmp_earnings_calendar_msft.json"), "MSFT")
    assert result["data"]["date"] == "2026-07-28"
    assert result["data"]["eps_estimated"] == 3.2


def test_massive_daily_bars_and_quote_normalize():
    bars = normalize_massive_daily_bars(load("massive_daily_bars_spy.json"), "SPY")
    quote = normalize_massive_quote_snapshot(load("massive_quote_snapshot_spy.json"), "SPY")
    assert_symbol_envelope(bars, "massive", "SPY")
    assert bars["data"]["bars"][0]["close"] == 553.0
    assert quote["data"]["last_price"] == 553.0


def test_massive_missing_required_bar_fields_raises_clean_error():
    with pytest.raises(ProviderResponseError):
        normalize_massive_daily_bars({"results": [{"t": 1, "o": 1}]}, "SPY")


def test_edgar_submissions_and_form4_normalize_partial_metadata():
    raw = load("edgar_form4_filings_msft.json")
    submissions = normalize_edgar_company_submissions(raw, "MSFT")
    form4 = normalize_edgar_form4_filings(raw, "MSFT")
    assert submissions["provider"] == "sec_edgar"
    assert submissions["data"]["name"] == "MICROSOFT CORP"
    assert form4["data"]["form4_filings"][0]["accession_number"] == "0000789019-26-000001"


def test_fred_series_normalizes_observations_and_requires_observations():
    result = normalize_fred_series(load("fred_dgs10.json"), "DGS10")
    assert result["provider"] == "fred"
    assert result["series_id"] == "DGS10"
    assert result["data"]["observations"][0]["value"] == "4.25"
    with pytest.raises(ProviderResponseError):
        normalize_fred_series({}, "DGS10")


def test_yahoo_quote_snapshot_normalizes():
    result = normalize_yahoo_quote_snapshot(load("yahoo_quote_snapshot_msft.json"), "MSFT")
    assert_symbol_envelope(result, "yahoo", "MSFT")
    assert result["data"]["last_price"] == 450.12
