# Portfolio Impact

## Purpose

Portfolio Impact determines whether a supplied ticker helps the portfolio, not just whether it looks attractive in isolation.

## Inputs

Use `analyze_portfolio_impact(signal)` with a standalone signal, ticker context, factor exposures, risk gate, confidence, and optional holdings.

## Output

Returns standalone read, portfolio read, reason, suggested role, sizing implication, concentration flags, and diversification benefit.

## Example

```bash
python -m stockgod portfolio-impact NVDA --input tests/fixtures/portfolio_impact_input.json
```

## Limitations

Without holdings, analysis is limited and does not hallucinate portfolio exposure. No external data is fetched.
