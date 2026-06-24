from stockgod.cli import main


def test_portfolio_impact_command_renders(capsys):
    assert main(["portfolio-impact", "NVDA", "--input", "tests/fixtures/portfolio_impact_input.json"]) == 0
    output = capsys.readouterr().out
    assert "Portfolio Impact" in output
    assert "Standalone:" in output


def test_postmortem_command_renders_no_entry_message(capsys):
    assert main(["postmortem", "NVDA"]) == 0
    assert "No journaled signal found for NVDA" in capsys.readouterr().out


def test_postmortem_command_renders_input(capsys):
    assert main(["postmortem", "NVDA", "--input", "tests/fixtures/postmortem_input.json"]) == 0
    output = capsys.readouterr().out
    assert "Post-Mortem" in output
    assert "Error Type:" in output


def test_journal_review_filters_ticker(capsys):
    assert main(["journal-review", "NVDA", "--path", "tests/fixtures/journal_entries.json"]) == 0
    output = capsys.readouterr().out
    assert "NVDA" in output
    assert "MSFT" not in output
