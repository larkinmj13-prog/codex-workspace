# Stock God Evidence Engine v6

Deterministic scaffold and functional core for the Stock God Evidence Engine v6 build.

## Current Status

The deterministic v6 build is complete through Phase 3:

- Phase 0: repository/package/docs scaffold
- Phase 1: core deterministic signal logic
- Phase 1 refinement: CLI/docs polish
- Phase 2: screening, confidence, disagreement, and regime logic
- Phase 2 refinement: JSON CLI inputs and integration tests
- Phase 3: portfolio impact, post-mortem, and deeper journal layer

No live data is implemented yet. All commands use supplied JSON, fixtures, or deterministic sample/mock data.

## Current CLI Commands

```bash
python -m stockgod
python -m stockgod review-signal
python -m stockgod why-now
python -m stockgod journal
python -m stockgod journal --path PATH
python -m stockgod journal-add TICKER
python -m stockgod journal-add TICKER --path PATH
python -m stockgod journal-review TICKER
python -m stockgod journal-review TICKER --path PATH
python -m stockgod pop
python -m stockgod pop --input PATH
python -m stockgod confidence
python -m stockgod confidence --input PATH
python -m stockgod data-check
python -m stockgod data-check --input PATH
python -m stockgod regime-override
python -m stockgod regime-override --input PATH
python -m stockgod portfolio-impact TICKER
python -m stockgod portfolio-impact TICKER --input PATH
python -m stockgod postmortem TICKER
python -m stockgod postmortem TICKER --input PATH
python -m stockgod stock-card TICKER
python -m stockgod stock-card TICKER --input PATH
python -m stockgod stock-card TICKER --live
python -m stockgod provider-check fmp --ticker MSFT
python -m stockgod provider-check massive --ticker SPY
python -m stockgod provider-check edgar --ticker MSFT
python -m stockgod provider-check fred --series DGS10
python -m stockgod provider-check yahoo --ticker MSFT
python -m stockgod build-input TICKER --input PATH
python -m stockgod build-input TICKER --live --no-macro
python -m stockgod analyze TICKER --input PATH
python -m stockgod analyze TICKER --live --no-macro
python -m stockgod watchlist-digest --input PATH
python -m stockgod watchlist-digest --tickers MSFT,SPY --live --no-macro
```

The `build-input` / `analyze` / `watchlist-digest` commands are the provider-evidence MVP — a fact-only, read-only layer over the deterministic engine (no scores, ratings, technical levels, or buy/sell). See [docs/PROVIDER_EVIDENCE.md](docs/PROVIDER_EVIDENCE.md).

## Current Limitation

Default commands remain deterministic and supplied/mock-data oriented. Phase 4/5 provider commands can make explicit read-only live requests only when configured keys are supplied; they do not generate recommendations or financial advice.

This repository does **not** currently implement:

- Provider-backed scoring
- Provider-backed recommendations
- Real technical levels
- Real fundamental scoring
- Options analysis
- Dashboard/UI
- New scoring logic
- Automated live market scans

Do not treat current outputs as financial advice. The Phase 5 stock card is read-only and does not emit scores, ratings, buy/sell signals, technical levels, position sizing, or recommendations.


## Runtime Secrets

Provider-backed commands require environment variables or GitHub Actions Secrets.

Required for read-only stock-card validation:

- `FMP_API_KEY`
- `MASSIVE_API_KEY`

Optional:

- `FRED_API_KEY`
- `SEC_USER_AGENT`

Never commit secrets. Do not place real keys in `.env.example`, README, docs, tests, fixtures, or prompts.

Example local PowerShell use:

```powershell
$env:FMP_API_KEY="LOCAL_ONLY"
$env:MASSIVE_API_KEY="LOCAL_ONLY"
$env:PYTHONPATH="src"

python -m stockgod stock-card MSFT --live --no-macro
```

## Test Commands

```bash
python -m pytest
ruff check .
```

## Smoke Test Commands

```bash
PYTHONPATH=src python -m stockgod pop --input tests/fixtures/phase2_pop_input.json
PYTHONPATH=src python -m stockgod confidence --input tests/fixtures/phase2_confidence_input.json
PYTHONPATH=src python -m stockgod data-check --input tests/fixtures/phase2_data_check_input.json
PYTHONPATH=src python -m stockgod regime-override --input tests/fixtures/phase2_regime_override_input.json
PYTHONPATH=src python -m stockgod portfolio-impact NVDA --input tests/fixtures/portfolio_impact_input.json
PYTHONPATH=src python -m stockgod postmortem NVDA --input tests/fixtures/postmortem_input.json
PYTHONPATH=src python -m stockgod journal-review NVDA --path tests/fixtures/journal_entries.json
PYTHONPATH=src python -m stockgod stock-card MSFT --input tests/fixtures/stock_card_msft.json
```

## Next Planned Phase

Next planned phase: **Phase 4A read-only provider integration**.

Planned providers:

- Massive Market Data: price/OHLCV, technicals, options later
- FMP Premium: fundamentals, valuation, earnings, news, insider discovery
- SEC EDGAR: filings and Form 4 verification
- FRED: macro/rates
- Yahoo Finance: fallback/sanity check only

Phase 4A adds read-only provider foundations only. It does not add real scoring, live reports, technical levels, trading, order execution, or automated recommendations. Provider checks fail gracefully when keys or optional dependencies are missing.
