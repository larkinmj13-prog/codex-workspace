"""Basic decision journal persistence for Phase 1."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

DEFAULT_JSON_PATH = Path("data/state/decision_journal.json")
DEFAULT_MARKDOWN_PATH = Path("reports/journal/decision_journal.md")

DEFAULT_ENTRY: dict[str, Any] = {
    "id": "",
    "ticker": "",
    "date": "",
    "price": 0,
    "signal": "",
    "signal_quality": "",
    "own_it": "",
    "enter_now": "",
    "best_action": "do_nothing",
    "stock_type": "",
    "composite": 0,
    "confidence": "",
    "risk_gate": "",
    "market_regime": "",
    "levels": {},
    "why_now": "",
    "why_not": "",
    "bull_case": [],
    "bear_case": [],
    "divergences": [],
    "invalidation": "",
    "data_quality": "",
    "model_version": "",
    "outcome": None,
    "review_date": None,
    "status": "open",
    "source": "manual",
    "confidence_breakdown": {
        "price": "missing",
        "fundamentals": "missing",
        "earnings": "missing",
        "insider": "null",
        "options": "not_applicable",
        "market_regime": "missing",
        "news": "not_applicable",
    },
    "data_disagreements": [],
    "regime_override": {
        "override_active": False,
        "regime_adjustment": "none",
        "reason": "",
        "min_rr_required": None,
        "min_confidence_required": None,
        "standalone_signal": False,
    },
}

ALLOWED_BEST_ACTIONS = {
    "buy",
    "partial",
    "wait",
    "add",
    "hold",
    "trim",
    "avoid",
    "sell_risk",
    "do_nothing",
}


def load_journal(path: str | Path) -> list[dict[str, Any]]:
    """Load journal entries, returning an empty list when the file is absent."""
    journal_path = Path(path)
    if not journal_path.exists():
        return []
    data = json.loads(journal_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return [_normalize_entry(entry if isinstance(entry, dict) else {}) for entry in data]


def save_journal(entries: list[dict[str, Any]], path: str | Path) -> None:
    """Save journal entries as pretty JSON."""
    journal_path = Path(path)
    journal_path.parent.mkdir(parents=True, exist_ok=True)
    normalized = [_normalize_entry(entry if isinstance(entry, dict) else {}) for entry in entries]
    journal_path.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")


def add_journal_entry(entry: dict[str, Any], path: str | Path) -> dict[str, Any]:
    """Add a journal entry to a JSON journal and return the normalized entry."""
    entries = load_journal(path)
    normalized = _normalize_entry(entry)
    entries.append(normalized)
    save_journal(entries, path)
    return normalized


def update_journal_outcome(entry_id: str, outcome: dict[str, Any] | str, path: str | Path) -> dict[str, Any] | None:
    """Update a journal entry outcome and mark it reviewed."""
    entries = load_journal(path)
    for entry in entries:
        if entry["id"] == entry_id:
            entry["outcome"] = outcome
            entry["status"] = "reviewed"
            entry["review_date"] = datetime.now(UTC).isoformat()
            save_journal(entries, path)
            return entry
    return None


def find_entries_by_ticker(entries: list[dict[str, Any]], ticker: str) -> list[dict[str, Any]]:
    """Find normalized journal entries for a ticker."""
    wanted = ticker.upper()
    return [_normalize_entry(entry) for entry in entries if str(entry.get("ticker", "")).upper() == wanted]


def find_open_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return entries that remain open."""
    return [_normalize_entry(entry) for entry in entries if _normalize_entry(entry)["status"] == "open"]


def maybe_auto_journal_signal(signal: dict[str, Any], path: str | Path) -> dict[str, Any] | None:
    """Auto-journal only meaningful signal changes and de-duplicate noisy repeats."""
    if not _is_meaningful_for_auto_journal(signal):
        return None
    entries = load_journal(path)
    normalized = _normalize_entry(signal)
    duplicate = _find_duplicate(entries, normalized)
    if duplicate is not None:
        entries[duplicate].update(normalized)
        save_journal(entries, path)
        return _normalize_entry(entries[duplicate])
    entries.append(normalized)
    save_journal(entries, path)
    return normalized


def _is_meaningful_for_auto_journal(signal: dict[str, Any]) -> bool:
    if signal.get("explicit_user_request"):
        return True
    if str(signal.get("confidence")) == "Low" and str(signal.get("best_action")) == "do_nothing":
        return False
    if signal.get("stale_data_report"):
        return False
    if signal.get("daily_pop_inclusion") or signal.get("risk_gate_changed") or signal.get("stop_or_invalidation_triggered"):
        return True
    if signal.get("signal_label_changed"):
        return True
    return str(signal.get("signal")) in {"Buy Setup", "Elite Buy Setup"}


def _find_duplicate(entries: list[dict[str, Any]], candidate: dict[str, Any]) -> int | None:
    candidate_day = str(candidate.get("date", ""))[:10]
    for index, entry in enumerate(entries):
        if (
            str(entry.get("ticker", "")).upper() == str(candidate.get("ticker", "")).upper()
            and str(entry.get("signal", "")) == str(candidate.get("signal", ""))
            and str(entry.get("date", ""))[:10] == candidate_day
            and str(entry.get("why_now", "")) == str(candidate.get("why_now", ""))
        ):
            return index
    return None


def render_journal_markdown(entries: list[dict[str, Any]]) -> str:
    """Render journal entries to concise Markdown."""
    lines = ["# Decision Journal", ""]
    if not entries:
        lines.append("No entries recorded.")
        return "\n".join(lines) + "\n"

    for raw_entry in entries:
        entry = _normalize_entry(raw_entry if isinstance(raw_entry, dict) else {})
        title = entry["ticker"] or "UNKNOWN"
        lines.extend(
            [
                f"## {title} — {entry['date']}",
                "",
                f"- ID: `{entry['id']}`",
                f"- Best action: {entry['best_action']}",
                f"- Signal quality: {entry['signal_quality']}",
                f"- Confidence: {entry['confidence']}",
                f"- Risk gate: {entry['risk_gate']}",
                f"- Why now: {entry['why_now']}",
                f"- Why not: {entry['why_not']}",
                "",
            ]
        )
    return "\n".join(lines)


def _normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(DEFAULT_ENTRY)
    normalized.update(entry)

    if not normalized["id"]:
        normalized["id"] = str(uuid4())
    if not normalized["date"]:
        normalized["date"] = datetime.now(UTC).isoformat()
    if normalized["best_action"] not in ALLOWED_BEST_ACTIONS:
        normalized["best_action"] = "do_nothing"
    if normalized["status"] not in {"open", "closed", "reviewed"}:
        normalized["status"] = "open"
    if normalized["source"] not in {"manual", "daily_pop", "signal_card", "postmortem"}:
        normalized["source"] = "manual"

    for key in ("bull_case", "bear_case", "divergences"):
        if not isinstance(normalized[key], list):
            normalized[key] = []
    if not isinstance(normalized["levels"], dict):
        normalized["levels"] = {}
    if not isinstance(normalized["confidence_breakdown"], dict):
        normalized["confidence_breakdown"] = deepcopy(DEFAULT_ENTRY["confidence_breakdown"])
    if not isinstance(normalized["data_disagreements"], list):
        normalized["data_disagreements"] = []
    if not isinstance(normalized["regime_override"], dict):
        normalized["regime_override"] = deepcopy(DEFAULT_ENTRY["regime_override"])

    return normalized
