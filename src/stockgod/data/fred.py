"""Read-only FRED macro provider client and normalizers."""

from __future__ import annotations

from typing import Any

from stockgod.data._http import UrlLibSession, request_json, utc_now
from stockgod.data.config import ProviderConfig, load_provider_config
from stockgod.data.errors import MissingApiKeyError, ProviderResponseError


def normalize_fred_series(raw: dict, series_id: str) -> dict:
    observations = raw.get("observations")
    if not isinstance(observations, list):
        raise ProviderResponseError("FRED series response missing observations")
    data = {"series_id": series_id, "observations": [{"date": item.get("date"), "value": item.get("value")} for item in observations]}
    as_of = data["observations"][-1]["date"] if data["observations"] else utc_now()
    return {"provider": "fred", "series_id": series_id, "as_of": as_of, "data": data, "raw": raw}


class FREDClient:
    provider = "fred"

    def __init__(self, config: ProviderConfig | None = None, session: Any | None = None, base_url: str = "https://api.stlouisfed.org/fred") -> None:
        self.config = config or load_provider_config()
        self.session = session or UrlLibSession()
        self.base_url = base_url.rstrip("/")

    def get_series(self, series_id: str) -> dict:
        if not self.config.fred_api_key:
            raise MissingApiKeyError("FRED_API_KEY is required for FRED requests")
        raw = request_json(self.session, f"{self.base_url}/series/observations", {"series_id": series_id, "api_key": self.config.fred_api_key, "file_type": "json"})
        return normalize_fred_series(raw, series_id)
