from stockgod.data.config import ProviderConfig
from stockgod.data.edgar import EdgarClient
from stockgod.data.fmp import FMPClient
from stockgod.data.fred import FREDClient
from stockgod.data.massive import MassiveClient
from stockgod.data.router import get_fallback_provider, get_fundamentals_provider, get_insider_verification_provider, get_macro_provider, get_price_provider
from stockgod.data.yahoo import YahooFallbackClient


def test_router_creation_does_not_trigger_network_calls():
    config = ProviderConfig()
    assert isinstance(get_price_provider(config), MassiveClient)
    assert isinstance(get_fundamentals_provider(config), FMPClient)
    assert isinstance(get_insider_verification_provider(config), EdgarClient)
    assert isinstance(get_macro_provider(config), FREDClient)
    assert isinstance(get_fallback_provider(config), YahooFallbackClient)
