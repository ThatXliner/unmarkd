"""Round-trip regression tests for block/inline structure.

Each case is a CommonMark construct that previously failed to round-trip
(``marko.convert(md) != marko.convert(unmark(marko.convert(md)))``) or crashed.
Found via grammar-aware fuzzing; locked in here so they never regress.
"""
import marko
import pytest

import unmarkd


def helper(text: str) -> None:
    value0 = marko.convert(text)
    unmarked = unmarkd.unmark(html=value0)
    value1 = marko.convert(unmarked)
    assert value0 == value1, (value0, value1, unmarked)


class TestListItemInlines:
    """`<li>` mixing inline tags with bare text used to crash or drop the list."""

    def test_strong_then_text(self) -> None:
        helper("- **b** c")

    def test_text_then_strong(self) -> None:
        helper("- a **b**")

    def test_em_and_text(self) -> None:
        helper("- *i* x")

    def test_strike_and_text(self) -> None:
        helper("- ~~s~~ y")

    def test_ordered_strong_then_text(self) -> None:
        helper("1. **b** c")

    def test_inline_spacing_preserved(self) -> None:
        helper("- [a](https://x.co) **b** c")

    def test_link_image_spacing(self) -> None:
        helper("- a [b](https://x.co) ![c](https://x.co)")

    def test_adjacent_strongs(self) -> None:
        helper("- **a** **b**")


class TestLooseLists:
    """Blank-line-separated items render loose (``<li><p>``) and must stay loose."""

    def test_loose_ul(self) -> None:
        helper("- a\n\n- b")

    def test_loose_ol(self) -> None:
        helper("1. a\n\n2. b")

    def test_loose_ul_three(self) -> None:
        helper("- a\n\n- b\n\n- c")

    def test_tight_ul_unchanged(self) -> None:
        helper("- a\n- b")


class TestListItemBlocks:
    """Block children of a list item (code fences, blockquotes) must indent to
    the marker width so they stay inside the item."""

    def test_code_fence_in_item(self) -> None:
        helper("- ```\n  code\n  ```")

    def test_code_fence_in_ordered_item(self) -> None:
        helper("1. ```\n   code\n   ```")

    def test_paragraph_then_code_fence(self) -> None:
        helper("- text\n\n  ```\n  code\n  ```")

    def test_two_digit_ordinal_code_fence(self) -> None:
        helper("10. ```\n    code\n    ```")

    def test_blockquote_in_item(self) -> None:
        helper("- > q")


class TestNestedLists:
    def test_nested_ul(self) -> None:
        helper("- a\n  - nested")

    def test_nested_ul_two_items(self) -> None:
        helper("- a\n  - b\n  - c")

    def test_nested_ol(self) -> None:
        helper("1. a\n   1. b")

    def test_deep_nesting(self) -> None:
        helper("- top\n  - mid\n    - deep")


class TestSoftBreaks:
    """A bare newline between inline content is a soft break, not a paragraph
    break. Block-level newlines must still separate blocks."""

    def test_soft_break_between_tags(self) -> None:
        helper("**a**\n**b**")

    def test_soft_break_in_blockquote(self) -> None:
        helper("> **a**\n> **b**")

    def test_multiline_blockquote(self) -> None:
        helper("> a\n> b")

    def test_two_paragraphs_stay_separate(self) -> None:
        helper("a\n\nb")

    def test_three_paragraphs_stay_separate(self) -> None:
        helper("p1\n\np2\n\np3")

    def test_paragraph_heading_paragraph(self) -> None:
        helper("a\n\n# h\n\nb")


class TestHardBreaks:
    """A ``<br />`` is a hard line break within a block, not a paragraph break."""

    def test_hard_break(self) -> None:
        helper("a  \nb")

    def test_hard_break_twice(self) -> None:
        helper("a  \nb  \nc")

    def test_hard_break_after_emphasis(self) -> None:
        helper("*x*  \ny")

    def test_hard_break_after_strong(self) -> None:
        helper("**x**  \ny")

    def test_hard_break_after_literal_backslash(self) -> None:
        helper("a\\\\  \nb")

    def test_hard_break_after_link_and_backslash(self) -> None:
        helper("[a](http://x.co) \\\\  \nb")


