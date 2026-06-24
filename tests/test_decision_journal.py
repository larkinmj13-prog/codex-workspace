import json
from uuid import UUID

from stockgod.state.decision_journal import (
    add_journal_entry,
    find_entries_by_ticker,
    find_open_entries,
    load_journal,
    maybe_auto_journal_signal,
    render_journal_markdown,
    save_journal,
    update_journal_outcome,
)


def test_add_entry_generates_uuid_and_fills_defaults(tmp_path):
    path = tmp_path / "decision_journal.json"
    entry = add_journal_entry({"ticker": "NVDA"}, path)

    UUID(entry["id"])
    assert entry["ticker"] == "NVDA"
    assert entry["best_action"] == "do_nothing"
    assert entry["levels"] == {}
    assert entry["outcome"] is None


def test_save_and_load_json(tmp_path):
    path = tmp_path / "decision_journal.json"
    save_journal([{"ticker": "MSFT", "best_action": "hold"}], path)

    raw = json.loads(path.read_text(encoding="utf-8"))
    loaded = load_journal(path)

    assert raw[0]["ticker"] == "MSFT"
    assert loaded[0]["best_action"] == "hold"


def test_render_journal_markdown():
    markdown = render_journal_markdown([
        {
            "id": "abc",
            "ticker": "NVDA",
            "date": "2026-06-23T00:00:00+00:00",
            "best_action": "wait",
            "signal_quality": "B+",
            "confidence": "Medium",
            "risk_gate": "none",
            "why_now": "Breakout confirmed.",
            "why_not": "No major caveat identified.",
        }
    ])

    assert "# Decision Journal" in markdown
    assert "## NVDA" in markdown
    assert "Best action: wait" in markdown


def test_load_missing_file_returns_empty_list(tmp_path):
    assert load_journal(tmp_path / "missing.json") == []


def test_de_duplicates_same_ticker_signal_date(tmp_path):
    path = tmp_path / "journal.json"
    signal = {"ticker": "NVDA", "date": "2026-06-23T00:00:00+00:00", "signal": "Buy Setup", "why_now": "Changed", "confidence": "High"}
    first = maybe_auto_journal_signal(signal, path)
    second = maybe_auto_journal_signal(signal | {"price": 10}, path)
    entries = load_journal(path)
    assert first is not None and second is not None
    assert len(entries) == 1
    assert entries[0]["price"] == 10


def test_update_journal_outcome_works(tmp_path):
    path = tmp_path / "journal.json"
    saved = add_journal_entry({"ticker": "NVDA"}, path)
    updated = update_journal_outcome(saved["id"], "worked", path)
    assert updated["outcome"] == "worked"
    assert updated["status"] == "reviewed"


def test_find_entries_by_ticker_works():
    entries = [{"ticker": "NVDA"}, {"ticker": "MSFT"}]
    assert len(find_entries_by_ticker(entries, "nvda")) == 1


def test_find_open_entries_works():
    entries = [{"ticker": "NVDA", "status": "open"}, {"ticker": "MSFT", "status": "closed"}]
    assert len(find_open_entries(entries)) == 1


def test_maybe_auto_journal_ignores_unchanged_neutral_cards(tmp_path):
    path = tmp_path / "journal.json"
    result = maybe_auto_journal_signal({"ticker": "NVDA", "signal": "Neutral", "confidence": "Low", "best_action": "do_nothing"}, path)
    assert result is None
    assert load_journal(path) == []


def test_maybe_auto_journal_records_buy_setup_daily_pop_and_risk_gate(tmp_path):
    path = tmp_path / "journal.json"
    assert maybe_auto_journal_signal({"ticker": "A", "signal": "Buy Setup"}, path) is not None
    assert maybe_auto_journal_signal({"ticker": "B", "daily_pop_inclusion": True}, path) is not None
    assert maybe_auto_journal_signal({"ticker": "C", "risk_gate_changed": True}, path) is not None
    assert len(load_journal(path)) == 3
