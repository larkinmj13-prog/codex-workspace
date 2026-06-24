import pytest

from stockgod.data.config import ProviderConfig
from stockgod.data.edgar import EdgarClient
from stockgod.data.errors import MissingApiKeyError, ProviderNotImplementedError


class Response:
    status_code = 200
    def json(self):
        return {"filings": {"recent": {"form": ["4", "10-K"]}}}


class Session:
    def get(self, url, params=None, headers=None, timeout=20):
        assert headers["User-Agent"] == "agent"
        return Response()


def test_edgar_requires_sec_user_agent_for_request_attempt():
    with pytest.raises(MissingApiKeyError):
        EdgarClient(config=ProviderConfig()).get_company_submissions("0000789019")


def test_edgar_normalized_output_shape():
    result = EdgarClient(config=ProviderConfig(sec_user_agent="agent"), session=Session(), base_url="https://example.test").get_company_submissions("789019")
    assert result["provider"] == "sec_edgar"
    assert result["cik"] == "0000789019"
    assert {"provider", "as_of", "data", "raw"}.issubset(result)


def test_edgar_form4_raw_stub_is_clean():
    with pytest.raises(ProviderNotImplementedError):
        EdgarClient(config=ProviderConfig(sec_user_agent="agent"), session=Session()).fetch_form4_raw("x")
