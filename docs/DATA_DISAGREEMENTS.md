# Data Disagreement Alerts

## Purpose

Data Disagreement Alerts detect material conflicts between supplied provider dictionaries.

## Inputs

Use `detect_data_disagreements(primary, backup, category)` with provider dictionaries and a category such as `price`, `fundamentals`, `earnings`, or `insider_verification`.

## Output

Returns a list of alerts with severity, category, providers, resolved source, and a concise message.

## Rules

- Prefer the primary source unless EDGAR contradicts insider classification.
- EDGAR wins for insider verification.
- Price differences above 1% or timestamp mismatches create alerts.
- Earnings date mismatch inside five trading days is high severity.
- Forward P/E differences large enough to change valuation bucket reduce confidence.
- Reports are not blocked unless severe disagreement affects actionability.

## Limitations

No provider data is fetched. This module only compares supplied dictionaries.
