import pytest

from stockgod.data.config import ProviderConfig
from stockgod.data.errors import ProviderNotImplementedError
from stockgod.data.yahoo import YahooFallbackClient


class FakeTicker:
    fast_info = {"last_price": 100}


class FakeYF:
    @staticmethod
    def Ticker(ticker):
        return FakeTicker()


def test_yahoo_optional_dependency_behavior_when_disabled():
    with pytest.raises(ProviderNotImplementedError):
        YahooFallbackClient(config=ProviderConfig(yahoo_fallback_enabled=False)).get_quote_snapshot("MSFT")


def test_yahoo_normalized_output_shape_with_injected_dependency():
    result = YahooFallbackClient(yfinance_module=FakeYF()).get_quote_snapshot("msft")
    assert result["provider"] == "yahoo"
    assert result["ticker"] == "MSFT"
    assert {"provider", "as_of", "data", "raw"}.issubset(result)
