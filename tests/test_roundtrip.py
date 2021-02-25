import commonmark.main
from hypothesis import assume, given, example
from hypothesis import strategies as st

import unmarkd


@given(
    text=st.text(),
)
@example("")
def test_roundtrip_commonmark_unmark(text):
    assume(text.strip() == text)
    value0 = commonmark.main.commonmark(text=text)
    reversed = unmarkd.unmark(html=value0)
    value1 = commonmark.main.commonmark(reversed)
    assert value0 == value1, (value0, value1, reversed)
