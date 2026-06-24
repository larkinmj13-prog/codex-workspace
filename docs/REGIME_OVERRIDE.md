# VIX / Market Regime Override

## Purpose

Regime Override turns supplied VIX/context fields into confirmation and threshold guidance. VIX is contextual, not directional.

## Output

`build_regime_override(signal)` returns override status, regime adjustment, reason, minimum R:R/confidence requirements, and `standalone_signal: false`.

## VIX Extremes Rule

- VIX <= 13 must not create a sell signal.
- VIX >= 35 must not create a strong buy signal.
- VIX >= 35 may return panic/washout context and require confirmation.
- VIX > 25 suppresses marginal Buy Setups.
- VIX > 30 may return Black Ice or panic context, but only as regime context.
- No VIX-only input can produce final Buy Setup or Sell Risk.

## Limitations

No term-structure inversion is inferred when term-structure data is missing. No external data is fetched.
