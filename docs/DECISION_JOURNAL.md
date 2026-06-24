# Decision Journal

## Purpose

The Basic Decision Journal stores Phase 1 deterministic decision snapshots. It records supplied signal context but does not perform financial analysis or outcome attribution.

## Storage Paths

Default intended paths:

```text
data/state/decision_journal.json
reports/journal/decision_journal.md
```

The helper functions accept caller-provided paths for testability.

## Functions

- `load_journal(path)` loads JSON entries or returns an empty list when absent.
- `save_journal(entries, path)` writes normalized entries as JSON.
- `add_journal_entry(entry, path)` fills safe defaults, appends, saves, and returns the saved entry.
- `render_journal_markdown(entries)` renders concise Markdown.

## Entry Fields

Entries include identifiers, ticker, date, price, signal summary, signal quality, own/enter decisions, best action, stock type, composite, confidence, risk gate, market regime, levels, Why Now / Why Not, bull/bear cases, divergences, invalidation, data quality, model version, outcome, and review date.

Missing fields are filled with safe defaults. Invalid `best_action` values are replaced with `do_nothing`.

## Limitations

- No database.
- No external data calls.
- No performance analysis.
- No post-mortem logic.

## Phase 3 Integration

Additional helpers support outcome updates, ticker filtering, open-entry filtering, and meaningful-change auto-journaling. Auto-journaling de-duplicates repeated same-ticker/signal/date entries unless the material reason changed.

Functions added:

- `update_journal_outcome(...)`
- `find_entries_by_ticker(...)`
- `find_open_entries(...)`
- `maybe_auto_journal_signal(...)`
