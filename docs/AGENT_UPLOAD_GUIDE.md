# Agent Upload Guide

Use this guide when continuing Stock God Evidence Engine v6 work in this repository.

## Before Implementing

1. Read `docs/CODEX_HANDOFF_MASTER_SPEC.md`.
2. Confirm the requested task is within the current phase.
3. Do not implement financial analysis behavior unless the source-of-truth docs define the required rules.
4. Do not invent market levels, scoring thresholds, EDGAR behavior, or external-data assumptions.

## Phase 0 Boundary

Phase 0 includes only:

- Documentation.
- Project metadata.
- Environment example.
- Skeleton package.
- Placeholder CLI.
- Smoke test.

Phase 0 excludes:

- Analysis modules.
- Market data access.
- EDGAR/Form 4 verification.
- Scoring logic.
- State persistence.
- Daily Pop reports.
- Portfolio analysis.
- Post-mortems.
