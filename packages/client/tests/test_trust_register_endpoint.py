from assertpy import assert_that
from starlette.testclient import TestClient


def describe_POST_trust_register() -> None:
    def it_is_accessible(http: TestClient) -> None:
        response = http.post("/trust/register", json={})
        assert_that(response.status_code).is_not_equal_to(404)
        assert_that(response.status_code).is_less_than(500)
