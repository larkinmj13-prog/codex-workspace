from stockgod import __version__
from stockgod.cli import main


def test_package_imports():
    assert __version__ == "0.1.0"


def test_placeholder_cli_runs(capsys):
    assert main([]) == 0
    captured = capsys.readouterr()
    assert "scaffold is installed" in captured.out
    assert "Phase 1 deterministic commands" in captured.out


def test_phase_1_review_signal_cli_runs(capsys):
    assert main(["review-signal"]) == 0
    captured = capsys.readouterr()
    assert "Phase 1 deterministic scaffold" in captured.out
    assert "Result:" in captured.out
