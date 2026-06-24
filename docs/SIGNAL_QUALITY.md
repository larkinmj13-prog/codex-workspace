# Signal Quality Tiers

## Purpose

Signal Quality assigns a deterministic Phase 1 quality tier from supplied signal fields. It is not a backtested scoring model and does not perform financial analysis.

## Allowed Tiers

```text
A+
A
A-
B+
B
B-
C
D
F
```

## Key Inputs

Common supplied fields include:

- `thesis_strength`
- `entry_quality`
- `meaningful_caveats`
- `confidence`
- `risk_gate`
- `reward_risk`
- `min_reward_risk`
- `earnings_within_5_days`
- `event_risk_caveat`
- `severe_contradiction`
- `technical_levels_available`
- `market_regime`
- `defensive_setup`
- `danger_or_hedge_setup`

## Output

`assign_signal_quality(signal)` returns:

```json
{
  "tier": "A+|A|A-|B+|B|B-|C|D|F",
  "reason": "concise deterministic explanation"
}
```

## Caps

The Phase 1 implementation applies simple caps for low confidence, active risk gates, reward/risk below threshold, earnings proximity without accepted caveat, severe contradiction, missing technical levels, Red regime, and Black Ice regime.

## Limitations

- No external data calls.
- No real scoring engine.
- No invented financial thresholds.
- Tier inputs must be prepared by another layer.
