#!/usr/bin/env python
# -*- coding: utf-8 -*-
from typing import Callable, Iterable

import unmarkd


def helper(
    possiblities: Iterable[str],
    should_be: str,
    for_functions: Iterable[Callable[[str], str]] = (
        unmarkd.unmark,  # type: ignore
        unmarkd.unmarkers.StackOverflowUnmarker().unmark,  # type: ignore
    ),
) -> None:
    for func in for_functions:
        for possibility in possiblities:
            assert func(possibility) == should_be


# TODO: Use hypothesis
def test_italic() -> None:
    helper(("<i>Italic</i>", "<em>Italic</em>"), should_be="*Italic*")


def test_bold() -> None:
    helper(("<b>Bold</b>", "<strong>Bold</strong>"), should_be="**Bold**")
