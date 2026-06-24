# Confidence Breakdown

## Purpose

Confidence Breakdown explains High, Medium, Low, or No Action confidence from supplied data-quality fields. It is a data-quality label, not a return forecast.

## Inputs

Use `build_confidence_breakdown(signal)` with fields such as `data_quality`, `single_stock_thesis`, `uses_options`, `insider_affects_score`, and `material_data_disagreement`.

## Output

Returns confidence, a phone-card `short_reason`, per-category data quality, and `why_not_high` caveats.

## Rules

- Missing price data returns `No Action`.
- Missing fundamentals for a single-stock thesis usually caps confidence at Low.
- Missing options data is `not_applicable` for non-options long-term cards.
- Unverified insider data only reduces confidence when it affects score/actionability.
- Material data disagreement and missing/stale earnings reduce confidence.

## Limitations

No external data is fetched. Inputs must already be prepared.
