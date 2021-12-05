import pytest


# we want to have pytest assert introspection in the helpers, otherwise we get "AssertionError"
# without knowing what went wrong
pytest.register_assert_rewrite('test.base')
