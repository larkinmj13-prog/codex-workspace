"""Categorized Daily Pop report using supplied Phase 2 signals."""

from __future__ import annotations

from datetime import date
from typing import Any

from stockgod.analysis.signal_review_board import review_signal
from stockgod.analysis.why_now import generate_why_now_why_not

CATEGORIES = [
    ("best_new_buy_setups", "1. BEST NEW BUY SETUPS"),
    ("pullback", "2. BEST PULLBACK OPPORTUNITIES"),
    ("breakout", "3. BREAKOUT CANDIDATES"),
    ("watchlist_near_buy_zone", "4. HIGH-QUALITY WATCHLIST NEAR BUY ZONE"),
    ("insider", "5. INSIDER CONVICTION POPS"),
    ("danger", "6. DANGER / RISK-GATE CHANGES"),
    ("market_regime", "7. MARKET REGIME SHIFT"),
    ("lesson", "8. LESSON OF THE DAY"),
]

MATERIAL_TRIGGER_FIELDS = {
    "signal_label_changed",
    "buy_zone_reached",
    "breakout_confirmed",
    "stop_or_danger_triggered",
    "qualifying_insider_event",
    "risk_gate_changed",
    "earnings_risk_inside_5_days",
    "market_regime_changed",
    "confidence_improved_materially",
    "data_disagreement_resolved",
}


def build_daily_pop_report(signals: list[dict[str, Any]], preferences: dict[str, Any] | None = None) -> str:
    """Build a concise categorized Daily Pop report from supplied signals."""
    preferences = preferences or {}
    max_names = int(preferences.get("max_names", 10))
    report_date = preferences.get("date") or date.today().isoformat()
    buckets: dict[str, list[dict[str, Any]]] = {key: [] for key, _ in CATEGORIES}

    for signal in signals:
        if _is_lesson(signal):
            buckets["lesson"].append(signal)
            continue
        if _is_market_regime(signal):
            buckets["market_regime"].append(signal)
            continue
        if not _has_material_change(signal):
            continue
        _ensure_why_now(signal)
        if _is_danger(signal):
            buckets["danger"].append(signal)
            continue
        if _is_suppressed_by_regime(signal, preferences):
            continue
        if str(signal.get("confidence", "")) == "Low" and not signal.get("elite_setup", False):
            continue
        if review_signal(signal).get("result") not in {"pass", "conditional"}:
            continue
        category = _category_for(signal)
        buckets[category].append(signal)

    lines = [f"DAILY POP SCREEN — {report_date}", ""]
    total = sum(len(items) for items in buckets.values())
    if total == 0:
        lines.extend([
            "No qualifying pops today.",
            "",
            "Reason:",
            "No ticker met the material-change, confidence, risk-gate, and reward/risk thresholds.",
        ])
        return "\n".join(lines) + "\n"

    remaining = max_names
    for key, heading in CATEGORIES:
        lines.append(heading)
        items = buckets[key][: max(0, remaining)] if key not in {"lesson", "market_regime"} else buckets[key][:1]
        if not items:
            lines.extend(["None.", ""])
            continue
        for item in items:
            lines.extend(_render_item(key, item))
            if key not in {"lesson", "market_regime"}:
                remaining -= 1
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _has_material_change(signal: dict[str, Any]) -> bool:
    if signal.get("material_change", False):
        return True
    if abs(float(signal.get("composite_delta", 0) or 0)) >= 5:
        return True
    if signal.get("entry_score_delta") is not None and abs(float(signal.get("entry_score_delta") or 0)) >= 7:
        return True
    return any(bool(signal.get(field, False)) for field in MATERIAL_TRIGGER_FIELDS)


def _ensure_why_now(signal: dict[str, Any]) -> None:
    generated = generate_why_now_why_not(signal)
    signal.setdefault("why_now", generated["why_now"])
    signal.setdefault("why_not", generated["why_not"])


def _is_danger(signal: dict[str, Any]) -> bool:
    return bool(signal.get("stop_or_danger_triggered") or signal.get("risk_gate_changed") or signal.get("risk_gate") not in {None, "", "none"})


def _is_suppressed_by_regime(signal: dict[str, Any], preferences: dict[str, Any]) -> bool:
    regime_override = dict(preferences.get("regime_override", {}) or {})
    return bool(
        regime_override.get("regime_adjustment") == "suppress_marginal_buys"
        and signal.get("marginal_buy_setup", False)
        and not signal.get("elite_setup", False)
    )


def _is_lesson(signal: dict[str, Any]) -> bool:
    return bool(signal.get("lesson_of_the_day"))


def _is_market_regime(signal: dict[str, Any]) -> bool:
    return bool(signal.get("market_regime_changed") and signal.get("market_regime_summary"))


def _category_for(signal: dict[str, Any]) -> str:
    if signal.get("category_hint") in {key for key, _ in CATEGORIES}:
        return str(signal["category_hint"])
    if signal.get("pullback_into_buy_zone"):
        return "pullback"
    if signal.get("breakout_confirmed"):
        return "breakout"
    if signal.get("near_buy_zone"):
        return "watchlist_near_buy_zone"
    if signal.get("qualifying_insider_event"):
        return "insider"
    return "best_new_buy_setups"


def _render_item(category: str, signal: dict[str, Any]) -> list[str]:
    ticker = signal.get("ticker", "UNKNOWN")
    tier = signal.get("tier") or signal.get("signal_quality", "?")
    label = signal.get("signal", signal.get("signal_label", "Signal"))
    score = signal.get("score", signal.get("composite", 0))
    conf = _conf_short(str(signal.get("confidence", "")))
    why_now = signal.get("why_now", "No urgent trigger; watch only.")
    why_not = signal.get("why_not", "No major caveat identified.")

    if category == "pullback":
        return [f"{ticker} — Tier {tier} · {label} · {score}/100 · conf {conf}", f"Buy Zone: {signal.get('buy_zone', 'not supplied')}", f"Why Now: {why_now}", f"Why Not: {why_not}"]
    if category == "breakout":
        return [f"{ticker} — close above {signal.get('breakout_level', 'not supplied')}", f"Confirmation: {signal.get('confirmation', 'confirmation required')}", f"Why Now: {why_now}", f"Why Not: {why_not}"]
    if category == "watchlist_near_buy_zone":
        return [f"{ticker} — Own it? {signal.get('own_it', 'Yes')} · Enter now? {signal.get('enter_now', 'Wait')}", f"Why Now: {why_now}", f"Why Not: {why_not}"]
    if category == "insider":
        return [f"{ticker} — {signal.get('insider_signal', 'qualifying insider event')}", f"Why Now: {why_now}", f"Why Not: {why_not}"]
    if category == "danger":
        return [f"{ticker} — {signal.get('risk_gate', 'risk gate change')}", f"Why Not: {why_not}"]
    if category == "market_regime":
        return [str(signal.get("market_regime_summary", signal.get("market_regime", "Unknown"))), f"Level that flips it: {signal.get('flip_level', 'not supplied')}"]
    if category == "lesson":
        return [str(signal.get("lesson_of_the_day"))]
    return [f"{ticker} — Tier {tier} · {label} · {score}/100 · conf {conf}", f"Why Now: {why_now}", f"Why Not: {why_not}", f"Action: {signal.get('action', 'watch only until confirmed')}"]


def _conf_short(confidence: str) -> str:
    return {"High": "H", "Medium": "M", "Low": "L", "No Action": "NA"}.get(confidence, confidence or "?")
