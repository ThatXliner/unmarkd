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


def bold(thing: str) -> str:
    return f"<b>{thing}</b>"


def italic(thing: str) -> str:
    return f"<i>{thing}</i>"


def test_italic_and_bold() -> None:
    helper(
        (italic(bold("Italic and bold")), bold(italic("Italic and bold"))),
        "***Italic and bold***",
    )
