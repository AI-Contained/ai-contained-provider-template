from assertpy import assert_that

from ai_contained.trust.server.trust_config import RoleSet, TrustConfig


def describe_RoleSet() -> None:
    def describe_permits() -> None:
        def it_allows_only_listed_roles() -> None:
            result = RoleSet(frozenset({"shell"}), frozenset())
            assert_that(result.permits("shell")).is_true()
            assert_that(result.permits("aws")).is_false()

        def it_denies_a_role_that_is_explicitly_blocked() -> None:
            result = RoleSet(frozenset({"shell", "aws"}), frozenset({"shell"}))
            assert_that(result.permits("shell")).is_false()
            assert_that(result.permits("aws")).is_true()

        def it_allows_any_role_when_wildcard_is_set() -> None:
            result = RoleSet(frozenset({"*"}), frozenset({"shell"}))
            assert_that(result.permits("shell")).is_false()
            assert_that(result.permits("aws")).is_true()
