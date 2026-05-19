import json

import pytest
from assertpy import assert_that
from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.testclient import TestClient

import test_trust_client as _self
from ai_contained.trust.client import TrustClient
from ai_contained.trust.server import register
from ai_contained.trust.server.secret_route import secret_route


# Delegate for secret_endpoint - monkeypatched per test to control the response.
async def secret_handler(request: Request) -> Response:
    raise NotImplementedError


@pytest.fixture
def mcp() -> FastMCP:
    server = FastMCP("test")
    register(server)

    @secret_route(server, "/test/secret", methods=["POST"])
    async def secret_endpoint(request: Request) -> Response:
        return await secret_handler(request)

    return server


def describe_TrustClient() -> None:
    @pytest.fixture
    def trust_client(http: TestClient) -> TrustClient:
        return TrustClient(http)  # TestClient is a subclass of httpx.Client

    def describe_register() -> None:
        def it_returns_true_on_success(trust_client: TrustClient) -> None:
            assert_that(trust_client.register()).is_true()

        def it_returns_false_when_already_registered(trust_client: TrustClient) -> None:
            assert_that(trust_client.register()).is_true()
            assert_that(trust_client.register()).is_false()

    def describe_post() -> None:
        expected = {"value": "supersecret"}

        @pytest.fixture
        def trust_client(http: TestClient, monkeypatch: pytest.MonkeyPatch) -> TrustClient:
            async def _handler(request: Request) -> Response:
                return JSONResponse(expected)

            monkeypatch.setattr(_self, "secret_handler", _handler)
            client = TrustClient(http)
            client.register()
            return client

        def it_post_raw_returns_decrypted_bytes(trust_client: TrustClient) -> None:
            result = trust_client.post_raw("/test/secret", {})
            assert_that(result).is_equal_to(json.dumps(expected).encode())

        def it_post_returns_decrypted_json(trust_client: TrustClient) -> None:
            result = trust_client.post("/test/secret", {})
            assert_that(result).is_equal_to(expected)
