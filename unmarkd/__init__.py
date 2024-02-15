"""A markdown reverser."""

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    import bs4

from . import unmarkers


def unmark(html: Union[str, "bs4.NavigableString", "bs4.BeautifulSoup"]) -> str:
    """Convert HTML to markdown."""
    return unmarkers.BasicUnmarker().unmark(html)


__version__ = "1.1.2"
