"""TrustStore — registry of trusted clients."""

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address

IPAddress = IPv4Address | IPv6Address


@dataclass(frozen=True)
class RegisteredClient:
    """Public keys for a registered client."""

    signing_public_key: str
    encryption_public_key: str


class TrustStore:
    """Holds registered client public keys, keyed by client IP address."""

    def __init__(self) -> None:
        self._clients: dict[IPAddress, RegisteredClient] = {}


_instance: TrustStore | None = None


def get_trust_store() -> TrustStore:
    """Return the process-wide TrustStore singleton."""
    global _instance
    if _instance is None:
        _instance = TrustStore()
    return _instance
