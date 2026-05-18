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
    # TestClient defaults client to ("testclient", 50000) which is not a valid IP — override so
    # request.client.host parses as an IPAddress and one-registration-per-IP enforcement works.
    return TestClient(mcp.http_app(), client=("127.0.0.1", 50000))
