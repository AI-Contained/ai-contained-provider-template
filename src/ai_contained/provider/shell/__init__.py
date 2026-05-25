"""Shell provider."""

from fastmcp import FastMCP

from ai_contained.provider.shell.read_bash import register as _register_read_bash
from ai_contained.provider.shell.write_command import register as _register_write_command


async def register(mcp: FastMCP) -> None:
    """Register all shell provider tools with the MCP server."""
    await _register_read_bash(mcp)
    await _register_write_command(mcp)
