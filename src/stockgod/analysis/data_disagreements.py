"""Detect deterministic data disagreements between supplied provider dictionaries."""

from __future__ import annotations

from typing import Any

PRIMARY_BY_CATEGORY = {
    "price": "massive",
    "ohlcv": "massive",
    "fundamentals": "fmp",
    "earnings": "fmp",
    "insider_discovery": "fmp",
    "insider_verification": "edgar",
    "macro": "fred",
    "options": "massive",
    "news": "fmp",
}


def detect_data_disagreements(primary: dict[str, Any], backup: dict[str, Any], category: str) -> list[dict[str, Any]]:
    """Return material provider conflicts without fetching provider data."""
    category = category.lower()
    alerts: list[dict[str, Any]] = []
    primary_provider = str(primary.get("provider") or PRIMARY_BY_CATEGORY.get(category, "primary")).lower()
    backup_provider = str(backup.get("provider") or "backup").lower()

    if category == "insider_verification":
        primary_code = primary.get("transaction_code")
        backup_code = backup.get("transaction_code")
        if primary_code and backup_code and primary_code != backup_code:
            resolved = "edgar" if "edgar" in {primary_provider, backup_provider} else primary_provider
            alerts.append(_alert("high", category, "Insider Conflict: FMP flags insider purchase, but EDGAR Form 4 shows different transaction code. Insider signal ignored.", primary_provider, backup_provider, resolved))
        return alerts

    if category in {"price", "ohlcv"}:
        p_price = _num(primary.get("price") or primary.get("close"))
        b_price = _num(backup.get("price") or backup.get("close"))
        if p_price and b_price and abs(p_price - b_price) / p_price > 0.01:
            alerts.append(_alert("medium", category, "Price providers differ by more than 1%. Using primary source; confidence reduced.", primary_provider, backup_provider, primary_provider))
        if primary.get("timestamp") and backup.get("timestamp") and primary.get("timestamp") != backup.get("timestamp"):
            alerts.append(_alert("low", category, "Price timestamp mismatch across providers. Using primary source; confidence reduced.", primary_provider, backup_provider, primary_provider))
        return alerts

    if category == "earnings":
        if primary.get("earnings_date") != backup.get("earnings_date"):
            severity = "high" if primary.get("within_5_days") or backup.get("within_5_days") else "medium"
            alerts.append(_alert(severity, category, "Earnings date mismatch across providers. Using primary source; confidence reduced.", primary_provider, backup_provider, primary_provider))
        return alerts

    if category == "fundamentals":
        if not primary and backup:
            alerts.append(_alert("medium", category, "Fundamentals missing from primary but present in backup. Confidence reduced.", primary_provider, backup_provider, backup_provider))
            return alerts
        p_pe = _num(primary.get("forward_pe"))
        b_pe = _num(backup.get("forward_pe"))
        if p_pe and b_pe and abs(p_pe - b_pe) / p_pe > 0.2:
            alerts.append(_alert("medium", category, "FMP and backup show materially different forward P/E. Using FMP as primary; confidence reduced.", primary_provider, backup_provider, primary_provider))
        return alerts

    for key, value in primary.items():
        if key in {"provider"} or key not in backup:
            continue
        if backup[key] != value:
            alerts.append(_alert("low", category, f"Provider disagreement on {key}. Using primary source; confidence reduced.", primary_provider, backup_provider, primary_provider))
            break
    return alerts


def _num(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _alert(severity: str, category: str, message: str, primary_provider: str, backup_provider: str, resolved: str) -> dict[str, Any]:
    return {"has_disagreement": True, "severity": severity, "category": category, "message": message, "primary_provider": primary_provider, "backup_provider": backup_provider, "resolved_value_source": resolved}
