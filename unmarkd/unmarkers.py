#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate markdown from messy HTML"""

import abc
from typing import Optional, Union

import bs4


class BaseUnmarker(abc.ABC):
    def unmark(self, html: Union[str, bs4.NavigableString, bs4.BeautifulSoup]) -> str:
        """The main reverser method. Use this to convert HTML into markdown"""
        if type(html) is str:
            html = bs4.BeautifulSoup(html, features="html.parser")
        # TODO: Modularize
        if type(html) in (str, bs4.NavigableString):
            return html
        output = ""

        def wrap(element: bs4.BeautifulSoup, around_with: str) -> str:
            output = ""
            output += around_with
            for item in element.children:
                assert item is not None, "This should never happen"
                output += self.unmark(item)
            output += around_with
            return output

        for child in html.children:
            if isinstance(child, bs4.NavigableString):  # Strings
                output += child
            elif child.name == "div":  # Other text
                for item in child.children:
                    output += self.unmark(item)
            elif child.name == "p":  # Normal text
                output += self.unmark(child)
            elif child.name == "del":
                output += wrap(child, around_with="~~")
            elif child.name == "pre":  # Code blocks
                output += f"\n```{self.detect_language(html)}\n"
                output += html.code.get_text()
                output += "\n```\n"
            elif child.name == "code":  # Inline Code
                output += f"`{self.unmark(child)}`"
            elif child.name == "hr":  # One of those line thingies
                output += "\n---\n"
            elif child.name.startswith("h"):  # Headers
                output += (
                    "\n" + "#" * int(child.name[1:]) + " " + self.unmark(child) + "\n"
                )
            elif child.name in {"b", "strong"}:  # Bold
                output += wrap(child, around_with="**")
            elif child.name in {"i", "em"}:  # Italics
                output += wrap(child, around_with="*")
            elif child.name == "a":  # Link
                output += f"[{self.unmark(child)}]({child['href']})"
            elif child.name == "img":  # Images
                output += f"![{child.get('alt')}]({child['src']})"
            elif child.name == "ul":  # Bullet list
                for item in child("li"):
                    output += f"\n * {self.unmark(item)}"
            elif child.name == "ol":  # Number list
                for index, item in enumerate(child("li")):
                    output += f"\n {index + 1}. {self.unmark(item)}"
            elif child.name == "br":
                output += "\n\n"
            elif child.name == "blockquote":
                output += "> " + self.unmark(child.p) + "\n"

            else:  # Other HTML tags that weren't mentioned here
                output += str(child)

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
