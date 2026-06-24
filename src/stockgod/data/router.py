"""Provider router for read-only data clients."""

from __future__ import annotations

from stockgod.data.config import ProviderConfig, load_provider_config
from stockgod.data.edgar import EdgarClient
from stockgod.data.fmp import FMPClient
from stockgod.data.fred import FREDClient
from stockgod.data.massive import MassiveClient
from stockgod.data.yahoo import YahooFallbackClient


def get_price_provider(config: ProviderConfig | None = None):
    config = config or load_provider_config()
    return MassiveClient(config=config)


def get_fundamentals_provider(config: ProviderConfig | None = None):
    config = config or load_provider_config()
    return FMPClient(config=config)


def get_earnings_provider(config: ProviderConfig | None = None):
    config = config or load_provider_config()
    return FMPClient(config=config)


def get_insider_discovery_provider(config: ProviderConfig | None = None):
    config = config or load_provider_config()
    return FMPClient(config=config)


def get_insider_verification_provider(config: ProviderConfig | None = None):
    config = config or load_provider_config()
    return EdgarClient(config=config)


def get_macro_provider(config: ProviderConfig | None = None):
    config = config or load_provider_config()
    return FREDClient(config=config)


def get_fallback_provider(config: ProviderConfig | None = None):
    config = config or load_provider_config()
    return YahooFallbackClient(config=config)
