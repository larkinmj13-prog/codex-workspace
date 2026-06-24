"""Tiny HTTP helpers for injectable read-only provider clients."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from stockgod.data.errors import ProviderRequestError, ProviderResponseError


class UrlLibSession:
    """Minimal session with a requests-like get method."""

    def get(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None, timeout: int = 20):
        query = f"?{urlencode(params or {})}" if params else ""
        request = Request(url + query, headers=headers or {})
        try:
            with urlopen(request, timeout=timeout) as response:  # noqa: S310 - read-only configured provider URL
                return _Response(response.read().decode("utf-8"), response.status)
        except URLError as exc:
            raise ProviderRequestError(str(exc)) from exc


class _Response:
    def __init__(self, text: str, status_code: int) -> None:
        self.text = text
        self.status_code = status_code

    def json(self) -> Any:
        return json.loads(self.text)


def request_json(session: Any, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
    response = session.get(url, params=params or {}, headers=headers or {}, timeout=20)
    if getattr(response, "status_code", 200) >= 400:
        raise ProviderRequestError(f"Provider request failed with status {response.status_code}")
    try:
        return response.json()
    except (TypeError, ValueError) as exc:
        raise ProviderResponseError("Provider returned invalid JSON") from exc


def utc_now() -> str:
    return datetime.now(UTC).isoformat()
