from bs4 import BeautifulSoup
import unmarkd


class TestComments:
    def test_bare(self) -> None:
        assert unmarkd.unmark("<!--Comment-->") == "<!--Comment-->"

    def test_list(self) -> None:
        assert (
            unmarkd.unmark("<!--e-->\n<ol><li><!--Comment-->Hi</li></ol>")
            == "<!--e-->\n\n1. <!--Comment-->Hi"
        )
        assert (
            unmarkd.unmark("<ol><!--e-->\n<li><!--Comment-->Hi</li></ol>")
            == "<!--e-->\n1. <!--Comment-->Hi"
        ), unmarkd.unmark("<ol><!--e-->\n<li><!--Comment-->Hi</li></ol>")


def test_empty_html() -> None:
    assert unmarkd.unmark(BeautifulSoup("")) == ""


def test_custom_elements() -> None:
    assert (
        unmarkd.unmark("<custom-element></custom-element>")
        == "<custom-element></custom-element>"
    )


def test_header_tag() -> None:
    assert unmarkd.unmark("<header>yo</header>") == "<header>yo</header>"
