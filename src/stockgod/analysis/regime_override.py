"""VIX / market regime override logic for supplied Phase 2 fields."""

from __future__ import annotations

from typing import Any


def build_regime_override(signal: dict[str, Any]) -> dict[str, Any]:
    """Build contextual VIX override guidance without standalone buy/sell signals."""
    vix = signal.get("vix")
    term_structure = signal.get("vix_term_structure", "missing")
    base = {"override_active": False, "regime_adjustment": "none", "reason": "VIX unavailable; no regime override.", "min_rr_required": None, "min_confidence_required": None, "standalone_signal": False, "term_structure": term_structure or "missing", "requires_confirmation": False, "final_signal": "none"}
    if vix is None:
        return base

    vix = float(vix)
    result = base | {"override_active": True, "reason": "VIX normal; use standard thresholds."}

    if vix <= 13:
        result |= {"regime_adjustment": "complacency_watch", "reason": "VIX at complacency extreme; watch reversal risk, no standalone sell signal.", "min_rr_required": None, "min_confidence_required": None}
    elif vix <= 18:
        result |= {"override_active": False, "reason": "VIX calm/risk-on support; normal thresholds."}
    elif vix <= 20:
        result |= {"regime_adjustment": "raise_rr_threshold", "reason": "VIX 18-20; slightly stricter entries.", "min_rr_required": 1.7, "min_confidence_required": "Medium", "requires_confirmation": True}
    elif vix <= 25:
        result |= {"regime_adjustment": "raise_rr_threshold", "reason": "VIX above 20; require better R:R and confirmation.", "min_rr_required": 2.0, "min_confidence_required": "Medium", "requires_confirmation": True}
    elif vix <= 30:
        result |= {"regime_adjustment": "suppress_marginal_buys", "reason": "VIX above 25; suppress marginal Buy Setups.", "min_rr_required": 2.0, "min_confidence_required": "Medium", "requires_confirmation": True}
    elif vix < 40:
        adjustment = "black_ice" if vix > 30 else "panic_watch"
        result |= {"regime_adjustment": adjustment, "reason": "VIX panic/washout context; no automatic strong buy, confirmation required.", "min_rr_required": 2.5, "min_confidence_required": "High", "requires_confirmation": True}
    else:
        result |= {"regime_adjustment": "black_ice", "reason": "VIX crisis/forced-selling context; danger and opportunity watch only, confirmation required.", "min_rr_required": 3.0, "min_confidence_required": "High", "requires_confirmation": True}

    if term_structure in {None, ""}:
        result["term_structure"] = "missing"
    result["standalone_signal"] = False
    result["final_signal"] = "none"
    return result
