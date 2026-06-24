from stockgod.analysis.postmortem import build_postmortem
from stockgod.state.decision_journal import add_journal_entry, load_journal, update_journal_outcome


def entry(**overrides):
    data = {"ticker": "NVDA", "date": "2026-06-01T00:00:00+00:00", "signal": "Buy Setup", "data_quality": "fresh"}
    data.update(overrides)
    return data


def test_no_journal_entry_returns_useful_message():
    result = build_postmortem({"ticker": "NVDA"})
    assert "No journaled signal found" in result["message"]


def test_invalidation_triggered_is_detected():
    result = build_postmortem({"ticker": "NVDA", "journal_entry": entry(), "days_elapsed": 30, "invalidation_triggered": True})
    assert result["invalidation_triggered"] == "yes"
    assert result["error_type"] == "risk_error"


def test_stale_missing_data_can_produce_data_error():
    result = build_postmortem({"ticker": "NVDA", "journal_entry": entry(data_quality="stale"), "days_elapsed": 30})
    assert result["error_type"] == "data_error"


def test_wrong_classification_can_produce_classification_error():
    result = build_postmortem({"ticker": "NVDA", "journal_entry": entry(), "days_elapsed": 30, "wrong_classification": True})
    assert result["error_type"] == "classification_error"


def test_too_little_time_elapsed_returns_no_error_yet():
    result = build_postmortem({"ticker": "NVDA", "journal_entry": entry(), "days_elapsed": 2})
    assert result["error_type"] == "no_error_yet"


def test_outcome_update_writes_back_to_journal(tmp_path):
    path = tmp_path / "journal.json"
    saved = add_journal_entry(entry(), path)
    updated = update_journal_outcome(saved["id"], {"error_type": "risk_error"}, path)
    loaded = load_journal(path)
    assert updated is not None
    assert loaded[0]["status"] == "reviewed"
    assert loaded[0]["outcome"] == {"error_type": "risk_error"}
