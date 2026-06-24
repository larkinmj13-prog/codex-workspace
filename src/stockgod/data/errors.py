"""Shared provider errors."""

class ProviderError(Exception):
    """Base provider error."""


class MissingApiKeyError(ProviderError):
    """Required API key or user-agent is missing."""


class ProviderRequestError(ProviderError):
    """Provider request failed."""


class ProviderResponseError(ProviderError):
    """Provider response could not be normalized."""


class ProviderNotImplementedError(ProviderError):
    """Provider capability or optional dependency is not available."""
