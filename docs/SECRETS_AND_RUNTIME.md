# Secrets and Runtime Configuration

## Development

Use Codex Cloud environment secrets, local environment variables, or a local untracked `.env` file loaded into your shell.

Required provider variables for read-only stock-card validation:

- `FMP_API_KEY`
- `MASSIVE_API_KEY`

Optional provider variables:

- `FRED_API_KEY`
- `SEC_USER_AGENT`

## Scheduled / Cloud Runs

Use GitHub Actions Secrets for cloud validation runs.

Required secret names:

- `FMP_API_KEY`
- `MASSIVE_API_KEY`
- `FRED_API_KEY`
- `SEC_USER_AGENT`

Do not put keys in:

- prompts
- README
- docs
- `.env.example`
- tests
- fixtures
- committed `.env` files

## Provider behavior

Provider-backed commands read keys from runtime environment variables. If a required key is missing, provider commands should fail cleanly with a missing-key message.

Never print, log, echo, or persist secret values. It is safe to print whether a key is configured, but not the value.

## Current limitation

Provider-backed commands are read-only. They do not produce scores, ratings, buy/sell signals, technical levels, recommendations, position sizing, or trade instructions.
