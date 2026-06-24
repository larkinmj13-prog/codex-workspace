"""Read-only FMP provider client and normalizers."""

from __future__ import annotations

from typing import Any

from stockgod.data._http import UrlLibSession, request_json, utc_now
from stockgod.data.config import ProviderConfig, load_provider_config
from stockgod.data.errors import MissingApiKeyError, ProviderResponseError


def _first(raw: Any) -> dict[str, Any]:
    if isinstance(raw, list):
        return raw[0] if raw and isinstance(raw[0], dict) else {}
    return raw if isinstance(raw, dict) else {}


def _envelope(ticker: str, data: dict[str, Any], raw: Any, as_of: str | None = None) -> dict[str, Any]:
    return {"provider": "fmp", "symbol": ticker.upper(), "ticker": ticker.upper(), "as_of": as_of or utc_now(), "data": data, "raw": raw}


def normalize_fmp_company_profile(raw: dict | list, ticker: str) -> dict:
    item = _first(raw)
    if not item:
        raise ProviderResponseError("FMP company profile response is empty")
    data = {"symbol": item.get("symbol", ticker).upper(), "company_name": item.get("companyName"), "sector": item.get("sector"), "industry": item.get("industry"), "market_cap": item.get("mktCap")}
    return _envelope(ticker, data, raw, item.get("date"))


def normalize_fmp_key_metrics(raw: dict | list, ticker: str) -> dict:
    item = _first(raw)
    if not item:
        raise ProviderResponseError("FMP key metrics response is empty")
    data = {"symbol": item.get("symbol", ticker).upper(), "market_cap": item.get("marketCapTTM") or item.get("marketCap"), "pe_ratio": item.get("peRatioTTM") or item.get("peRatio"), "revenue_per_share": item.get("revenuePerShareTTM")}
    return _envelope(ticker, data, raw, item.get("date"))


def normalize_fmp_financial_ratios(raw: dict | list, ticker: str) -> dict:
    item = _first(raw)
    if not item:
        raise ProviderResponseError("FMP financial ratios response is empty")
    data = {"symbol": item.get("symbol", ticker).upper(), "pe_ratio": item.get("priceEarningsRatioTTM") or item.get("peRatioTTM"), "gross_profit_margin": item.get("grossProfitMarginTTM"), "return_on_equity": item.get("returnOnEquityTTM")}
    return _envelope(ticker, data, raw, item.get("date"))


def normalize_fmp_earnings_calendar(raw: dict | list, ticker: str) -> dict:
    item = _first(raw)
    if not item:
        raise ProviderResponseError("FMP earnings calendar response is empty")
    data = {"symbol": item.get("symbol", ticker).upper(), "date": item.get("date"), "eps_estimated": item.get("epsEstimated"), "eps_actual": item.get("eps")}
    return _envelope(ticker, data, raw, item.get("date"))


class FMPClient:
    provider = "fmp"

    def __init__(self, config: ProviderConfig | None = None, session: Any | None = None, base_url: str = "https://financialmodelingprep.com/api/v3") -> None:
        self.config = config or load_provider_config()
        self.session = session or UrlLibSession()
        self.base_url = base_url.rstrip("/")

    def get_company_profile(self, ticker: str) -> dict:
        return normalize_fmp_company_profile(self._request(f"profile/{ticker}"), ticker)

    def get_key_metrics(self, ticker: str) -> dict:
        return normalize_fmp_key_metrics(self._request(f"key-metrics-ttm/{ticker}"), ticker)

    def get_financial_ratios(self, ticker: str) -> dict:
        return normalize_fmp_financial_ratios(self._request(f"ratios-ttm/{ticker}"), ticker)

    def get_income_statement(self, ticker: str) -> dict:
        return self._get(ticker, f"income-statement/{ticker}")

    def get_balance_sheet(self, ticker: str) -> dict:
        return self._get(ticker, f"balance-sheet-statement/{ticker}")

    def get_cash_flow(self, ticker: str) -> dict:
        return self._get(ticker, f"cash-flow-statement/{ticker}")

    def get_earnings_calendar(self, ticker: str) -> dict:
        return normalize_fmp_earnings_calendar(self._request("historical/earning_calendar", {"symbol": ticker}), ticker)

    def get_insider_discovery(self, ticker: str) -> dict:
        return self._get(ticker, "insider-trading", {"symbol": ticker})

    def _request(self, path: str, params: dict[str, Any] | None = None) -> Any:
        if not self.config.fmp_api_key:
            raise MissingApiKeyError("FMP_API_KEY is required for FMP requests")
        query = dict(params or {}) | {"apikey": self.config.fmp_api_key}
        return request_json(self.session, f"{self.base_url}/{path}", query)

    def _get(self, ticker: str, path: str, params: dict[str, Any] | None = None) -> dict:
        raw = self._request(path, params)
        return {"provider": self.provider, "symbol": ticker.upper(), "ticker": ticker.upper(), "as_of": utc_now(), "data": raw, "raw": raw}
