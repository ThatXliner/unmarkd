"""A markdown reverser."""
from typing import Union

import bs4  # type: ignore

from . import unmarkers


def unmark(html: Union[str, bs4.NavigableString, bs4.BeautifulSoup]) -> str:  # type: ignore
    """Convert HTML to markdown"""
    return unmarkers.BasicUnmarker().unmark(html)  # type: ignore


__version__ = "0.1.2"
