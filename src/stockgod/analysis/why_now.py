"""Why Now / Why Not text generation for supplied signal fields."""

from __future__ import annotations

from typing import Any

WHY_NOW_MESSAGES = {
    "buy_zone_reached": "Buy zone reached.",
    "breakout_confirmed": "Breakout confirmed.",
    "pullback_into_buy_zone": "Pullback into buy zone.",
    "signal_label_improved": "Signal label improved.",
    "risk_gate_removed": "Risk gate removed.",
    "market_regime_improved": "Market regime improved.",
    "earnings_risk_cleared": "Earnings risk cleared.",
    "qualifying_insider_event": "Qualifying insider event present.",
    "valuation_improved": "Valuation improved.",
    "confidence_improved": "Confidence improved.",
}

WHY_NOT_MESSAGES = {
    "earnings_within_5_days": "Earnings within 5 days.",
    "vix_or_regime_stress": "VIX or regime stress present.",
    "reward_risk_below_threshold": "Reward/risk below threshold.",
    "valuation_stretched": "Valuation stretched.",
    "confidence_low": "Confidence low.",
    "technical_setup_extended": "Technical setup extended.",
    "market_regime_red_or_black_ice": "Market regime Red or Black Ice.",
    "unresolved_contradiction": "Unresolved contradiction.",
    "material_data_disagreement": "Material data disagreement.",
    "missing_technical_levels": "Missing technical levels.",
}

WHY_NOW_FALLBACK = "No urgent trigger; watch only."
WHY_NOT_FALLBACK = "No major caveat identified."


def generate_why_now_why_not(signal: dict[str, Any]) -> dict[str, str]:
    """Generate concise deterministic Why Now / Why Not statements."""
    why_now = _collect_messages(signal, WHY_NOW_MESSAGES) or [WHY_NOW_FALLBACK]
    why_not = _collect_messages(signal, WHY_NOT_MESSAGES) or [WHY_NOT_FALLBACK]
    return {"why_now": " ".join(why_now), "why_not": " ".join(why_not)}


def _collect_messages(signal: dict[str, Any], messages: dict[str, str]) -> list[str]:
    return [message for key, message in messages.items() if bool(signal.get(key, False))]
