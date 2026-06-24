"""Yahoo fallback/sanity-check provider and normalizers."""

from __future__ import annotations

from typing import Any

from stockgod.data._http import utc_now
from stockgod.data.config import ProviderConfig, load_provider_config
from stockgod.data.errors import ProviderNotImplementedError


def normalize_yahoo_quote_snapshot(raw: dict, ticker: str) -> dict:
    data = {"symbol": (raw.get("symbol") or ticker).upper(), "last_price": raw.get("last_price") or raw.get("lastPrice") or raw.get("regularMarketPrice"), "timestamp": raw.get("timestamp") or raw.get("regularMarketTime")}
    return {"provider": "yahoo", "symbol": ticker.upper(), "ticker": ticker.upper(), "as_of": str(data["timestamp"] or utc_now()), "data": data, "raw": raw}


class YahooFallbackClient:
    provider = "yahoo"

    def __init__(self, config: ProviderConfig | None = None, yfinance_module: Any | None = None) -> None:
        self.config = config or load_provider_config()
        self._yfinance = yfinance_module

    def get_quote_snapshot(self, ticker: str) -> dict:
        yf = self._load_yfinance()
        raw = yf.Ticker(ticker).fast_info
        data = dict(raw) if not isinstance(raw, dict) else raw
        data.setdefault("symbol", ticker.upper())
        return normalize_yahoo_quote_snapshot(data, ticker)

    def _load_yfinance(self) -> Any:
        if not self.config.yahoo_fallback_enabled:
            raise ProviderNotImplementedError("Yahoo fallback is disabled")
        if self._yfinance is not None:
            return self._yfinance
        try:
            import yfinance as yf  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ProviderNotImplementedError("Yahoo fallback requires optional dependency yfinance") from exc
        return yf
