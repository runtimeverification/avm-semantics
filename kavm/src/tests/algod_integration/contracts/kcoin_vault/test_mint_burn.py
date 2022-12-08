from datetime import timedelta
from typing import Any

from hypothesis import Phase, given, settings
from hypothesis import strategies as st

MIN_ARG_VALUE = 10
MAX_ARG_VALUE = 1 * 10**6
TEST_CASE_DEADLINE = timedelta(seconds=5)
N_TESTS = 25


@settings(deadline=TEST_CASE_DEADLINE, max_examples=N_TESTS, phases=[Phase.generate])
@given(
    microalgos=st.integers(min_value=MIN_ARG_VALUE, max_value=MAX_ARG_VALUE),
)
def test_mint_burn(initial_state_fixture: Any, microalgos: int) -> None:
    client, user_addr, user_private_key = initial_state_fixture
    minted = client.call_mint(user_addr, user_private_key, microalgos)
    got_back = client.call_burn(user_addr, user_private_key, minted)
    assert abs(got_back - microalgos) <= 1
