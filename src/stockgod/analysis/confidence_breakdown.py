"""Confidence breakdown for supplied Phase 2 signal fields."""

from __future__ import annotations

from typing import Any

ORDER = ["No Action", "Low", "Medium", "High"]
RANK = {value: index for index, value in enumerate(ORDER)}

DEFAULT_BREAKDOWN = {
    "price": "fresh",
    "fundamentals": "fresh",
    "earnings": "confirmed",
    "insider": "null",
    "options": "not_applicable",
    "market_regime": "fresh",
    "news": "not_applicable",
}


def build_confidence_breakdown(signal: dict[str, Any]) -> dict[str, Any]:
    """Explain confidence using only supplied data-quality fields."""
    breakdown = DEFAULT_BREAKDOWN | dict(signal.get("data_quality", {}) or {})
    if not signal.get("uses_options", False) and breakdown.get("options") == "missing":
        breakdown["options"] = "not_applicable"

    confidence = str(signal.get("confidence", "High") or "High")
    why_not_high: list[str] = []

    if breakdown["price"] == "missing":
        return _result("No Action", "Conf: NA — price missing", breakdown, ["missing price data"])

    if signal.get("single_stock_thesis", True) and breakdown["fundamentals"] == "missing":
        confidence = _cap(confidence, "Low")
        why_not_high.append("fundamentals missing")
    elif breakdown["fundamentals"] in {"stale", "partial"}:
        confidence = _cap(confidence, "Medium")
        why_not_high.append(f"fundamentals {breakdown['fundamentals']}")

    if breakdown["earnings"] in {"missing", "estimated"}:
        confidence = _cap(confidence, "Medium")
        why_not_high.append(f"earnings {breakdown['earnings']}")

    if signal.get("insider_affects_score", False) and breakdown["insider"] == "unverified":
        confidence = _cap(confidence, "Medium")
        why_not_high.append("insider unverified")

    if signal.get("material_data_disagreement", False):
        confidence = _cap(confidence, "Medium")
        why_not_high.append("material data disagreement")

    if breakdown["market_regime"] in {"stale", "missing"}:
        confidence = _cap(confidence, "Medium")
        why_not_high.append(f"market regime {breakdown['market_regime']}")

    if breakdown["news"] == "stale":
        confidence = _cap(confidence, "Medium")
        why_not_high.append("news stale")

    short_reason = _short_reason(confidence, breakdown, why_not_high)
    return _result(confidence, short_reason, breakdown, why_not_high)


def _cap(current: str, cap: str) -> str:
    return current if RANK.get(current, 0) <= RANK[cap] else cap


def _short_reason(confidence: str, breakdown: dict[str, str], why_not_high: list[str]) -> str:
    label = {"High": "H", "Medium": "M", "Low": "L", "No Action": "NA"}[confidence]
    if why_not_high:
        return f"Conf: {label} — {why_not_high[0]}"
    return f"Conf: {label} — fundamentals {breakdown['fundamentals']}, options {breakdown['options'].replace('_', ' ')}"


def _result(confidence: str, short_reason: str, breakdown: dict[str, str], why_not_high: list[str]) -> dict[str, Any]:
    return {"confidence": confidence, "short_reason": short_reason, "breakdown": breakdown, "why_not_high": why_not_high}
