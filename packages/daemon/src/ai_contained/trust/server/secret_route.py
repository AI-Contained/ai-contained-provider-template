from collections.abc import Callable, Coroutine

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import Response

from ai_contained.trust.server.trust_store import get_trust_store

Handler = Callable[[Request], Coroutine[None, None, Response]]


def secret_route(
    mcp: FastMCP,
    path: str,
    methods: list[str],
) -> Callable[[Handler], Handler]:
    def decorator(fn: Handler) -> Handler:
        @mcp.custom_route(path, methods=methods)
        async def handler(request: Request) -> Response:
            store = get_trust_store()
            # 1. Look up client in store by IP — 401 if unregistered
            # 2. Parse Authorization: Signature keyId="Ed25519",signature="<hex>"
            # 3. Verify Ed25519 signature over request body — 401 if invalid
            # 4. Call fn(request)
            # 5. Encrypt response body if 200 (or X-Trust-Secret: encrypt), unless X-Trust-Secret: plaintext
            # 6. Strip X-Trust-Secret header before returning
            return await fn(request)

        return handler

    return decorator
