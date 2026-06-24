# Read-Only Stock Card — Phase 5

## Purpose

Phase 5 introduces the first read-only stock card. It can render supplied normalized provider envelopes or, when explicitly requested, fetch read-only live provider data using configured keys.

## CLI

```bash
python -m stockgod stock-card MSFT --input tests/fixtures/stock_card_msft.json
python -m stockgod stock-card MSFT --live
python -m stockgod stock-card MSFT --live --no-macro
```

## Inputs

The supplied JSON path should contain normalized provider envelopes for company profile, daily bars, earnings, and optional macro context.

## Output Limits

The card is informational only. It does not produce scores, ratings, buy/sell signals, technical levels, recommendations, position sizing, or financial advice.

## Live Mode

Live mode is read-only and requires configured provider keys. Missing keys fail cleanly through provider errors. Default tests do not call live APIs.
