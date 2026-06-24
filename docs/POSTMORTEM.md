# Post-Mortem Mode

## Purpose

Post-Mortem Mode reviews supplied prior journal entries and subsequent context to classify what worked, what failed, and what the model should learn.

## Inputs

Use `build_postmortem(payload)` with a ticker, original journal entry, elapsed time, current/subsequent context, invalidation status, and major changes.

## Output

Returns ticker, original signal, what happened, right/wrong notes, error type, risk-control status, invalidation status, model lesson, and recommended adjustment.

## Example

```bash
python -m stockgod postmortem NVDA --input tests/fixtures/postmortem_input.json
```

## Limitations

Post-mortem requires a prior journal entry or supplied input. It is diagnostic, not proof the model was right or wrong without enough time and context.
