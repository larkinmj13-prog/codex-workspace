"""Deterministic portfolio impact analysis for supplied holdings."""

from __future__ import annotations

from typing import Any

ATTRACTIVE_SIGNALS = {"Buy Setup", "Elite Buy Setup", "Add", "Breakout Candidate"}


def analyze_portfolio_impact(signal: dict[str, Any]) -> dict[str, Any]:
    """Determine whether a ticker helps the portfolio, not only standalone appeal."""
    standalone = str(signal.get("standalone_signal") or signal.get("signal") or "")
    risk_gate = str(signal.get("risk_gate", "none") or "none")
    holdings = list(signal.get("holdings") or [])

    if risk_gate not in {"", "none"}:
        return _result(standalone, "avoid", f"Active risk gate: {risk_gate}.", "avoid", "avoid_new_money", [], "unknown")

    if not holdings:
        return _result(standalone, "limited", "No portfolio holdings provided. Analysis is based on standalone ticker context only.", "watchlist", "unknown", [], "unknown")

    flags = _concentration_flags(signal, holdings)
    attractive = standalone in ATTRACTIVE_SIGNALS
    if attractive and flags:
        return _result(standalone, "size_smaller", "Attractive standalone read, but portfolio concentration is elevated.", "satellite", "smaller", flags, "low")
    if attractive:
        return _result(standalone, "add", "Attractive standalone read with no supplied concentration conflict.", "satellite", "normal", [], "medium")
    if flags:
        return _result(standalone, "watch", "Portfolio overlap exists and standalone read is not compelling.", "watchlist", "smaller", flags, "low")
    return _result(standalone, "watch", "No portfolio conflict supplied, but standalone read is not an add signal.", "watchlist", "unknown", [], "medium")


def render_portfolio_impact(result: dict[str, Any], ticker: str) -> str:
    """Render concise portfolio impact output."""
    if result["portfolio_read"] == "limited":
        return f"Portfolio Impact: Limited\nReason: {result['reason']}\n"
    flags = ", ".join(result["concentration_flags"]) or "none"
    return (
        f"Portfolio Impact — {ticker}\n"
        f"Standalone: {result['standalone_read']}\n"
        f"Portfolio Read: {result['portfolio_read']}\n"
        f"Sizing: {result['sizing_implication']}\n"
        f"Role: {result['suggested_role']}\n"
        f"Flags: {flags}\n"
        f"Reason: {result['reason']}\n"
    )


def _concentration_flags(signal: dict[str, Any], holdings: list[dict[str, Any]]) -> list[str]:
    flags: list[str] = []
    sector = signal.get("sector")
    industry = signal.get("industry")
    factors = set(signal.get("factor_exposures") or [])

    sector_weight = sum(float(h.get("weight", 0) or 0) for h in holdings if h.get("sector") == sector)
    industry_matches = [h.get("ticker", "UNKNOWN") for h in holdings if industry and h.get("industry") == industry]
    factor_matches = sorted({factor for h in holdings for factor in (h.get("factor_exposures") or []) if factor in factors})

    if sector and sector_weight >= 0.15:
        flags.append(f"sector concentration: {sector}")
    if industry_matches:
        flags.append(f"industry overlap: {industry}")
    if factor_matches:
        flags.append("factor overlap: " + ", ".join(factor_matches))
    return flags


def _result(standalone: str, portfolio: str, reason: str, role: str, sizing: str, flags: list[str], diversification: str) -> dict[str, Any]:
    return {
        "standalone_read": standalone,
        "portfolio_read": portfolio,
        "reason": reason,
        "suggested_role": role,
        "sizing_implication": sizing,
        "concentration_flags": flags,
        "diversification_benefit": diversification,
    }
