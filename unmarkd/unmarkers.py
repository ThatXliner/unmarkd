#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate markdown from messy HTML"""

import abc
from typing import Union

import bs4


class BaseUnmarker(abc.ABC):

    ESCAPING_DICT = {"*": R"\*", "`": R"\`", "\\": "\\\\", "~": R"\~"}
    UNORDERED_FORMAT = "\n - {next_item}"
    ORDERED_FORMAT = "\n {number_index}. {next_item}"

    def __render_list(
        self,
        element: bs4.BeautifulSoup,
        item_format: str,
        counter_initial_value: int = 1,
    ) -> str:
        output = ""
        counter = counter_initial_value
        for item in (e for e in element if str(e).strip()):
            if item.name != "li":  # Or else it'd be invalid
                continue
            assert item.name == "li"
            output += item_format.format(
                next_item=self.__parse(item), number_index=counter
            )
            counter += 1
        return output

    def escape(self, string: str) -> str:
        """Escape a string to be markdown-safe"""
        return "".join(map(self.__escape_character, string))

    def __escape_character(self, char: str) -> str:
        assert len(char) == 1
        return self.ESCAPING_DICT.get(char, char)

    def __parse(self, html: bs4.BeautifulSoup, escape: bool = False) -> str:
        # TODO: Modularize
        def wrap(element: bs4.BeautifulSoup, around_with: str) -> str:
            return around_with + self.__parse(element, escape=True) + around_with

        output = ""
        if html is None:
            return ""
        for child in html.children:
            if type(child) in (str, bs4.NavigableString):
                if child == "\n":
                    output += "\n\n"
                else:
                    output += self.escape(child) if escape else child
            elif child.name == "div":  # Other text
                for item in child.children:
                    output += self.__parse(item)
            elif child.name == "p":  # Normal text
                output += self.__parse(child, escape=True)
            elif child.name == "del":
                output += wrap(child, around_with="~~")
            elif child.name == "pre":  # Code blocks
                output += (
                    f"\n```{self.detect_language(child)}\n{child.code.get_text()}```\n"
                )
            elif child.name == "code":  # Inline Code
                output += f"`{self.__parse(child, escape=False)}`"
            elif child.name == "hr":  # One of those line thingies
                output += "\n---\n"
            elif child.name.startswith("h"):  # Headers
                output += "#" * int(child.name[1:]) + " " + self.__parse(child) + "\n"
            elif child.name in {"b", "strong"}:  # Bold
                output += wrap(child, around_with="**")
            elif child.name in {"i", "em"}:  # Italics
                output += wrap(child, around_with="*")
            elif child.name == "a":  # Link
                output += (
                    f"[{self.__parse(child)}]({child['href']}"
                    + (
                        " " + repr(self.escape(child["title"]))
                        if child.get("title")
                        else ""
                    )
                    + ")"
                )
            elif child.name == "img":  # Images
                try:
                    tag = child.contents[0]
                except IndexError:
                    tag = child
                try:
                    tag_text = child.contents[-1]
                except IndexError:
                    next_sib = tag.next_sibling
                    tag_text = (
                        next_sib.extract().strip()
                        if next_sib
                        else tag.get_text().strip()
                    )
                output += f"![{tag.get('alt') or tag_text}]({tag['src']})"
            elif child.name == "ul":  # Bullet list
                output += self.__render_list(child, self.UNORDERED_FORMAT)
            elif child.name == "ol":  # Number list
                output += self.__render_list(
                    child,
                    self.ORDERED_FORMAT,
                    counter_initial_value=int(child.get("start", 1)),
                )
            elif child.name == "br":
                output += "\n\n"
            elif child.name == "blockquote":
                output += (
                    (">" * (len(child("blockquote")) or 1))
                    + self.__parse(child).strip()
                    + "\n"
                )
            else:  # Other HTML tags that weren't mentioned here
                output += str(child)
        return output

    def unmark(self, html: Union[str, bs4.NavigableString, bs4.BeautifulSoup]) -> str:
        """The main reverser method. Use this to convert HTML into markdown"""
        if not type(html) == bs4.BeautifulSoup:
            html = bs4.BeautifulSoup(html, "html.parser")
        return self.__parse(html).strip()

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
            return ""
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
        elif lang.startswith("language-"):
            lang = lang[9:]
        return lang
