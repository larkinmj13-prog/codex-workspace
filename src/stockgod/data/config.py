"""Environment-backed provider configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderConfig:
    market_data_provider: str = "massive"
    massive_api_key: str = ""
    fundamentals_provider: str = "fmp"
    fmp_api_key: str = ""
    earnings_provider: str = "fmp"
    news_provider: str = "fmp"
    insider_discovery_provider: str = "fmp"
    insider_verification_provider: str = "sec_edgar"
    fred_api_key: str = ""
    sec_user_agent: str = ""
    yahoo_fallback_enabled: bool = True
    output_dir: str = "reports"
    state_path: str = "data/state/scans.json"
    journal_path: str = "data/state/decision_journal.json"
    model_version: str = "v6.0"


def load_provider_config(environ: dict[str, str] | None = None) -> ProviderConfig:
    """Load provider config from environment variables without requiring secrets."""
    env = environ if environ is not None else os.environ
    return ProviderConfig(
        market_data_provider=env.get("MARKET_DATA_PROVIDER", "massive"),
        massive_api_key=env.get("MASSIVE_API_KEY", env.get("STOCKGOD_MARKET_DATA_API_KEY", "")),
        fundamentals_provider=env.get("FUNDAMENTALS_PROVIDER", "fmp"),
        fmp_api_key=env.get("FMP_API_KEY", ""),
        earnings_provider=env.get("EARNINGS_PROVIDER", "fmp"),
        news_provider=env.get("NEWS_PROVIDER", "fmp"),
        insider_discovery_provider=env.get("INSIDER_DISCOVERY_PROVIDER", "fmp"),
        insider_verification_provider=env.get("INSIDER_VERIFICATION_PROVIDER", "sec_edgar"),
        fred_api_key=env.get("FRED_API_KEY", ""),
        sec_user_agent=env.get("SEC_USER_AGENT", env.get("STOCKGOD_EDGAR_USER_AGENT", "")),
        yahoo_fallback_enabled=env.get("YAHOO_FALLBACK_ENABLED", "true").lower() in {"1", "true", "yes", "on"},
        output_dir=env.get("OUTPUT_DIR", "reports"),
        state_path=env.get("STATE_PATH", "data/state/scans.json"),
        journal_path=env.get("JOURNAL_PATH", "data/state/decision_journal.json"),
        model_version=env.get("MODEL_VERSION", "v6.0"),
    )
