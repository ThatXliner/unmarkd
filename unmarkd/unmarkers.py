#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate markdown from messy HTML"""

import abc
from typing import Optional, Union

import bs4


class BaseUnmarker(abc.ABC):
    def __parse(self, child: bs4.BeautifulSoup) -> str:
        # TODO: Modularize
        def wrap(element: bs4.BeautifulSoup, around_with: str) -> str:
            return around_with + self.unmark(element) + around_with

        if type(child) in (str, bs4.NavigableString):
            return child
        elif child.name == "div":  # Other text
            for item in child.children:
                return self.unmark(item)
        elif child.name == "p":  # Normal text
            return self.unmark(child)
        elif child.name == "del":
            return wrap(child, around_with="~~")
        elif child.name == "pre":  # Code blocks
            return f"\n```{self.detect_language(child)}\n{child.code.get_text()}\n```\n"
        elif child.name == "code":  # Inline Code
            return f"`{self.unmark(child)}`"
        elif child.name == "hr":  # One of those line thingies
            return "\n---\n"
        elif child.name.startswith("h"):  # Headers
            return "\n" + "#" * int(child.name[1:]) + " " + self.unmark(child) + "\n"
        elif child.name in {"b", "strong"}:  # Bold
            return wrap(child, around_with="**")
        elif child.name in {"i", "em"}:  # Italics
            return wrap(child, around_with="*")
        elif child.name == "a":  # Link
            return f"[{self.unmark(child)}]({child['href']})"
        elif child.name == "img":  # Images
            return f"![{child.get('alt')}]({child['src']})"
        elif child.name == "ul":  # Bullet list
            output = ""
            for item in child("li"):
                output += f"\n * {self.unmark(item)}"
            return output
        elif child.name == "ol":  # Number list
            output = ""
            for index, item in enumerate(child("li")):
                output += f"\n {index + 1}. {self.unmark(item)}"
            return output
        elif child.name == "br":
            return "\n\n"
        elif child.name == "blockquote":
            return "> " + self.unmark(child.p) + "\n"

        else:  # Other HTML tags that weren't mentioned here
            return str(child)
        return output

    def unmark(self, html: Union[str, bs4.NavigableString, bs4.BeautifulSoup]) -> str:
        """The main reverser method. Use this to convert HTML into markdown"""
        if type(html) is str:
            html = bs4.BeautifulSoup(html, features="html.parser")
        output = ""
        for child in html.children:
            output += self.__parse(child)

        return output.strip()

    @abc.abstractmethod  # Language detecting compatibilities may vary
    def detect_language(self, html: bs4.BeautifulSoup) -> str:
        """From a block of HTML, detect the language. Usually from CSS classes

        Parameters
        ----------
        html : bs4.BeautifulSoup
            The block of HTML to parse from `html`.

        Returns
        -------
        str
            The found language. If no language if found, return "".

        """


class StackOverflowUnmarker(BaseUnmarker):
    """A specialized unmarker for HTML found on StackOverflow"""

    def detect_language(self, html: bs4.BeautifulSoup) -> str:
        classes = html.get("class") or html.code.get("class")
        if classes is None:
            return None
        classes = classes[:]  # Copy it
        for item in (
            "default",
            "s-code-block",
            "hljs",
            "lang-sh",
            "snippet-code-js",
            "prettyprint-override",
        ):
            try:
                classes.remove(item)
            except ValueError:
                pass
        if len(classes) == 0:
            return ""
        output = classes[-1]
        if output.startswith("lang-"):
            output = output[5:]
        if output.startswith("snippet-code-"):
            output = output[13:]
        return output


StackExchangeUnmarker = StackOverflowUnmarker


class BasicUnmarker(BaseUnmarker):
    """The basic, generic unmarker"""

    def detect_language(self, html: bs4.BeautifulSoup) -> str:
        classes = html.get("class") or html.code.get("class")
        if classes is None:
            return ""
        classes = classes[:]  # Copy it
        assert len(classes) == 1
        lang = classes[-1]
        if lang.startswith("lang-"):
            lang = lang[5:]
        return lang
