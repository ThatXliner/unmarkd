import commonmark.main
from hypothesis import assume, given, example
from hypothesis import strategies as st

import unmarkd


@given(text=st.text())
@example("")
@example("` `")
@example("0\n\n0")
@example("```\n```")
@example("```")
def test_roundtrip_commonmark_unmark(text):
    assume(text.strip() == text)
    value0 = commonmark.main.commonmark(text=text)
    unmarked = unmarkd.unmark(html=value0)
    value1 = commonmark.main.commonmark(unmarked)
    assert value0 == value1, (value0, value1, unmarked)
