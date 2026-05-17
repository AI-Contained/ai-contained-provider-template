"""trust_register endpoint — exchange public keys with the trust server."""

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse


def register(mcp: FastMCP) -> None:
    """Register the /trust/register endpoint with the MCP server."""

    @mcp.custom_route("/trust/register", methods=["POST"])
    async def trust_register(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ok"})
