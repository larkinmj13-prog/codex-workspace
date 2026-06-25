# Provider Evidence Layer (MVP)

Connects real read-only provider data to the existing deterministic engine. It is
**fact-only and conservative**: it reports what providers returned and how fresh it
is, derives a data-quality confidence label, and runs the engine on those facts.
It never scores, rates, ranks, computes technical levels, infers buy/sell intent,
or fabricates missing values.

## Compliance boundary (per `CODEX_HANDOFF_MASTER_SPEC.md`)

Implemented (factual, no invented rules):

- Evidence snapshot — identity, latest price/volume, fetched bar window, earnings
  date + 5-day proximity, optional macro, and a per-category data-quality map.
- Engine input — populates only factually-determinable fields. Judgment fields the
  spec defines no mapping for (`thesis_strength`, `entry_quality`, `reward_risk`,
  `risk_gate`, `market_regime`, `severe_contradiction`) are left **unset**, so the
  engine applies its own conservative defaults. `technical_levels_available` is
  always `False` (this layer never computes levels — "no hallucinated levels").
- Provider-backed confidence — the master spec defines confidence as a data-quality
  label, so it is derived directly from data freshness/presence.

Deliberately **not** implemented (would require inventing rules the spec leaves
undefined — out of scope until the spec defines them):

- Provider-backed scoring/tiers, reward:risk, risk gates.
- Real technical levels, market-regime classification.
- A true Daily Pop *screen* with material-change detection over a universe.

## Commands

```bash
# Engine input JSON from provider evidence (read-only)
python -m stockgod build-input MSFT --input tests/fixtures/stock_card_msft.json --as-of 2026-06-24
python -m stockgod build-input MSFT --input tests/fixtures/stock_card_msft.json --snapshot
python -m stockgod build-input MSFT --live --no-macro

# Conservative single-stock evidence read
python -m stockgod analyze MSFT --input tests/fixtures/stock_card_msft.json --as-of 2026-06-24
python -m stockgod analyze MSFT --live --no-macro

# Bounded evidence digest for an explicit ticker list (NOT a screen)
python -m stockgod watchlist-digest --input tests/fixtures/evidence/watchlist_payloads.json --as-of 2026-06-24
python -m stockgod watchlist-digest --tickers MSFT,SPY --live --no-macro
```

`--input` takes the same normalized provider envelopes the read-only stock card
consumes (`profile` / `daily_bars` / `earnings` / `macro`); `watchlist-digest --input`
takes a JSON array of those payloads. `--as-of YYYY-MM-DD` overrides "today" for
deterministic freshness / earnings-proximity (used by tests).

## Inputs / outputs

- Input: provider envelopes (live via configured keys, or supplied JSON).
- `build-input` output: a deterministic-engine signal dict (or the raw snapshot with
  `--snapshot`).
- `analyze` output: data-quality confidence, a conservative review (typically
  `conditional` / `watch_only` because no technical levels are computed), the
  signal-quality tier, and an explicit read-only disclaimer.
- `watchlist-digest` output: one line per supplied ticker (confidence, review,
  factual flags). Bounded to the supplied tickers; no universe scan.

## Limits

Read-only. No scores, ratings, price targets, technical levels, position sizing, or
buy/sell recommendations. Unknown facts are recorded as `missing`, never fabricated.
Unit tests use supplied fixtures and must not call live provider APIs.
