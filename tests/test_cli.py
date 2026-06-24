from stockgod.cli import main


def test_why_now_cli_runs(capsys):
    assert main(["why-now"]) == 0
    captured = capsys.readouterr()
    assert "Phase 1 deterministic scaffold: why-now" in captured.out
    assert "Why Now: Breakout confirmed." in captured.out
    assert "Why Not: Missing technical levels." in captured.out


def test_journal_add_and_journal_cli_share_custom_path(tmp_path, capsys):
    path = tmp_path / "decision_journal.json"

    assert main(["journal-add", "NVDA", "--path", str(path)]) == 0
    add_output = capsys.readouterr().out
    assert "Added journal entry" in add_output
    assert "NVDA" in add_output

    assert main(["journal", "--path", str(path)]) == 0
    journal_output = capsys.readouterr().out
    assert "# Decision Journal" in journal_output
    assert "## NVDA" in journal_output
    assert "Best action: do_nothing" in journal_output


def test_empty_journal_cli_uses_custom_path(tmp_path, capsys):
    path = tmp_path / "missing.json"

    assert main(["journal", "--path", str(path)]) == 0
    captured = capsys.readouterr()
    assert "No entries recorded." in captured.out


def test_phase_2_pop_cli_runs(capsys):
    assert main(["pop"]) == 0
    captured = capsys.readouterr()
    assert "DAILY POP SCREEN" in captured.out
    assert "BEST NEW BUY SETUPS" in captured.out


def test_phase_2_data_confidence_and_regime_cli_run(capsys):
    assert main(["data-check"]) == 0
    assert "Phase 2 deterministic scaffold: data-check" in capsys.readouterr().out

    assert main(["confidence"]) == 0
    assert "Phase 2 deterministic scaffold: confidence" in capsys.readouterr().out

    assert main(["regime-override"]) == 0
    output = capsys.readouterr().out
    assert "Phase 2 deterministic scaffold: regime-override" in output
    assert "Standalone signal: False" in output
