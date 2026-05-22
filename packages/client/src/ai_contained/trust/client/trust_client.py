"""TrustClient — role-aware secret fetcher backed by a TrustConnection."""

import json
from dataclasses import dataclass

from ai_contained.trust.client.trust_connection import TrustConnection


@dataclass
class TrustClient:
    """Tool-facing client for a single role. Wraps a shared TrustConnection with a baked-in path."""

    _connection: TrustConnection
    _path: str

    async def post_raw(self, payload: dict) -> bytes:
        return await self._connection.post_raw(self._path, payload)

    async def post(self, payload: dict) -> dict:
        return json.loads(await self.post_raw(payload))
