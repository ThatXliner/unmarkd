# This test code was written by the `hypothesis.extra.ghostwriter` module
# and is provided under the Creative Commons Zero public domain dedication.

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
    value1 = commonmark.main.commonmark(unmarkd.unmark(html=value0))
    assert value0 == value1, (value0, value1)
