import unmarkd


def test_comments():
    assert unmarkd.unmark("<!--Comment-->") == "<!--Comment-->"
