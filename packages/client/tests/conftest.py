import pytest
from fastmcp import FastMCP
from starlette.testclient import TestClient

from ai_contained.trust.server import register


@pytest.fixture
def mcp() -> FastMCP:
    server = FastMCP("test")
    register(server)
    return server


@pytest.fixture
def http(mcp: FastMCP) -> TestClient:
    return TestClient(mcp.http_app())
