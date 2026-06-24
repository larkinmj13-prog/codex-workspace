import pytest

from stockgod.data.config import ProviderConfig
from stockgod.data.errors import MissingApiKeyError
from stockgod.data.massive import MassiveClient


class Response:
    status_code = 200
    def json(self):
        return {"results": []}


class Session:
    def get(self, url, params=None, headers=None, timeout=20):
        return Response()


def test_massive_missing_api_key_raises_clean_error():
    with pytest.raises(MissingApiKeyError):
        MassiveClient(config=ProviderConfig()).get_daily_bars("SPY")


def test_massive_normalized_output_shape():
    result = MassiveClient(config=ProviderConfig(massive_api_key="key"), session=Session(), base_url="https://example.test").get_daily_bars("spy")
    assert result["provider"] == "massive"
    assert result["ticker"] == "SPY"
    assert {"provider", "as_of", "data", "raw"}.issubset(result)
