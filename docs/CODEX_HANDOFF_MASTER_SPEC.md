# Stock God Evidence Engine v6 — Master Spec

This document is the source of truth for the Stock God Evidence Engine v6 project in this repository.

## Current Build Status

The deterministic Stock God Evidence Engine v6 build is complete through Phase 3, and Phase 4A read-only provider foundations are implemented. The repository currently contains deterministic, supplied/mock-data-only modules, reports, state helpers, CLI commands, fixtures, and tests. No live provider data, external API integration, real technical levels, real fundamentals, options analysis, dashboard/UI, or new scoring logic is implemented yet.

Phase 4A is limited to read-only provider adapters, router/config foundations, CLI checks, fixtures, docs, and tests unless a later source-of-truth handoff explicitly broadens scope.


## Current Implementation Status

The deterministic v6 build is complete through Phase 3.

Completed:

- Phase 0 scaffold
- Phase 1 core deterministic logic
- Phase 1 CLI/docs refinement
- Phase 2 screening/confidence logic
- Phase 2 JSON CLI input refinement
- Phase 3 portfolio/post-mortem/journal layer

Current latest confirmed commit:
`b898e2a Implement Stock God phase 3 portfolio journal layer`

Current test status:
`81 passed`
`ruff check .` passed

No live data providers are implemented yet. Do not assume live data exists. All current modules remain deterministic and supplied/mock-data only.

Next strategic phase:
Phase 4A — read-only provider integration for Massive, FMP, SEC EDGAR, FRED, and Yahoo fallback.

## Phase 0 Scope

Phase 0 establishes the repository foundation only:

- Source-of-truth documentation.
- Python project metadata.
- Environment variable example file.
- Skeleton `stockgod` package.
- Placeholder CLI.
- One smoke test.

Phase 0 must not implement analysis modules, scoring logic, market data access, EDGAR access, state persistence, or report generation.


## Phase 1 Scope

Phase 1 adds the smallest useful deterministic core logic for:

- Signal Review Board.
- Why Now / Why Not.
- Signal Quality Tiers.
- Basic Decision Journal.
- Minimal CLI commands that use sample data and clearly identify themselves as deterministic scaffolds.

Phase 1 must not implement Daily Pop, Confidence Breakdown, Data Disagreement Alerts, VIX / Regime Override, Portfolio Impact, Post-Mortem, external data providers, a real scoring engine, technical levels, financial analysis, or options analysis.


## Phase 2 Scope

Phase 2 adds deterministic screening and confidence logic for supplied/mock signal objects:

- Categorized Daily Pop Screen.
- Confidence Breakdown.
- Data Disagreement Alerts.
- VIX / Market Regime Override.
- VIX Extremes Rule enforcement.

Phase 2 must not implement Portfolio Impact, Post-Mortem, external data providers, Massive/FMP/EDGAR/FRED integrations, real technical levels, real financial analysis, options analysis, or dashboard/UI behavior.

## Phase 3 Scope

Phase 3 adds the final deterministic functional layer for supplied/mock inputs:

- Portfolio Impact Analysis.
- Post-Mortem Mode.
- Deeper Decision Journal integration.
- CLI wiring for remaining v6 deterministic commands.

Phase 3 must not implement external data providers, Massive/FMP/EDGAR/FRED integrations, real technical levels, real financial analysis, options analysis, dashboard/UI behavior, real universe fetching, formal JSON schema validation, or `--output` report writing.

## Phase 4A Scope

Phase 4A adds read-only provider integration foundations for FMP, Massive, SEC EDGAR, FRED, and Yahoo fallback. It introduces provider configuration, interfaces, shared errors, provider clients, router helpers, provider-check CLI wiring, tests, and documentation.

Phase 4A must not implement trading, order execution, automated recommendations, real scoring changes, technical level engines, options analytics, dashboard/UI behavior, real Daily Pop universe scans, background schedulers, or write actions to external services.

## Source-of-Truth Hierarchy

1. `docs/CODEX_HANDOFF_MASTER_SPEC.md` is authoritative when present.
2. If the master spec is absent, `docs/CODEX_HANDOFF_ADDENDUM_V6.md` is the current source-of-truth spec.
3. Implementation must not invent financial thresholds, price levels, scoring rules, or external-data behavior not defined in source-of-truth documentation.

## Project Target

Stock God Evidence Engine v6.

## Core Rules to Preserve

1. Phone-card default.
2. Deep dive on request.
3. Long-term investor default profile.
4. Fundamentals / valuation = thesis.
5. Technicals = timing.
6. Separate `Own it?` and `Enter now?`.
7. Risk gate and score caps.
8. Confidence as data-quality label.
9. No hallucinated levels.
10. Earnings proximity on every card.
11. Insider code P necessary but not sufficient.
12. EDGAR/Form 4 verification for material insider signals.
13. Stock Type Classifier.
14. Classification-aware scoring.
15. Expert Lens Module.
16. Professor Mode.
17. Daily Pop Screen.
18. Learning Archive.
19. State / delta system.
20. Multiple-choice setup UX.
21. VIX extremes are contextual, not directional.

## VIX Extremes Rule

VIX extremes are contextual, not directional. Low VIX may indicate complacency risk but cannot trigger a standalone sell signal. High VIX may indicate panic/stress and possible contrarian opportunity but cannot trigger a standalone strong buy. VIX must be confirmed by price action, breadth, trend, support/reclaim levels, credit/rates, and market regime before affecting actionable buy/sell conclusions.

## Handoff Blocks

### Block 1: Documentation / Spec Hygiene

Status in this repo after Phase 0: started.

Expected scope:

- Source-of-truth spec.
- Upload or agent guide.
- Repository organization.
- Implementation order.
- Non-negotiable behavior rules.
- Testing expectations.

### Block 2: Core v6 Evidence Modules

Status in this repo after Phase 1: smallest useful deterministic implementation complete.

Implemented Phase 1 modules:

- `src/stockgod/analysis/signal_review_board.py`
- `src/stockgod/analysis/why_now.py`
- `src/stockgod/analysis/signal_quality.py`
- `src/stockgod/state/decision_journal.py`

Implemented Phase 1 features:

- Signal Review Board.
- Why Now / Why Not.
- Signal Quality Tiers.
- Basic Decision Journal.

### Block 3: Daily Pop and Market Context

Status in this repo after Phase 2: smallest useful deterministic implementation complete.

Implemented Phase 2 modules:

- `src/stockgod/reports/daily_pop.py`
- `src/stockgod/analysis/confidence_breakdown.py`
- `src/stockgod/analysis/data_disagreements.py`
- `src/stockgod/analysis/regime_override.py`

Expected future features:

- Categorized Daily Pop.
- Confidence Breakdown.
- Data Disagreement Alerts.
- VIX / Market Regime Override.
- VIX Extremes Rule.

### Block 4: Remaining v6 Expansion

Status in this repo after Phase 3: smallest useful deterministic implementation complete.

Implemented Phase 3 modules:

- `src/stockgod/analysis/portfolio_impact.py`
- `src/stockgod/analysis/postmortem.py`

Expected future features:

- Portfolio Impact Analysis.
- Post-Mortem Mode.
- Deeper Decision Journal integration.
- CLI wiring for remaining v6 commands.

## Placeholder CLI Behavior

The Phase 0 CLI exists only to verify packaging and command wiring. It may report that Stock God Evidence Engine v6 is scaffolded, but it must not perform stock analysis or imply that analysis modules are implemented.

## Testing Expectations

Phase 0 must include at least one smoke test proving the package imports and the placeholder CLI can be invoked.
