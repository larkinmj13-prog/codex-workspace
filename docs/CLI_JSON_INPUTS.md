# CLI JSON Inputs

## Purpose

Phase 2 CLI commands can read deterministic JSON files instead of built-in sample data. This is supplied/mock input only; the CLI does not fetch external provider data or infer missing financial values.

## Supported Commands

```bash
python -m stockgod pop --input sample.json
python -m stockgod confidence --input sample.json
python -m stockgod data-check --input sample.json
python -m stockgod regime-override --input sample.json
```

If `--input` is omitted, each command continues to use deterministic sample data.

## Expected Shapes

### `pop`

```json
{
  "signals": [{"ticker": "MSFT", "material_change": true}],
  "preferences": {"max_names": 5}
}
```

### `confidence`

```json
{
  "price": "fresh",
  "fundamentals": "fresh",
  "earnings": "confirmed",
  "options": "not_applicable"
}
```

### `data-check`

```json
{
  "category": "fundamentals",
  "primary": {"provider": "fmp", "forward_pe": 22.5},
  "backup": {"provider": "yahoo", "forward_pe": 34.0}
}
```

### `regime-override`

```json
{
  "vix": 35.0,
  "market_regime": "Red"
}
```

## Error Handling

Missing files and invalid JSON fail with a concise CLI error. They do not trigger fallback to live data.

## Limitations

- No external provider/API integration.
- No live Massive/FMP/EDGAR/FRED calls.
- No real technical levels or financial analysis.
