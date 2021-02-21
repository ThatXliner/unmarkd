"""A markdown reverser."""
from . import unmarkers


def unmark(html: str) -> str:
    """Convert HTML to markdown"""
    return unmarkers.BasicUnmarker().unmark(html)


__version__ = "0.1.0"
