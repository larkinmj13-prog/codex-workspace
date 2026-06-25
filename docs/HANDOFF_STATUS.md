# Handoff Status — Stock God Evidence Engine v6

Point-in-time handoff for continuing work (CI/provider integration brought green). For the
authoritative product spec see [`CODEX_HANDOFF_MASTER_SPEC.md`](CODEX_HANDOFF_MASTER_SPEC.md); for
running status see [`CURRENT_STATUS.md`](CURRENT_STATUS.md).

## Current state

- Repo: `larkinmj13-prog/codex-workspace`, default branch `main`.
- CI: **Read-Only Provider Validation** (`.github/workflows/read_only_provider_validation.yml`,
  `workflow_dispatch`, job `validate`) is **green**. `pytest`: 113 passed, 5 skipped; `ruff`: clean.
- Build: deterministic engine complete through Phase 3; Phase 4A–4C read-only provider foundations
  and Phase 5 read-only stock card implemented. **Not** yet built: provider-backed scoring, real
  technical levels, real fundamentals, options, dashboard/UI, live universe scans.

## What was broken and how it was fixed

| # | Symptom | Root cause | Fix (PR) |
|---|---------|-----------|----------|
| 1 | CI `Run tests` failed | `test_stock_card_live_missing_keys_fails_cleanly` made a live call in CI (env not cleared) instead of hitting the no-key branch | `monkeypatch.delenv` for `FMP_API_KEY`/`MASSIVE_API_KEY` to make the test env-independent (#2) |
| 2 | FMP `403 Forbidden` | `/api/v3/` legacy endpoints retired (keys created after 2025‑08‑31 are rejected) | Migrate `FMPClient` to the **stable** API (#3) |
| 3 | FMP `401 Unauthorized` | Invalid `FMP_API_KEY` secret value (wrong / double‑pasted) | Set the correct key; also strip surrounding whitespace from keys at config load (#4) |
| 4 | Massive `401 Unauthorized` | (a) aggregates path missing required `{from}/{to}` dates; (b) wrong auth scheme (`?apiKey=` vs required `Authorization: Bearer` header); (c) wrong `MASSIVE_API_KEY` value | Add date window (#3); Bearer header (#5); set the correct key; label each provider call for diagnosis (#5) |
| 5 | Intermittent Massive `401` | Massive free/"DELAYED" tier rate-limits (valid key, transient 401s; likely daily quota) | Validation step retries with backoff (4×, 20/40/60s) and warns instead of failing (#6) |

## Provider facts (verified working)

- **FMP** — stable API, base `https://financialmodelingprep.com/stable`, query-param style
  (`profile?symbol=MSFT`), auth `?apikey=<key>`. Normalizers read stable field names
  (`marketCap`, `epsActual`) with fallback to legacy (`mktCap`, `eps`). Configured key works.
- **Massive** — host `api.massive.com`, Polygon-style paths; aggregates require
  `/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from}/{to}`; auth is an
  `Authorization: Bearer <key>` **header** (not a query param). Free/DELAYED tier is rate-limited —
  expect intermittent 401s on repeated runs (handled by retry/warn).
- **FRED** — `FRED_API_KEY` not configured; the stock card runs with `--no-macro`, so FRED isn't exercised.

## Secrets / security

- GitHub Actions secrets set and valid: `FMP_API_KEY`, `MASSIVE_API_KEY`. Optional: `FRED_API_KEY`,
  `SEC_USER_AGENT`.
- Both live keys were shown during debugging; the owner chose not to rotate (exposure contained to a
  private session). If rotated later, the old key dies immediately — update the matching secret and
  re-run.
- **Never** put keys in repo, tests, fixtures, docs, logs, or commits. Secrets only.

## Code areas

- `src/stockgod/data/fmp.py` — stable URLs, query params, field fallbacks.
- `src/stockgod/data/massive.py` — Bearer auth, date-range aggregates path.
- `src/stockgod/data/config.py` — `load_provider_config` strips key whitespace via `_secret()`.
- `src/stockgod/reports/stock_card.py` — `fetch_live_stock_card_inputs` labels each provider call.
- `.github/workflows/read_only_provider_validation.yml` — retry + warn validation step.
- Tests use injected mock sessions; unit tests must **not** call live provider APIs. Live smoke tests
  (`tests/test_live_provider_smoke.py`) are skipped unless `RUN_LIVE_PROVIDER_SMOKE=1`.

## To finish the project (next phases — follow the master spec; do not invent rules)

The product vision in `CODEX_HANDOFF_MASTER_SPEC.md` is not yet built. Remaining, in spec order:

1. Harden read-only providers + fixture coverage (order: config/interfaces → FMP fundamentals/
   earnings/profile → Massive price/OHLCV → SEC EDGAR filings/Form 4 → FRED macro → Yahoo fallback).
2. Connect live provider data into the deterministic analysis layer (signals / confidence / Daily Pop),
   which currently runs on supplied/mock JSON only.
3. Then, **only per source-of-truth docs**: provider-backed scoring, real technical levels, real
   fundamental scoring, options analysis, real Daily Pop universe scans, dashboard/UI.

Do not invent financial thresholds, price levels, scoring rules, or EDGAR behavior not defined in the
master spec. Preserve the current read-only / no-advice guarantees (no scores, ratings, buy/sell
signals, technical levels, or recommendations).

## Running the validation

Actions → **Read-Only Provider Validation** → Run workflow → branch `main` (or `gh workflow run`).
A throttled run is **green with warnings**; a healthy run renders live MSFT/SPY cards.

## Cosmetic / non-blocking

- GitHub warns that `actions/checkout@v4` + `actions/setup-python@v5` run on deprecated Node 20.
  Bump versions whenever convenient; not required.
