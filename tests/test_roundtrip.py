import commonmark.main
import unmarkd
from hypothesis import assume, example, given
from hypothesis import strategies as st


@given(text=st.text())
@example("")
@example("` `")
@example("0\n\n0")
@example("```\n```")
@example("```")
@example(R"*\**")
@example(R"`\``")
def test_roundtrip_commonmark_unmark(text):
    assume(text.strip() == text)
    value0 = commonmark.main.commonmark(text=text)
    unmarked = unmarkd.unmark(html=value0)
    value1 = commonmark.main.commonmark(unmarked)
    assert value0 == value1, (value0, value1, unmarked)
