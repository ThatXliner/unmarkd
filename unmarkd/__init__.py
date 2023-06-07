"""A markdown reverser."""
from typing import Union

import bs4

from . import unmarkers


def unmark(html: Union[str, bs4.NavigableString, bs4.BeautifulSoup]) -> str:
    """Convert HTML to markdown."""
    return unmarkers.BasicUnmarker().unmark(html)


__version__ = "1.0.0"
