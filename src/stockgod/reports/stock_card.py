"""Read-only stock card renderer for Phase 5."""

from __future__ import annotations

from typing import Any

from stockgod.data.fmp import FMPClient
from stockgod.data.fred import FREDClient
from stockgod.data.massive import MassiveClient


def fetch_live_stock_card_inputs(ticker: str, include_macro: bool = True) -> dict[str, Any]:
    """Fetch read-only provider envelopes for the first live stock card."""
    symbol = ticker.upper()
    payload: dict[str, Any] = {
        "ticker": symbol,
        "data_mode": "live_read_only",
        "profile": FMPClient().get_company_profile(symbol),
        "earnings": FMPClient().get_earnings_calendar(symbol),
        "daily_bars": MassiveClient().get_daily_bars(symbol),
    }
    if include_macro:
        payload["macro"] = FREDClient().get_series("DGS10")
    return payload


def build_read_only_stock_card(ticker: str, payload: dict[str, Any] | None = None) -> str:
    """Render a concise read-only stock card from supplied normalized provider envelopes."""
    data = dict(payload or {})
    symbol = str(data.get("ticker") or ticker).upper()
    profile = _envelope_data(data.get("profile"))
    earnings = _envelope_data(data.get("earnings"))
    bars = _envelope_data(data.get("daily_bars"))
    macro = _envelope_data(data.get("macro"))

    latest_bar = _latest_bar(bars)
    lines = [
        f"STOCK GOD READ-ONLY CARD — {symbol}",
        "",
        f"Data Mode: {data.get('data_mode', 'supplied_read_only')}",
        f"Company: {profile.get('company_name') or 'Unknown'}",
        f"Sector: {profile.get('sector') or 'Unknown'} · Industry: {profile.get('industry') or 'Unknown'}",
        f"Market Cap: {_fmt(profile.get('market_cap'))}",
        f"Latest Close: {_fmt(latest_bar.get('close'))} as of {latest_bar.get('date', 'unknown')}",
        f"Volume: {_fmt(latest_bar.get('volume'))}",
        f"Earnings Date: {earnings.get('date') or 'unknown'}",
        f"Macro DGS10: {_latest_macro_value(macro)}",
        "",
        "Read-only: no score, no rating, no buy/sell signal, no technical levels, no recommendation.",
    ]
    return "\n".join(lines) + "\n"


def _envelope_data(envelope: Any) -> dict[str, Any]:
    if isinstance(envelope, dict) and isinstance(envelope.get("data"), dict):
        return envelope["data"]
    return envelope if isinstance(envelope, dict) else {}


def _latest_bar(data: dict[str, Any]) -> dict[str, Any]:
    bars = data.get("bars")
    if isinstance(bars, list) and bars:
        return bars[-1] if isinstance(bars[-1], dict) else {}
    return {}


def _latest_macro_value(data: dict[str, Any]) -> str:
    observations = data.get("observations")
    if isinstance(observations, list) and observations:
        latest = observations[-1]
        if isinstance(latest, dict):
            return f"{latest.get('value', 'unknown')} as of {latest.get('date', 'unknown')}"
    return "unknown"


def _fmt(value: Any) -> str:
    if value is None or value == "":
        return "unknown"
    if isinstance(value, int | float):
        return f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
    return str(value)
