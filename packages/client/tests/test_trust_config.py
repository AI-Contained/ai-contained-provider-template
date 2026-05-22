import httpx
import pytest
from assertpy import assert_that
from starlette.testclient import TestClient

from ai_contained.trust import client as trust_client
from ai_contained.trust.client.trust_connection import TrustConnection


def describe_TrustConfig() -> None:
    def describe_parse() -> None:
        def it_returns_empty_for_empty_string() -> None:
            assert_that(trust_client.TrustConfig._parse("")).is_empty()

        def it_maps_bare_url_to_wildcard() -> None:
            assert_that(trust_client.TrustConfig._parse("http://server:8080")).is_equal_to(
                {"*": "http://server:8080"}
            )

        def it_maps_role_to_url() -> None:
            assert_that(trust_client.TrustConfig._parse("aws=http://aws:8080")).is_equal_to(
                {"aws": "http://aws:8080"}
            )

        def it_maps_multiple_roles() -> None:
            assert_that(trust_client.TrustConfig._parse("aws=http://aws:8080,github=http://github:8080")).is_equal_to(
                {"aws": "http://aws:8080", "github": "http://github:8080"}
            )

        def it_maps_empty_url_to_none() -> None:
            assert_that(trust_client.TrustConfig._parse("aws=")).is_equal_to({"aws": None})

        def it_combines_wildcard_and_role_override() -> None:
            assert_that(trust_client.TrustConfig._parse("http://server:8080,aws=http://aws:8080")).is_equal_to(
                {"*": "http://server:8080", "aws": "http://aws:8080"}
            )

        def it_combines_wildcard_with_deny() -> None:
            assert_that(trust_client.TrustConfig._parse("http://server:8080,aws=")).is_equal_to(
                {"*": "http://server:8080", "aws": None}
            )

        def it_raises_on_duplicate_role() -> None:
            assert_that(trust_client.TrustConfig._parse).raises(trust_client.DuplicateSourceError).when_called_with(
                "aws=http://foo.com:8080,aws=http://bar.com:8080"
            )

        def it_raises_on_duplicate_wildcard() -> None:
            assert_that(trust_client.TrustConfig._parse).raises(trust_client.DuplicateSourceError).when_called_with(
                "http://foo.com:8080,http://foo.com:8081"
            )

    def describe_get_client() -> None:
        @pytest.mark.skip(reason="conftest always initializes the singleton via init_trust_config — true uninitialized state cannot be tested in this suite")
        def it_is_uninitialized_by_default() -> None:
            assert_that(trust_client.get_trust_config()).is_none()

        def it_allows_known_role_and_denies_unknown(http: TestClient) -> None:
            trust_client.init_trust_config("aws=http://127.0.0.1:8080", lambda url: http)
            assert_that(trust_client.get_trust_config().get_client("github")).is_none()
            assert_that(trust_client.get_trust_config().get_client("aws")).is_instance_of(trust_client.TrustClient)

        def it_allows_any_role_via_wildcard(http: TestClient) -> None:
            trust_client.init_trust_config("http://127.0.0.1:8080", lambda url: http)
            assert_that(trust_client.get_trust_config().get_client("github")).is_instance_of(trust_client.TrustClient)
            assert_that(trust_client.get_trust_config().get_client("aws")).is_instance_of(trust_client.TrustClient)

        def it_denies_role_even_with_wildcard(http: TestClient) -> None:
            trust_client.init_trust_config("http://127.0.0.1:8080,aws=", lambda url: http)
            assert_that(trust_client.get_trust_config().get_client("github")).is_instance_of(trust_client.TrustClient)
            assert_that(trust_client.get_trust_config().get_client("aws")).is_none()

        def it_shares_connection_across_roles_on_same_host(http: TestClient) -> None:
            trust_client.init_trust_config("aws=http://127.0.0.1:8080,shell=http://127.0.0.1:8080", lambda url: http)
            config = trust_client.get_trust_config()
            assert_that(config.get_client("aws")._connection).is_same_as(config.get_client("shell")._connection)
