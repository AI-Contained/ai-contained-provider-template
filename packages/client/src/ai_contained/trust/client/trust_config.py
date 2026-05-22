"""TrustConfig — builds and holds TrustClient instances parsed from TRUST_SERVERS."""

import time
from collections.abc import Callable

import httpx

_sleep = time.sleep  # exposed for monkeypatching in tests

from ai_contained.trust.client.trust_client import TrustClient
from ai_contained.trust.client.trust_connection import TrustConnection

HttpClientFactory = Callable[[httpx.URL], httpx.Client]


def _default_http_client_factory(url: httpx.URL) -> httpx.Client:
    return httpx.Client(base_url=url)


class DuplicateSourceError(ValueError):
    def __init__(self, role: str) -> None:
        display = "wildcard" if role == "*" else f"role {role!r}"
        super().__init__(f"duplicate {display} in TRUST_SERVERS")


def _register_clients(
    parsed: dict[str, str | None],
    factory: HttpClientFactory,
    max_retries: int = 5,
) -> dict[str, TrustClient | None]:
    raise NotImplementedError


class TrustConfig:
    """Parsed registry from TRUST_SERVERS — maps role to TrustClient.

    Populated at startup; static for the lifetime of the process.
    """

    @staticmethod
    def _parse(raw: str) -> dict[str, str | None]:
        """Parse a comma-separated [role=]url string into {role: url | None}.

        - "" → {}
        - "http://server:8080" (no "=") → {"*": "http://server:8080"}
        - "aws=http://server:8080" → {"aws": "http://server:8080"}
        - "aws=" → {"aws": None}  (explicit deny)
        """
        if not raw:
            return {}
        result: dict[str, str | None] = {}
        for token in raw.split(","):
            token = token.strip()
            if not token:
                continue
            elif "=" in token:
                role, raw_url = token.split("=", 1)
                url: str | None = raw_url if raw_url else None
            else:
                role, url = "*", token

            if role in result:
                raise DuplicateSourceError(role)
            result[role] = url
        return result

    def __init__(self, trust_servers: str, factory: HttpClientFactory) -> None:
        self._clients: dict[str, TrustClient | None] = {}
        #raise NotImplementedError

    def get_client(self, role: str) -> TrustClient | None:
        """Return the TrustClient for a role, or None if not configured."""
        raise NotImplementedError


_instance: TrustConfig | None = None


def get_trust_config() -> TrustConfig | None:
    """Return the process-wide TrustConfig singleton, or None if not yet initialized."""
    return _instance


def init_trust_config(raw: str, factory: HttpClientFactory = _default_http_client_factory) -> TrustConfig:
    """Initialize (or reinitialize) the process-wide TrustConfig singleton."""
    global _instance
    if _instance is not None:
        _instance = None
    _instance = TrustConfig(raw, factory)
    return _instance
