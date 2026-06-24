"""Opt-in live provider smoke tests for Phase 4C.

These tests are skipped unless RUN_LIVE_PROVIDER_SMOKE=1 is set. They are intended
only for a developer machine or CI job with real read-only provider credentials.
"""

from __future__ import annotations

import os

import pytest

from stockgod.data.edgar import EdgarClient
from stockgod.data.errors import ProviderError
from stockgod.data.fmp import FMPClient
from stockgod.data.fred import FREDClient
from stockgod.data.massive import MassiveClient

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_LIVE_PROVIDER_SMOKE") != "1",
    reason="set RUN_LIVE_PROVIDER_SMOKE=1 with provider keys to run live smoke tests",
)


def _assert_provider_envelope(result: dict, provider: str) -> None:
    assert result["provider"] == provider
    assert result["as_of"]
    assert isinstance(result["data"], dict)
    assert result["raw"] is not None
    assert result.get("symbol") or result.get("series_id") or result.get("cik")


def _require_env(name: str) -> None:
    if not os.environ.get(name):
        pytest.skip(f"{name} is not configured")


def test_live_fmp_company_profile_smoke() -> None:
    _require_env("FMP_API_KEY")
    result = FMPClient().get_company_profile("MSFT")
    _assert_provider_envelope(result, "fmp")


def test_live_massive_daily_bars_smoke() -> None:
    _require_env("MASSIVE_API_KEY")
    result = MassiveClient().get_daily_bars("SPY")
    _assert_provider_envelope(result, "massive")


def test_live_edgar_company_submissions_smoke() -> None:
    _require_env("SEC_USER_AGENT")
    result = EdgarClient().get_company_submissions("0000789019")
    _assert_provider_envelope(result, "sec_edgar")


def test_live_fred_dgs10_smoke() -> None:
    _require_env("FRED_API_KEY")
    result = FREDClient().get_series("DGS10")
    _assert_provider_envelope(result, "fred")


def test_live_provider_errors_are_clean() -> None:
    try:
        FMPClient().get_company_profile("MSFT")
    except ProviderError as exc:
        assert str(exc)
