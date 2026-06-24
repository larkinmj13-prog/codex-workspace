import pytest

from stockgod.data.config import ProviderConfig
from stockgod.data.errors import MissingApiKeyError
from stockgod.data.fmp import FMPClient


class Response:
    status_code = 200
    def json(self):
        return [{"symbol": "MSFT"}]


class Session:
    def __init__(self):
        self.calls = []
    def get(self, url, params=None, headers=None, timeout=20):
        self.calls.append((url, params, headers, timeout))
        return Response()


def test_fmp_missing_api_key_raises_clean_error():
    with pytest.raises(MissingApiKeyError):
        FMPClient(config=ProviderConfig()).get_company_profile("MSFT")


def test_fmp_normalized_output_shape():
    session = Session()
    result = FMPClient(config=ProviderConfig(fmp_api_key="key"), session=session, base_url="https://example.test").get_company_profile("msft")
    assert result["provider"] == "fmp"
    assert result["ticker"] == "MSFT"
    assert {"provider", "as_of", "data", "raw"}.issubset(result)
    assert session.calls
