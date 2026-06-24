import pytest

from stockgod.data.config import ProviderConfig
from stockgod.data.errors import MissingApiKeyError
from stockgod.data.fred import FREDClient


class Response:
    status_code = 200
    def json(self):
        return {"observations": []}


class Session:
    def get(self, url, params=None, headers=None, timeout=20):
        return Response()


def test_fred_missing_api_key_raises_clean_error():
    with pytest.raises(MissingApiKeyError):
        FREDClient(config=ProviderConfig()).get_series("DGS10")


def test_fred_normalized_output_shape():
    result = FREDClient(config=ProviderConfig(fred_api_key="key"), session=Session(), base_url="https://example.test").get_series("DGS10")
    assert result["provider"] == "fred"
    assert result["series_id"] == "DGS10"
    assert {"provider", "as_of", "data", "raw"}.issubset(result)
