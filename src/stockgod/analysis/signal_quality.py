"""Signal quality tiers for Phase 1 deterministic review."""

from __future__ import annotations

from typing import Any

TIERS = ["A+", "A", "A-", "B+", "B", "B-", "C", "D", "F"]
TIER_RANK = {tier: index for index, tier in enumerate(TIERS)}


def assign_signal_quality(signal: dict[str, Any]) -> dict[str, str]:
    """Assign a simple quality tier without backtested weighting."""
    tier = _base_tier(signal)
    reasons = [_base_reason(tier)]

    risk_gate = str(signal.get("risk_gate", "none") or "none")
    if risk_gate == "no_action":
        tier = _worse(tier, "F")
        reasons.append("no-action risk gate")
    elif risk_gate not in {"", "none"}:
        tier = _worse(tier, "D")
        reasons.append("active risk gate")

    if str(signal.get("confidence", "")) == "Low":
        tier = _worse(tier, "B")
        reasons.append("Low confidence caps tier at B")

    reward_risk = signal.get("reward_risk")
    min_reward_risk = signal.get("min_reward_risk")
    if reward_risk is not None and min_reward_risk is not None and reward_risk < min_reward_risk:
        tier = _worse(tier, "C")
        reasons.append("reward/risk below threshold caps tier at C")

    if signal.get("earnings_within_5_days", False) and not signal.get("event_risk_caveat", False):
        tier = _worse(tier, "B")
        reasons.append("earnings proximity caps tier at B")

    if signal.get("severe_contradiction", False):
        tier = _worse(tier, "C")
        reasons.append("severe contradiction caps tier at C")

    if not signal.get("technical_levels_available", True):
        tier = _worse(tier, "C")
        reasons.append("missing technical levels caps tier at C")

    market_regime = str(signal.get("market_regime", "Unknown") or "Unknown")
    if market_regime == "Red" and not signal.get("defensive_setup", False):
        tier = _worse(tier, "B")
        reasons.append("Red regime caps tier at B")
    if market_regime == "Black Ice" and not signal.get("danger_or_hedge_setup", False):
        tier = _worse(tier, "C")
        reasons.append("Black Ice regime caps tier at C")

    return {"tier": tier, "reason": "; ".join(reasons) + "."}


def _base_tier(signal: dict[str, Any]) -> str:
    thesis = str(signal.get("thesis_strength", "") or "")
    entry = str(signal.get("entry_quality", "") or "")
    regime = str(signal.get("market_regime", "Unknown") or "Unknown")
    caveats = int(signal.get("meaningful_caveats", 0) or 0)

    if thesis == "strong" and entry == "strong" and regime == "Green" and caveats == 0:
        return "A+"
    if thesis == "strong" and entry in {"strong", "acceptable"} and caveats <= 1:
        return "A"
    if thesis == "strong" and caveats == 1:
        return "A-"
    if thesis in {"good", "strong"} and entry in {"acceptable", "close"}:
        return "B+"
    if thesis in {"good", "strong"}:
        return "B"
    if entry == "needs_confirmation":
        return "B-"
    if signal.get("broken_thesis", False):
        return "F"
    if signal.get("avoid_new_money", False):
        return "D"
    return "C"


def _base_reason(tier: str) -> str:
    meanings = {
        "A+": "strong thesis, strong entry, supportive regime, no risk gate",
        "A": "strong thesis with acceptable entry and minor caveats",
        "A-": "strong setup with one meaningful caveat",
        "B+": "good candidate close to actionable",
        "B": "good but not urgent",
        "B-": "watchlist only; needs confirmation",
        "C": "watch only",
        "D": "avoid new money",
        "F": "sell risk or broken thesis",
    }
    return meanings[tier]


def _worse(current: str, cap: str) -> str:
    return current if TIER_RANK[current] >= TIER_RANK[cap] else cap
