"""Signal Review Board for Phase 1 deterministic setup review."""

from __future__ import annotations

from typing import Any, Literal

ReviewResult = Literal["pass", "conditional", "fail", "no_action"]
Actionability = Literal["actionable", "watch_only", "avoid", "do_nothing"]


def _is_active_risk_gate(risk_gate: str) -> bool:
    return risk_gate not in {"", "none"}


def review_signal(signal: dict[str, Any]) -> dict[str, str]:
    """Evaluate an already-prepared signal without fetching external data."""
    risk_gate = str(signal.get("risk_gate", "none") or "none")
    confidence = str(signal.get("confidence", "") or "")

    if risk_gate == "no_action":
        return _result("no_action", "Risk gate requires no action.", "do_nothing")

    if signal.get("severe_contradiction", False):
        return _result("fail", "Severe contradiction unresolved.", "avoid")

    if _is_active_risk_gate(risk_gate):
        return _result("fail", f"Active risk gate: {risk_gate}.", "avoid")

    if confidence == "Low" and signal.get("missing_key_data", False):
        return _result("no_action", "Low confidence with missing key data.", "do_nothing")

    if signal.get("earnings_within_5_days", False) and not signal.get("event_risk_caveat", False):
        return _result("conditional", "Earnings within 5 days lacks event-risk caveat.", "watch_only")

    reward_risk = signal.get("reward_risk")
    min_reward_risk = signal.get("min_reward_risk")
    if reward_risk is not None and min_reward_risk is not None and reward_risk < min_reward_risk:
        return _result("conditional", "Reward/risk below minimum.", "watch_only")

    if not signal.get("technical_levels_available", True):
        return _result("conditional", "Technical levels unavailable.", "watch_only")

    if signal.get("data_conflict_unresolved", False):
        return _result("conditional", "Unresolved data conflict.", "watch_only")

    if signal.get("classification_uncertain", False):
        return _result("conditional", "Stock classification uncertain.", "watch_only")

    if str(signal.get("market_regime", "Unknown")) == "Black Ice":
        return _result("conditional", "Black Ice market regime requires caution.", "watch_only")

    return _result("pass", "Clean deterministic setup.", "actionable")


def _result(result: ReviewResult, reason: str, actionability: Actionability) -> dict[str, str]:
    return {"result": result, "reason": reason, "actionability": actionability}
