import markdown_it
from hypothesis import assume, example, given
from hypothesis import strategies as st

import unmarkd


def helper(text: str) -> None:
    md = markdown_it.MarkdownIt()
    value0 = md.render(text)
    unmarked = unmarkd.unmark(html=value0)
    value1 = md.render(unmarked)
    assert value0 == value1, (value0, value1, unmarked)


@given(text=st.text())
#@example(
#    """<ul>
#<li>tb
#<ol>
#<li>i1</li>
#<li>i2</li>
#<li>i3</li>
#</ol>
#</li>
#<li>bb</li>
#</ul>"""
#)
def test_roundtrip_commonmark_unmark(text):
    assume(text.strip() == text)
    helper(text)


class TestExampleCases:
    def test_example_1(self):  helper("")
    def test_example_2(self):  helper("` `")
    def test_example_3(self):  helper(text="0\n\n0")
    def test_example_4(self):  helper(text="```\n```")
    def test_example_5(self):  helper(text="0.")
    def test_example_6(self):  helper(text="```")
    def test_example_7(self):  helper(text=R"*\**")
    def test_example_8(self):  helper(text=R"**\***")
    def test_example_9(self):  helper(text=R"`\``")
    def test_example_10(self): helper(text=R"-")
    def test_example_11(self): helper(text=R">")
    def test_example_12(self): helper(text=R"<")
    def test_example_13(self): helper("*foo `bar* baz`")
