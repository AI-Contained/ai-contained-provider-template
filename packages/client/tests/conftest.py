import pytest
from fastmcp import FastMCP
from starlette.testclient import TestClient

from ai_contained.trust.server import register
from ai_contained.trust.server.trust_store import TrustStore


@pytest.fixture
def mcp() -> FastMCP:
    server = FastMCP("test")
    register(server, TrustStore())
    return server


@pytest.fixture
def http(mcp: FastMCP) -> TestClient:
    return TestClient(mcp.http_app())
