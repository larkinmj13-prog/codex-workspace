# Data Providers — Phase 4A

## Purpose

Phase 4A adds read-only provider foundations. Provider clients fetch and normalize data for later phases without changing scoring, signals, technical levels, or recommendations.

## Provider Roles

- FMP: fundamentals, valuation, earnings, company profile, news, insider discovery.
- Massive: price/OHLCV, market data, future technical input data, options later.
- SEC EDGAR: filings, company submissions, Form 4 verification.
- FRED: macro/rates/economic series.
- Yahoo Finance: fallback/sanity check only.

## Required Environment Variables

- `FMP_API_KEY`
- `MASSIVE_API_KEY`
- `FRED_API_KEY`
- `SEC_USER_AGENT`
- `YAHOO_FALLBACK_ENABLED`

Provider keys are not required to import the package, create provider objects, run routers, or run tests. Missing keys raise clean provider errors only when a real request is attempted.

## Provider Priority

1. Massive for price/OHLCV.
2. FMP for fundamentals, earnings, profile, news, insider discovery.
3. SEC EDGAR for filings and insider verification.
4. FRED for macro/rates.
5. Yahoo fallback/sanity check only.

## Read-Only Limitation

Phase 4A is read-only. It does not add trading, order execution, recommendations, scoring changes, technical levels, options analytics, background jobs, or write actions to external services.

## No-Live-Tests Rule

Unit tests must not call live provider APIs. Use mocked sessions, monkeypatching, and fixtures.

## Example Provider Checks

```bash
python -m stockgod provider-check fmp --ticker MSFT
python -m stockgod provider-check massive --ticker SPY
python -m stockgod provider-check edgar --ticker MSFT
python -m stockgod provider-check fred --series DGS10
python -m stockgod provider-check yahoo --ticker MSFT
```

Without keys or optional dependencies, these commands should print concise provider errors and no raw traceback.

## Normalized Provider Envelope

Phase 4B hardens provider output contracts. Symbol-based providers return a small envelope:

```json
{
  "provider": "fmp|massive|sec_edgar|yahoo",
  "symbol": "MSFT",
  "as_of": "ISO8601 or source timestamp",
  "data": {},
  "raw": {}
}
```

FRED macro series use `series_id` instead of `symbol`:

```json
{
  "provider": "fred",
  "series_id": "DGS10",
  "as_of": "ISO8601 or source timestamp",
  "data": {},
  "raw": {}
}
```

## Provider Fixtures

Small sanitized fixtures live under `tests/fixtures/providers/`. They are deterministic contract examples only and contain no API keys, secrets, or giant raw payloads.

## Contract Tests

Provider contract tests verify that normalizers return stable envelopes, tolerate optional missing fields, and raise clean `ProviderResponseError` exceptions when required fields are missing.

## EDGAR Form 4 Verification Helpers

Phase 4B adds transaction-code helpers for future insider verification. Code `P` is labeled `potential_purchase`, but it is not a standalone conviction signal. Codes `A`, `M`, and `F` are not open-market purchase signals. Unknown or missing codes remain `unknown_or_unverified`.

## What This Phase Does Not Do

Phase 4B does not connect provider data into signal generation, score stocks, infer insider intent, fetch live data in tests, build technical levels, run Daily Pop scans, or create buy/sell recommendations.

## Phase 4C Live Smoke Tests

Phase 4C introduces an opt-in live smoke test harness for real read-only provider credentials. These tests are skipped by default and only run when `RUN_LIVE_PROVIDER_SMOKE=1` is set with the matching provider credentials.

Example:

```bash
RUN_LIVE_PROVIDER_SMOKE=1 python -m pytest tests/test_live_provider_smoke.py
```

Live smoke tests must remain read-only, must not print secrets, and must not create scores, signals, technical levels, recommendations, trades, or reports.
