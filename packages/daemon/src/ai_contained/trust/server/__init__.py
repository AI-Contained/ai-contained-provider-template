"""Trust server daemon."""

from fastmcp import FastMCP

from ai_contained.trust.server.trust_register import register as _register_trust_register
from ai_contained.trust.server.trust_store import TrustStore


def register(mcp: FastMCP, store: TrustStore | None = None) -> None:
    """Register all trust server endpoints with the MCP server."""
    _register_trust_register(mcp, store)
