"""Lightweight normalized provider contracts for Phase 4B."""

from __future__ import annotations

from typing import Any, NotRequired, TypedDict


class ProviderEnvelope(TypedDict):
    provider: str
    as_of: str
    data: dict[str, Any]
    raw: dict[str, Any]
    symbol: NotRequired[str]
    series_id: NotRequired[str]
    cik: NotRequired[str]


class CompanyProfile(TypedDict, total=False):
    symbol: str
    company_name: str
    sector: str
    industry: str
    market_cap: int | float | None


class FinancialStatement(TypedDict, total=False):
    symbol: str
    date: str | None
    period: str | None
    revenue: int | float | None
    net_income: int | float | None


class KeyMetrics(TypedDict, total=False):
    symbol: str
    market_cap: int | float | None
    pe_ratio: int | float | None
    revenue_per_share: int | float | None


class FinancialRatios(TypedDict, total=False):
    symbol: str
    pe_ratio: int | float | None
    gross_profit_margin: int | float | None
    return_on_equity: int | float | None


class EarningsCalendar(TypedDict, total=False):
    symbol: str
    date: str | None
    eps_estimated: int | float | None
    eps_actual: int | float | None


class DailyBar(TypedDict):
    date: str
    open: int | float
    high: int | float
    low: int | float
    close: int | float
    volume: int | float


class DailyBars(TypedDict):
    symbol: str
    bars: list[DailyBar]


class CompanySubmissions(TypedDict, total=False):
    cik: str
    symbol: str
    name: str
    recent_filings: dict[str, Any]


class Form4FilingSummary(TypedDict, total=False):
    cik: str
    accession_number: str | None
    filing_date: str | None
    form_type: str | None
    reporting_owner: str | None


class MacroSeries(TypedDict):
    series_id: str
    observations: list[dict[str, Any]]


class QuoteSnapshot(TypedDict, total=False):
    symbol: str
    last_price: int | float | None
    timestamp: str | int | None
