"""Build a fact-only evidence snapshot from normalized provider envelopes.

The snapshot is descriptive only: identity, latest price/volume, the fetched
bar window, earnings date/proximity, optional macro, and a per-category
data-quality map (fresh / stale / missing / confirmed / not_applicable).

It deliberately does NOT compute technical levels, scores, ratings, signals,
or recommendations, and never fabricates a value the providers did not return
(master spec: "no hallucinated levels"; "do not invent ... external-data
behavior"). Inputs are the same normalized envelopes the read-only stock card
consumes, so ``build-input`` and ``stock-card`` share one upstream shape.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

# A daily bar whose date is within this many calendar days of `today` is "fresh".
FRESH_PRICE_DAYS = 5


def build_evidence_snapshot(payload: dict[str, Any], today: date | None = None) -> dict[str, Any]:
    """Return a deterministic fact-only snapshot from provider envelopes.

    ``payload`` matches the read-only stock-card input: ``ticker`` plus optional
    ``profile`` / ``daily_bars`` / ``earnings`` / ``macro`` provider envelopes.
    """
    data = dict(payload or {})
    as_of = today or datetime.now(UTC).date()
    symbol = str(data.get("ticker") or "").upper()

    profile = _envelope_data(data.get("profile"))
    earnings = _envelope_data(data.get("earnings"))
    bars_data = _envelope_data(data.get("daily_bars"))
    macro = _envelope_data(data.get("macro"))

    bars = bars_data.get("bars") if isinstance(bars_data.get("bars"), list) else []
    latest = bars[-1] if bars and isinstance(bars[-1], dict) else {}

    identity = {
        "company_name": profile.get("company_name"),
        "sector": profile.get("sector"),
        "industry": profile.get("industry"),
        "market_cap": profile.get("market_cap"),
    }

    price = {
        "latest_close": latest.get("close"),
        "latest_date": latest.get("date"),
        "latest_volume": latest.get("volume"),
        "window_start": bars[0].get("date") if bars and isinstance(bars[0], dict) else None,
        "window_end": latest.get("date"),
        "bar_count": len(bars),
    }

    earnings_date = earnings.get("date")
    earnings_block = {
        "date": earnings_date,
        "eps_estimated": earnings.get("eps_estimated"),
        "eps_actual": earnings.get("eps_actual"),
        "within_5_days": _within_days(earnings_date, as_of, 5),
    }

    macro_block = None
    observations = macro.get("observations") if isinstance(macro, dict) else None
    if isinstance(observations, list) and observations and isinstance(observations[-1], dict):
        macro_block = {
            "series_id": macro.get("series_id"),
            "value": observations[-1].get("value"),
            "date": observations[-1].get("date"),
        }

    has_price = bool(latest.get("close") is not None)
    has_fundamentals = bool(profile.get("company_name") or profile.get("market_cap") is not None)
    has_earnings = bool(earnings_date)

    data_quality = {
        "price": _price_quality(latest.get("date"), as_of) if has_price else "missing",
        "fundamentals": "fresh" if has_fundamentals else "missing",
        "earnings": "confirmed" if has_earnings else "missing",
        "insider": "null",            # not fetched in this layer
        "options": "not_applicable",  # this is not an options card
        "market_regime": "fresh" if macro_block else "missing",  # honest: only if macro was fetched
        "news": "not_applicable",     # not fetched in this layer
    }

    return {
        "ticker": symbol,
        "as_of": as_of.isoformat(),
        "data_mode": str(data.get("data_mode") or "evidence_read_only"),
        "evidence_only": True,
        "identity": identity,
        "price": price,
        "earnings": earnings_block,
        "macro": macro_block,
        "data_quality": data_quality,
        "missing_key_data": (not has_price) or (not has_fundamentals),
    }


def _envelope_data(envelope: Any) -> dict[str, Any]:
    if isinstance(envelope, dict) and isinstance(envelope.get("data"), dict):
        return envelope["data"]
    return envelope if isinstance(envelope, dict) else {}


def _price_quality(latest_date: Any, as_of: date) -> str:
    parsed = _parse_date(latest_date)
    if parsed is None:
        return "stale"
    return "fresh" if 0 <= (as_of - parsed).days <= FRESH_PRICE_DAYS else "stale"


def _within_days(value: Any, as_of: date, days: int) -> bool:
    parsed = _parse_date(value)
    if parsed is None:
        return False
    delta = (parsed - as_of).days
    return 0 <= delta <= days


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            return None
