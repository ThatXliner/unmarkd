import unmarkd


def test_comments() -> None:
    assert unmarkd.unmark("<!--Comment-->") == "<!--Comment-->"
