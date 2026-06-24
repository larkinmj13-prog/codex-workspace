"""Deterministic post-mortem review for supplied journal entries."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

NO_ENTRY_TEMPLATE = "No journaled signal found for {ticker}. Run `journal-add {ticker}` after a meaningful signal before using postmortem."


def build_postmortem(payload: dict[str, Any]) -> dict[str, Any]:
    """Classify what happened after a journaled signal using supplied data only."""
    ticker = str(payload.get("ticker") or "UNKNOWN").upper()
    entry = payload.get("journal_entry") or payload.get("original_journal_entry")
    if not isinstance(entry, dict) or not entry:
        return {
            "ticker": ticker,
            "message": NO_ENTRY_TEMPLATE.format(ticker=ticker),
            "error_type": "no_error_yet",
        }

    original_signal = str(entry.get("signal", ""))
    major_changes = list(payload.get("major_changes") or [])
    stale_data = bool(payload.get("stale_or_missing_data") or entry.get("data_quality") in {"stale", "missing"})
    wrong_classification = bool(payload.get("wrong_classification"))
    invalidation_triggered = bool(payload.get("invalidation_triggered"))
    regime_changed = bool(payload.get("market_regime_changed_sharply"))
    days_elapsed = int(payload.get("days_elapsed", _days_elapsed(entry.get("date"))) or 0)

    if days_elapsed < 5 and not invalidation_triggered and not stale_data and not wrong_classification:
        error_type = "no_error_yet"
        risk_controls = "too_early"
        what_happened = "Too little time has passed to judge the signal."
    elif stale_data:
        error_type = "data_error"
        risk_controls = "partial"
        what_happened = "Signal review was impaired by stale or missing data."
    elif wrong_classification:
        error_type = "classification_error"
        risk_controls = "partial"
        what_happened = "Stock type/classification was wrong for the setup."
    elif regime_changed:
        error_type = "regime_error"
        risk_controls = "partial"
        what_happened = "Market regime changed sharply after the signal."
    elif invalidation_triggered:
        error_type = "risk_error"
        risk_controls = "yes" if payload.get("risk_controls_worked", True) else "no"
        what_happened = "Invalidation triggered after the original signal."
    else:
        error_type = "no_error_yet"
        risk_controls = "too_early"
        what_happened = "No decisive post-mortem error identified yet."

    return {
        "ticker": ticker,
        "original_signal": original_signal,
        "what_happened": what_happened,
        "what_was_right": list(payload.get("what_was_right") or []),
        "what_was_wrong": major_changes,
        "error_type": error_type,
        "risk_controls_worked": risk_controls,
        "invalidation_triggered": "yes" if invalidation_triggered else "no",
        "model_lesson": _lesson(error_type),
        "recommended_adjustment": _adjustment(error_type),
    }


def render_postmortem(result: dict[str, Any]) -> str:
    """Render concise post-mortem output."""
    if "message" in result:
        return result["message"] + "\n"
    return (
        f"Post-Mortem — {result['ticker']}\n"
        f"Original Signal: {result['original_signal']}\n"
        f"Error Type: {result['error_type']}\n"
        f"Invalidation Triggered: {result['invalidation_triggered']}\n"
        f"Lesson: {result['model_lesson']}\n"
        f"Adjustment: {result['recommended_adjustment']}\n"
    )


def _days_elapsed(date_text: Any) -> int:
    if not date_text:
        return 0
    try:
        then = datetime.fromisoformat(str(date_text).replace("Z", "+00:00"))
    except ValueError:
        return 0
    now = datetime.now(UTC)
    if then.tzinfo is None:
        then = then.replace(tzinfo=UTC)
    return max(0, (now - then).days)


def _lesson(error_type: str) -> str:
    return {
        "data_error": "Do not elevate confidence when required data is stale or missing.",
        "classification_error": "Recheck stock type before applying scoring expectations.",
        "regime_error": "Regime shifts need explicit review before adding risk.",
        "risk_error": "Respect invalidation and journal whether risk controls worked.",
        "no_error_yet": "Do not judge the signal before enough evidence develops.",
    }.get(error_type, "Keep post-mortem lesson concise.")


def _adjustment(error_type: str) -> str:
    return {
        "data_error": "data_source",
        "classification_error": "classification",
        "regime_error": "alert_threshold",
        "risk_error": "level_logic",
        "no_error_yet": "none",
    }.get(error_type, "none")
