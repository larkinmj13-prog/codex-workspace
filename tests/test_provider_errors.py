from stockgod.data.errors import MissingApiKeyError, ProviderError, ProviderNotImplementedError, ProviderRequestError, ProviderResponseError


def test_provider_errors_are_clean_exception_types():
    assert issubclass(MissingApiKeyError, ProviderError)
    assert issubclass(ProviderRequestError, ProviderError)
    assert issubclass(ProviderResponseError, ProviderError)
    assert issubclass(ProviderNotImplementedError, ProviderError)