class TestMultiParagraphItems:
    """A loose item may hold several paragraphs; later ones are indented
    continuation paragraphs."""

    def test_two_paragraph_item(self) -> None:
        helper("- a\n\n  b")

    def test_three_paragraph_item(self) -> None:
        helper("- a\n\n  b\n\n  c")

    def test_ordered_two_paragraph_item(self) -> None:
        helper("1. a\n\n   b")

    def test_multi_paragraph_item_with_link(self) -> None:
        helper("- a\n\n  [l](https://x.com 't')")

    def test_two_digit_ordinal_continuation(self) -> None:
        # "10. " is four columns wide; the continuation must indent to match or
        # it escapes the list.
        helper("10. a\n\n    b")

    def test_long_list_with_trailing_continuation(self) -> None:
        items = "\n".join(f"{i}. x{i}" for i in range(1, 12))
        helper(items + "\n\n    cont")


class TestNestedEmphasis:
    """``***`` is ambiguous; nested emphasis must alternate delimiters so the
    strong/em order survives the round trip."""

    def test_strong_over_em(self) -> None:
        helper("**_x_**")

    def test_em_over_strong(self) -> None:
        helper("_**x**_")

    def test_triple(self) -> None:
        helper("***x***")

    def test_em_inside_strong_with_text(self) -> None:
        helper("**a _b_ c**")

    def test_strong_inside_em_with_text(self) -> None:
        helper("*a **b** c*")

    def test_three_levels_deep(self) -> None:
        helper("**_*x*_**")


class TestListItemEscaping:
    """A literal block-starter character at the start of a list item must stay
    escaped, or it reparses as a heading/blockquote/nested bullet."""

    def test_escaped_hash(self) -> None:
        helper(r"- \# x")

    def test_escaped_gt(self) -> None:
        helper(r"- \> x")

    def test_escaped_dash(self) -> None:
        helper(r"- \- x")

    def test_escaped_star_midtext(self) -> None:
        helper(r"- a \* b")

    def test_literal_hash_unescaped(self) -> None:
        helper("- # x")


class TestHeadingEscaping:
    """Heading text is escaped so a literal backtick/special doesn't pair with
    a later delimiter and corrupt the round trip."""

    def test_escaped_backtick(self) -> None:
        helper(r"# \` x")

    def test_escaped_hash(self) -> None:
        helper(r"# \# x")

    def test_escaped_bracket(self) -> None:
        helper(r"## \[ x")

    def test_heading_with_emphasis(self) -> None:
        helper("# **bold**")

    def test_literal_special_after_code_span(self) -> None:
        # The <code> child must not leave the escaping flag flipped for the
        # following literal backtick.
        helper(r"# `a` \` `b`")

    def test_literal_star_after_strong(self) -> None:
        helper(r"# **b** \* c")


class TestBlockquotePrefix:
    """Every line of a multi-line blockquote keeps its marker; quoted content
    is escaped so it does not leak out as a sibling block."""

    def test_multiline_plain(self) -> None:
        helper("> a\n> b\n> c")

    def test_multiline_with_emphasis(self) -> None:
        helper("> a\n> **b**")

    def test_escaped_hash_in_quote(self) -> None:
        helper(r"> \# x")

    def test_nested_markers(self) -> None:
        helper(">>")

    def test_triple_nested_markers(self) -> None:
        helper(">>>")


class TestLinkTitles:
    """Titles with non-ASCII used to be mangled by ``repr()``."""

    def test_nbsp_in_title(self) -> None:
        helper("[x](https://x.com 'a\xa0b')")

    def test_quote_in_title(self) -> None:
        helper("""[x](https://x.com 'has "quote"')""")

    def test_plain_title(self) -> None:
        helper("[x](https://x.com 'title')")


class TestKnownLimitations:
    """Cases that cannot round-trip because BeautifulSoup's ``html.parser``
    discards information before unmarkd ever sees the tree."""

    @pytest.mark.xfail(
        reason="html.parser collapses runs of whitespace inside <code>, so a "
        "code span of only spaces loses its length before unmarkd runs.",
        strict=True,
    )
    def test_whitespace_only_code_span(self) -> None:
        helper("`  `")
