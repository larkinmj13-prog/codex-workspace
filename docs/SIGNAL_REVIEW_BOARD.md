# Signal Review Board

## Purpose

The Signal Review Board is a Phase 1 deterministic guardrail for already-prepared signal objects. It does not fetch data, calculate financial scores, or provide financial advice.

## Input Fields

Expected signal fields include:

- `risk_gate`
- `confidence`
- `missing_key_data`
- `earnings_within_5_days`
- `event_risk_caveat`
- `reward_risk`
- `min_reward_risk`
- `technical_levels_available`
- `data_conflict_unresolved`
- `classification_uncertain`
- `severe_contradiction`
- `market_regime`
- `why_now`

Missing optional fields are handled with safe defaults.

## Output Fields

`review_signal(signal)` returns:

```json
{
  "result": "pass|conditional|fail|no_action",
  "reason": "concise explanation",
  "actionability": "actionable|watch_only|avoid|do_nothing"
}
```

## Example

```python
from stockgod.analysis.signal_review_board import review_signal

review_signal({"risk_gate": "none", "confidence": "High"})
```

## Limitations

- No external data calls.
- No real scoring engine.
- No invented price levels or technical levels.
- Inputs must already be prepared by another layer.
