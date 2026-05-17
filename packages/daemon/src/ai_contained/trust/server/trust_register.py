"""trust_register endpoint — exchange public keys with the trust server."""

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from ai_contained.trust.server.trust_store import TrustStore, get_trust_store


def register(mcp: FastMCP, store: TrustStore | None = None) -> None:
    """Register the /trust/register endpoint with the MCP server."""
    store = store or get_trust_store()

    @mcp.custom_route("/trust/register", methods=["POST"])
    async def trust_register(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})
