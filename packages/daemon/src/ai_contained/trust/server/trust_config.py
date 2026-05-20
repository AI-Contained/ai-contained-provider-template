"""TrustConfig — allowlist of permitted clients parsed from TRUST_CLIENTS."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RoleSet:
    """Immutable set of allowed and denied roles for a client."""

    allowed: frozenset[str]  # explicit roles, or {"*"} for wildcard
    denied: frozenset[str]   # explicitly blocked roles

    def permits(self, role: str) -> bool:
        """Return True if role is allowed and not denied."""
        raise NotImplementedError


class TrustConfig:
    """Parsed allowlist from TRUST_CLIENTS — maps hostname to RoleSet.

    Populated at startup; static for the lifetime of the server.
    Call reset() in tests to reconfigure without reinstantiating.
    """

    @staticmethod
    def _parse(raw: str) -> dict[str, RoleSet]:
        """Parse a comma-separated role=hostname string into {hostname: RoleSet}.

        - "" or "none" → {}
        - "shell-provider" (no "=") → {"shell-provider": RoleSet({"*"}, {})}
        - "shell=shell-provider" → {"shell-provider": RoleSet({"shell"}, {})}
        - "shell=none" → {"none": RoleSet({}, {"shell"})}
        - multiple roles for same hostname are merged into one RoleSet
        """
        raise NotImplementedError

    def __init__(self, trust_clients: str) -> None:
        self._permitted: dict[str, RoleSet] = self._parse(trust_clients)

    def reset(self, trust_clients: str = "") -> None:
        """Reconfigure the allowlist — intended for use in tests only."""
        self._permitted = self._parse(trust_clients)

    def is_hostname_permitted(self, hostname: str) -> bool:
        """Return True if hostname appears in the allowlist."""
        raise NotImplementedError

    def is_role_permitted(self, hostname: str, role: str) -> bool:
        """Return True if hostname is permitted and granted the given role."""
        raise NotImplementedError


_instance: TrustConfig | None = None


def get_trust_config() -> TrustConfig:
    """Return the process-wide TrustConfig singleton."""
    global _instance
    if _instance is None:
        _instance = TrustConfig(os.environ.get("TRUST_CLIENTS", ""))
    return _instance
