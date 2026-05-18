"""TrustStore — registry of trusted clients.

Clients register once via POST /trust/register, providing their Ed25519 signing key
and Curve25519 encryption key. Registration is gated by IP address — one registration
per client IP is permitted. Subsequent requests are authenticated by verifying the
Ed25519 signature against the stored signing key.
"""

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address

# Union type for both IPv4 and IPv6 client addresses.
IPAddress = IPv4Address | IPv6Address


@dataclass(frozen=True)
class RegisteredClient:
    """Public keys for a registered client.

    frozen=True: keys are immutable after registration — a client cannot
    re-register from the same IP with different keys.
    """

    signing_public_key: str   # Ed25519 verify key — used to authenticate each request
    encryption_public_key: str  # Curve25519 public key — used to encrypt responses


class TrustStore:
    """In-memory registry of clients that have completed key exchange.

    Keyed by client IP address — enforces one registration per IP.
    Call reset() between tests to clear state.
    """

    def __init__(self) -> None:
        self._clients: dict[IPAddress, RegisteredClient] = {}

    def reset(self) -> None:
        """Clear all registered clients — intended for use in tests only."""
        self._clients.clear()


# Module-level singleton — one TrustStore per process in production.
# Tests bypass this by passing TrustStore() directly to register().
_instance: TrustStore | None = None


def get_trust_store() -> TrustStore:
    """Return the process-wide TrustStore singleton."""
    global _instance
    if _instance is None:
        _instance = TrustStore()
    return _instance
