"""CLI for Stock God Evidence Engine v6 deterministic scaffolds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from stockgod import __version__
from stockgod.analysis.confidence_breakdown import build_confidence_breakdown
from stockgod.analysis.data_disagreements import detect_data_disagreements
from stockgod.analysis.portfolio_impact import analyze_portfolio_impact, render_portfolio_impact
from stockgod.analysis.postmortem import build_postmortem, render_postmortem
from stockgod.analysis.regime_override import build_regime_override
from stockgod.analysis.signal_quality import assign_signal_quality
from stockgod.analysis.signal_review_board import review_signal
from stockgod.analysis.why_now import generate_why_now_why_not
from stockgod.data.edgar import EdgarClient
from stockgod.data.errors import ProviderError
from stockgod.data.fmp import FMPClient
from stockgod.data.fred import FREDClient
from stockgod.data.massive import MassiveClient
from stockgod.data.yahoo import YahooFallbackClient
from stockgod.reports.daily_pop import build_daily_pop_report
from stockgod.reports.stock_card import build_read_only_stock_card, fetch_live_stock_card_inputs
from stockgod.state.decision_journal import DEFAULT_JSON_PATH, add_journal_entry, find_entries_by_ticker, load_journal, render_journal_markdown


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="stockgod",
        description="Stock God Evidence Engine v6 deterministic scaffold CLI.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"stockgod {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("review-signal", help="Run a Phase 1 sample Signal Review Board check.")
    subparsers.add_parser("why-now", help="Run a Phase 1 sample Why Now / Why Not check.")
    pop = subparsers.add_parser("pop", help="Run a Phase 2 sample Daily Pop screen.")
    pop.add_argument("--input", help="Optional JSON input path.")
    data_check = subparsers.add_parser("data-check", help="Run a Phase 2 sample data disagreement check.")
    data_check.add_argument("--input", help="Optional JSON input path.")
    confidence = subparsers.add_parser("confidence", help="Run a Phase 2 sample confidence breakdown.")
    confidence.add_argument("--input", help="Optional JSON input path.")
    regime = subparsers.add_parser("regime-override", help="Run a Phase 2 sample VIX/regime override check.")
    regime.add_argument("--input", help="Optional JSON input path.")
    portfolio = subparsers.add_parser("portfolio-impact", help="Run a Phase 3 portfolio impact check.")
    portfolio.add_argument("ticker")
    portfolio.add_argument("--input", help="Optional JSON input path.")
    postmortem = subparsers.add_parser("postmortem", help="Run a Phase 3 post-mortem check.")
    postmortem.add_argument("ticker")
    postmortem.add_argument("--input", help="Optional JSON input path.")
    journal_review = subparsers.add_parser("journal-review", help="Review journal entries for a ticker.")
    journal_review.add_argument("ticker")
    journal_review.add_argument("--path", default=str(DEFAULT_JSON_PATH), help="Journal JSON path.")
    stock_card = subparsers.add_parser("stock-card", help="Render a Phase 5 read-only stock card.")
    stock_card.add_argument("ticker")
    stock_card.add_argument("--input", help="Optional JSON input path with normalized provider envelopes.")
    stock_card.add_argument("--live", action="store_true", help="Fetch live read-only provider data using configured keys.")
    stock_card.add_argument("--no-macro", action="store_true", help="Skip optional FRED macro fetch in live mode.")
    provider_check = subparsers.add_parser("provider-check", help="Check a read-only provider configuration/request.")
    provider_check.add_argument("provider", choices=["fmp", "massive", "edgar", "fred", "yahoo"])
    provider_check.add_argument("--ticker", help="Ticker for equity providers.")
    provider_check.add_argument("--series", help="FRED series id.")
    journal = subparsers.add_parser("journal", help="Render the decision journal as Markdown.")
    journal.add_argument("--path", default=str(DEFAULT_JSON_PATH), help="Journal JSON path.")
    journal_add = subparsers.add_parser("journal-add", help="Add a sample Phase 1 journal entry for a ticker.")
    journal_add.add_argument("ticker")
    journal_add.add_argument("--path", default=str(DEFAULT_JSON_PATH), help="Journal JSON path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "review-signal":
        signal = _sample_signal()
        review = review_signal(signal)
        quality = assign_signal_quality(signal)
        print("Phase 1 deterministic scaffold: review-signal")
        print(f"Result: {review['result']} ({review['actionability']})")
        print(f"Reason: {review['reason']}")
        print(f"Signal quality: {quality['tier']}")
        return 0

    if args.command == "why-now":
        result = generate_why_now_why_not({"breakout_confirmed": True, "missing_technical_levels": True})
        print("Phase 1 deterministic scaffold: why-now")
        print(f"Why Now: {result['why_now']}")
        print(f"Why Not: {result['why_not']}")
        return 0

    if args.command == "pop":
        payload = _load_cli_json(args.input, parser) if args.input else {"signals": _sample_pop_signals(), "preferences": {"date": "2026-06-23", "max_names": 5}}
        if not isinstance(payload, dict):
            parser.error("pop --input must contain a JSON object with signals and optional preferences")
        print(build_daily_pop_report(list(payload.get("signals", [])), dict(payload.get("preferences", {}) or {})), end="")
        return 0

    if args.command == "data-check":
        payload = _load_cli_json(args.input, parser) if args.input else {"category": "fundamentals", "primary": {"provider": "fmp", "forward_pe": 20}, "backup": {"provider": "yahoo", "forward_pe": 28}}
        if not isinstance(payload, dict):
            parser.error("data-check --input must contain a JSON object")
        alerts = detect_data_disagreements(dict(payload.get("primary", {}) or {}), dict(payload.get("backup", {}) or {}), str(payload.get("category", "fundamentals")))
        print("Phase 2 deterministic scaffold: data-check")
        if not alerts:
            print("No material disagreement detected.")
        for alert in alerts:
            print(f"{alert['severity']}: {alert['message']}")
        return 0

    if args.command == "confidence":
        payload = _load_cli_json(args.input, parser) if args.input else {"price": "fresh", "fundamentals": "fresh", "earnings": "confirmed", "options": "missing"}
        if not isinstance(payload, dict):
            parser.error("confidence --input must contain a JSON object")
        result = build_confidence_breakdown(_confidence_payload_to_signal(payload))
        print("Phase 2 deterministic scaffold: confidence")
        print(result["short_reason"])
        return 0

    if args.command == "regime-override":
        payload = _load_cli_json(args.input, parser) if args.input else {"vix": 35, "vix_term_structure": "missing"}
        if not isinstance(payload, dict):
            parser.error("regime-override --input must contain a JSON object")
        result = build_regime_override(payload)
        print("Phase 2 deterministic scaffold: regime-override")
        print(f"Adjustment: {result['regime_adjustment']}")
        print(f"Standalone signal: {result['standalone_signal']}")
        return 0

    if args.command == "portfolio-impact":
        payload = _load_cli_json(args.input, parser) if args.input else {"ticker": args.ticker, "standalone_signal": "Watch", "holdings": []}
        if not isinstance(payload, dict):
            parser.error("portfolio-impact --input must contain a JSON object")
        payload.setdefault("ticker", args.ticker.upper())
        result = analyze_portfolio_impact(payload)
        print(render_portfolio_impact(result, str(payload.get("ticker", args.ticker)).upper()), end="")
        return 0

    if args.command == "postmortem":
        payload = _load_cli_json(args.input, parser) if args.input else {"ticker": args.ticker}
        if not isinstance(payload, dict):
            parser.error("postmortem --input must contain a JSON object")
        payload.setdefault("ticker", args.ticker.upper())
        print(render_postmortem(build_postmortem(payload)), end="")
        return 0

    if args.command == "journal-review":
        entries = find_entries_by_ticker(load_journal(Path(args.path)), args.ticker)
        if not entries:
            print(f"No journal entries found for {args.ticker.upper()}.")
            return 0
        print(render_journal_markdown(entries), end="")
        return 0

    if args.command == "stock-card":
        return _run_stock_card(args, parser)

    if args.command == "provider-check":
        return _run_provider_check(args)

    if args.command == "journal":
        entries = load_journal(Path(args.path))
        print(render_journal_markdown(entries), end="")
        return 0

    if args.command == "journal-add":
        entry = add_journal_entry({"ticker": args.ticker.upper(), "signal": "Phase 1 sample"}, Path(args.path))
        print("Phase 1 deterministic scaffold: journal-add")
        print(f"Added journal entry {entry['id']} for {entry['ticker']}.")
        return 0

    print("Stock God Evidence Engine v6 scaffold is installed. Use --help to view Phase 1 deterministic commands.")
    return 0


def _run_stock_card(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    try:
        if args.live:
            payload = fetch_live_stock_card_inputs(args.ticker, include_macro=not args.no_macro)
        elif args.input:
            payload = _load_cli_json(args.input, parser)
            if not isinstance(payload, dict):
                parser.error("stock-card --input must contain a JSON object")
        else:
            payload = {"ticker": args.ticker, "data_mode": "sample_read_only"}
        print(build_read_only_stock_card(args.ticker, payload), end="")
        return 0
    except ProviderError as exc:
        print(f"Stock card failed: {exc}")
        return 1


def _run_provider_check(args: argparse.Namespace) -> int:
    try:
        if args.provider == "fmp":
            result = FMPClient().get_company_profile(args.ticker or "MSFT")
        elif args.provider == "massive":
            result = MassiveClient().get_daily_bars(args.ticker or "SPY")
        elif args.provider == "edgar":
            result = EdgarClient().get_company_submissions(args.ticker or "MSFT")
        elif args.provider == "fred":
            result = FREDClient().get_series(args.series or "DGS10")
        else:
            result = YahooFallbackClient().get_quote_snapshot(args.ticker or "MSFT")
    except ProviderError as exc:
        print(f"Provider check failed: {exc}")
        return 1

    subject = result.get("symbol") or result.get("ticker") or result.get("series_id") or result.get("cik") or "unknown"
    fields = ", ".join(result.keys())
    print(f"Provider: {result.get('provider')}")
    print(f"Subject: {subject}")
    print(f"As Of: {result.get('as_of')}")
    print(f"Fields: {fields}")
    return 0


def load_json_input(path: str | Path) -> dict[str, Any] | list[Any]:
    """Load supplied JSON input for deterministic CLI commands."""
    input_path = Path(path)
    if not input_path.exists():
        raise ValueError(f"Input JSON not found: {input_path}")
    try:
        return json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {input_path}: {exc.msg}") from exc


def _load_cli_json(path: str | Path, parser: argparse.ArgumentParser) -> dict[str, Any] | list[Any]:
    try:
        return load_json_input(path)
    except ValueError as exc:
        parser.error(str(exc))


def _confidence_payload_to_signal(payload: dict[str, Any]) -> dict[str, Any]:
    data_fields = {
        key: payload[key]
        for key in ("price", "fundamentals", "earnings", "insider", "options", "market_regime", "news")
        if key in payload
    }
    signal = dict(payload)
    signal["data_quality"] = dict(payload.get("data_quality", {}) or {}) | data_fields
    signal["material_data_disagreement"] = bool(payload.get("material_data_disagreement") or payload.get("data_disagreements"))
    return signal


def _sample_signal() -> dict[str, object]:
    return {
        "risk_gate": "none",
        "confidence": "High",
        "missing_key_data": False,
        "earnings_within_5_days": False,
        "event_risk_caveat": False,
        "reward_risk": 2.0,
        "min_reward_risk": 1.5,
        "technical_levels_available": True,
        "data_conflict_unresolved": False,
        "classification_uncertain": False,
        "severe_contradiction": False,
        "market_regime": "Green",
        "why_now": "Sample deterministic trigger.",
        "thesis_strength": "strong",
        "entry_quality": "strong",
    }


def _sample_pop_signals() -> list[dict[str, object]]:
    return [
        _sample_signal() | {"ticker": "NVDA", "signal_label_changed": True, "signal": "Buy Setup", "score": 88, "tier": "A", "why_now": "Signal label changed.", "why_not": "No major caveat identified."},
        {"ticker": "RISK", "risk_gate": "capped44", "risk_gate_changed": True, "confidence": "Low", "technical_levels_available": True, "why_now": "Risk gate changed.", "why_not": "Active risk gate."},
    ]


if __name__ == "__main__":
    raise SystemExit(main())
