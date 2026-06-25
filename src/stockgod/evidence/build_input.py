"""Map a fact-only evidence snapshot to deterministic-engine inputs and run them.

This is the bridge between real provider data and the existing Phase 1-3 engine.
It populates ONLY fields that are factually determinable from the snapshot
(data quality, earnings proximity, whether key data is missing). Judgment fields
the master spec does not define a mapping for -- ``thesis_strength``,
``entry_quality``, ``reward_risk``, ``risk_gate``, ``market_regime``,
``severe_contradiction`` -- are intentionally left unset so the deterministic
engine applies its own conservative defaults. ``technical_levels_available`` is
always ``False`` because this layer never computes price levels.

The result is therefore read-only and conservative: it surfaces real evidence
and a data-quality confidence label, and never emits a score, rating, target,
technical level, or buy/sell recommendation.
"""

from __future__ import annotations

from typing import Any

from stockgod.analysis.confidence_breakdown import build_confidence_breakdown
from stockgod.analysis.signal_quality import assign_signal_quality
from stockgod.analysis.signal_review_board import review_signal


def snapshot_to_engine_input(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Return the deterministic-engine signal dict for a snapshot (with confidence)."""
    signal = _base_engine_signal(snapshot)
    signal["confidence"] = build_confidence_breakdown(signal)["confidence"]
    return signal


def build_evidence_read(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Run the deterministic engine on snapshot facts; return a conservative read."""
    signal = _base_engine_signal(snapshot)
    breakdown = build_confidence_breakdown(signal)
    signal["confidence"] = breakdown["confidence"]
    return {
        "ticker": snapshot.get("ticker"),
        "as_of": snapshot.get("as_of"),
        "engine_input": signal,
        "confidence": breakdown,
        "review": review_signal(signal),
        "signal_quality": assign_signal_quality(signal),
    }


def render_evidence_read(read: dict[str, Any], snapshot: dict[str, Any]) -> str:
    """Render a concise, explicitly read-only evidence summary."""
    identity = snapshot.get("identity", {})
    price = snapshot.get("price", {})
    earnings = snapshot.get("earnings", {})
    review = read["review"]
    lines = [
        f"STOCK GOD EVIDENCE READ — {read['ticker']}",
        "",
        f"As Of: {read.get('as_of', 'unknown')}",
        f"Company: {identity.get('company_name') or 'Unknown'}",
        f"Sector: {identity.get('sector') or 'Unknown'} · Industry: {identity.get('industry') or 'Unknown'}",
        f"Latest Close: {_fmt(price.get('latest_close'))} as of {price.get('latest_date', 'unknown')}",
        f"Earnings Date: {earnings.get('date') or 'unknown'}"
        + (" (within 5 days)" if earnings.get("within_5_days") else ""),
        "",
        f"Confidence (data quality): {read['confidence']['confidence']} — {read['confidence']['short_reason']}",
        f"Review: {review['result']} ({review['actionability']}) — {review['reason']}",
        f"Signal quality: {read['signal_quality']['tier']}",
        "",
        "Evidence only: data-quality confidence and a conservative review of supplied facts. "
        "No score, rating, price target, technical level, or buy/sell recommendation. "
        "Judgment inputs not defined by the source-of-truth spec are left unset.",
    ]
    return "\n".join(lines) + "\n"


def build_watchlist_digest(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build a bounded, evidence-only digest for an explicit list of tickers."""
    return [build_evidence_read(snap) for snap in snapshots]


def render_watchlist_digest(reads: list[dict[str, Any]], as_of: str) -> str:
    """Render the bounded digest. Not a screen: only the supplied tickers appear."""
    lines = [f"WATCHLIST EVIDENCE DIGEST — {as_of}", ""]
    if not reads:
        lines.append("No tickers supplied.")
        return "\n".join(lines) + "\n"
    for read in reads:
        review = read["review"]
        flags = []
        if read["engine_input"].get("earnings_within_5_days"):
            flags.append("earnings within 5 days")
        if read["engine_input"].get("missing_key_data"):
            flags.append("missing key data")
        flag_text = ("; ".join(flags)) if flags else "none"
        lines.append(
            f"{read['ticker']}: confidence {read['confidence']['confidence']} · "
            f"review {review['result']}/{review['actionability']} · flags: {flag_text}"
        )
    lines.extend([
        "",
        "Bounded to the supplied tickers only (no universe scan). Evidence/data-quality "
        "and factual flags only — no scores, ratings, technical levels, or buy/sell signals.",
    ])
    return "\n".join(lines) + "\n"


def _base_engine_signal(snapshot: dict[str, Any]) -> dict[str, Any]:
    earnings = snapshot.get("earnings", {}) if isinstance(snapshot.get("earnings"), dict) else {}
    return {
        "ticker": snapshot.get("ticker"),
        "single_stock_thesis": True,
        "uses_options": False,
        "data_quality": dict(snapshot.get("data_quality", {}) or {}),
        "earnings_within_5_days": bool(earnings.get("within_5_days")),
        "event_risk_caveat": False,
        "missing_key_data": bool(snapshot.get("missing_key_data")),
        # Never computed by this layer -> the engine treats the setup conservatively:
        "technical_levels_available": False,
    }


def _fmt(value: Any) -> str:
    if value is None or value == "":
        return "unknown"
    if isinstance(value, int | float):
        return f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
    return str(value)
