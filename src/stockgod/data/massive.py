"""Read-only Massive market-data provider client and normalizers."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from stockgod.data._http import UrlLibSession, request_json, utc_now
from stockgod.data.config import ProviderConfig, load_provider_config
from stockgod.data.errors import MissingApiKeyError, ProviderResponseError


def _timestamp(value: Any) -> str:
    if isinstance(value, int | float):
        return datetime.fromtimestamp(value / 1000, tz=UTC).date().isoformat()
    return str(value) if value else utc_now()


def normalize_massive_daily_bars(raw: dict, ticker: str) -> dict:
    rows = raw.get("results")
    if not isinstance(rows, list):
        raise ProviderResponseError("Massive daily bars response missing results")
    bars = []
    for row in rows:
        required = {"t", "o", "h", "l", "c", "v"}
        if not required.issubset(row):
            raise ProviderResponseError("Massive daily bar missing required OHLCV fields")
        bars.append({"date": _timestamp(row["t"]), "open": row["o"], "high": row["h"], "low": row["l"], "close": row["c"], "volume": row["v"]})
    return {"provider": "massive", "symbol": ticker.upper(), "ticker": ticker.upper(), "as_of": bars[-1]["date"] if bars else utc_now(), "data": {"symbol": ticker.upper(), "bars": bars}, "raw": raw}


def normalize_massive_quote_snapshot(raw: dict, ticker: str) -> dict:
    container = raw.get("ticker", raw)
    trade = container.get("lastTrade", {}) if isinstance(container, dict) else {}
    data = {"symbol": ticker.upper(), "last_price": trade.get("p") or container.get("last_price"), "timestamp": trade.get("t") or container.get("timestamp")}
    return {"provider": "massive", "symbol": ticker.upper(), "ticker": ticker.upper(), "as_of": _timestamp(data["timestamp"]), "data": data, "raw": raw}


class MassiveClient:
    provider = "massive"

    def __init__(self, config: ProviderConfig | None = None, session: Any | None = None, base_url: str = "https://api.massive.com") -> None:
        self.config = config or load_provider_config()
        self.session = session or UrlLibSession()
        self.base_url = base_url.rstrip("/")

    def get_daily_bars(self, ticker: str, start: str | None = None, end: str | None = None) -> dict:
        if not self.config.massive_api_key:
            raise MissingApiKeyError("MASSIVE_API_KEY is required for Massive requests")
        today = datetime.now(UTC).date()
        frm = start or (today - timedelta(days=10)).isoformat()
        to = end or today.isoformat()
        params = {"apiKey": self.config.massive_api_key, "adjusted": "true", "sort": "asc", "limit": 50}
        url = f"{self.base_url}/v2/aggs/ticker/{ticker.upper()}/range/1/day/{frm}/{to}"
        raw = request_json(self.session, url, params)
        return normalize_massive_daily_bars(raw, ticker)

    def get_quote_snapshot(self, ticker: str) -> dict:
        if not self.config.massive_api_key:
            raise MissingApiKeyError("MASSIVE_API_KEY is required for Massive requests")
        raw = request_json(self.session, f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker.upper()}", {"apiKey": self.config.massive_api_key})
        return normalize_massive_quote_snapshot(raw, ticker)
