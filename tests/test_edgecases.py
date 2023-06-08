import unmarkd


class TestComments:
    def test_bare(self) -> None:
        assert unmarkd.unmark("<!--Comment-->") == "<!--Comment-->"

    def test_list(self) -> None:
        assert (
            unmarkd.unmark("<ol><!--e--><li><!--Comment-->Hi</li></ol>")
            == "<!--e==>\n1. <!--Comment-->Hi"
        )
