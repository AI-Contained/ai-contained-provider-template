import pytest
from assertpy import assert_that
from starlette.testclient import TestClient

from ai_contained.trust.client import TrustClient


@pytest.fixture
def trust_client(http: TestClient) -> TrustClient:
    return TrustClient(http)  # TestClient is a subclass of httpx.Client


def describe_POST_trust_register() -> None:
    def it_is_accessible(http: TestClient) -> None:
        response = http.post("/trust/register", json={})
        assert_that(response.status_code).is_equal_to(200)

    def it_returns_server_encryption_public_key(trust_client: TrustClient) -> None:
        server_public_key = trust_client.register()
        assert_that(server_public_key).is_not_none()
        assert_that(server_public_key).is_length(64)  # 32-byte Curve25519 key as hex

    def it_allows_re_registration_with_same_key(trust_client: TrustClient) -> None:
        trust_client.register()
        trust_client.register()  # same keypair — should update record, not raise

    def it_rejects_missing_signing_key(http: TestClient) -> None:
        response = http.post("/trust/register", json={"encryption_public_key": "ab" * 32})
        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.json()["code"]).is_equal_to("INVALID_KEY")

    def it_rejects_missing_encryption_key(http: TestClient) -> None:
        response = http.post("/trust/register", json={"signing_public_key": "ab" * 32})
        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.json()["code"]).is_equal_to("INVALID_KEY")

    def it_rejects_malformed_key_format(http: TestClient) -> None:
        response = http.post(
            "/trust/register",
            json={"signing_public_key": "not-hex", "encryption_public_key": "not-hex"},
        )
        assert_that(response.status_code).is_equal_to(400)
        assert_that(response.json()["code"]).is_equal_to("INVALID_KEY")
