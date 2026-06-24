# Why Now / Why Not

## Purpose

The Why Now / Why Not helper turns supplied boolean signal fields into concise deterministic timing and caution text. It does not call external data providers or infer missing market context.

## Inputs

Supported Why Now trigger fields include:

- `buy_zone_reached`
- `breakout_confirmed`
- `pullback_into_buy_zone`
- `signal_label_improved`
- `risk_gate_removed`
- `market_regime_improved`
- `earnings_risk_cleared`
- `qualifying_insider_event`
- `valuation_improved`
- `confidence_improved`

Supported Why Not warning fields include:

- `earnings_within_5_days`
- `vix_or_regime_stress`
- `reward_risk_below_threshold`
- `valuation_stretched`
- `confidence_low`
- `technical_setup_extended`
- `market_regime_red_or_black_ice`
- `unresolved_contradiction`
- `material_data_disagreement`
- `missing_technical_levels`

## Output

`generate_why_now_why_not(signal)` returns:

```json
{
  "why_now": "concise trigger text",
  "why_not": "concise caveat text"
}
```

Fallbacks are:

- Why Now: `No urgent trigger; watch only.`
- Why Not: `No major caveat identified.`

## Limitations

- Uses only supplied fields.
- Does not calculate valuation, levels, earnings dates, VIX, or regime.
- Does not provide financial advice.
