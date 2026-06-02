"""Round-trip regression tests for block/inline structure.

Each case is a CommonMark construct that previously failed to round-trip
(``marko.convert(md) != marko.convert(unmark(marko.convert(md)))``) or crashed.
Found via grammar-aware fuzzing; locked in here so they never regress.
"""
import marko

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


class TestLinkTitles:
    """Titles with non-ASCII used to be mangled by ``repr()``."""

    def test_nbsp_in_title(self) -> None:
        helper("[x](https://x.com 'a\xa0b')")

    def test_quote_in_title(self) -> None:
        helper("""[x](https://x.com 'has "quote"')""")

    def test_plain_title(self) -> None:
        helper("[x](https://x.com 'title')")
