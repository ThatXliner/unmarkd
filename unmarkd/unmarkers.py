#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate markdown from messy HTML"""

import abc
import html as lib_html
import re
import textwrap
from typing import Callable, Dict, Set, Union

import bs4


class BaseUnmarker(abc.ABC):
    ESCAPABLES: Set[str] = {
        "*",
        "`",
        "\\",
        "~",
        "_",
        "-",
        "[",
        "]",
        ">",
        # "(",
        # ")",
    }
    TAG_ALIASES: Dict[str, str] = {}
    DEFAULT_TAG_ALIASES: Dict[str, str] = {"em": "i", "strong": "b", "s": "del"}
    UNORDERED_FORMAT: str = "\n- {next_item}"
    ORDERED_FORMAT: str = "\n {number_index}. {next_item}"

    # def parse_css(self, css: str) -> Dict[str, str]:
    #     return {k: v for style in css.split(";") for k, v in style.split(":", 1)}

    def _render_list(
        self,
        element: bs4.BeautifulSoup,
        item_format: str,
        counter_initial_value: int = 1,
    ) -> str:
        """Render a list of items according to a format.

        Made to reduce code duplication.
        """
        output = ""
        for counter, item in enumerate(
            element(True, recursive=False), counter_initial_value
        ):
            output += (
                item_format.strip().format(
                    next_item=self.tag_li(item).rstrip(), number_index=counter
                )
                + "\n"
            )
        return output

    def escape(self, string: str) -> str:
        """Escape a string to be markdown-safe"""
        return "".join(map(self.__escape_character, string))

    def __escape_character(self, char: str) -> str:
        """Escape a single character"""
        assert len(char) == 1
        if char in self.ESCAPABLES:
            return "\\" + char
        return lib_html.escape(char)

    def wrap(self, element: bs4.BeautifulSoup, around_with: str) -> str:
        """Wrap an element in a markdown-safe manner

        Parameters
        ----------
        element : bs4.BeautifulSoup
            The element to wrap.
        around_with : str
            What to wrap `element` around with.

        Notes
        -----
            `around_with` will not be escaped.

        Returns
        -------
        str
            The wrapped version of the element.

        """
        return around_with + self.__parse(element, escape=True) + around_with

    def resolve_handler_func(self, name: str) -> Callable[[bs4.BeautifulSoup], str]:
        return getattr(self, "tag_" + name)

    def __parse(self, html: bs4.BeautifulSoup, escape: bool = False) -> str:
        """Parse an HTML element into valid markdown."""
        output = ""
        if html is None:
            return ""
        for child in html.children:
            if type(child) in (str, bs4.NavigableString):
                if child == "\n":
                    output += "\n\n"
                else:
                    output += self.escape(child) if escape else child
            elif type(child) is bs4.element.Doctype:
                continue
            else:
                name: str = child.name
                # To reduce code duplication
                name = (
                    self.DEFAULT_TAG_ALIASES.get(name)
                    or self.TAG_ALIASES.get(name)
                    or name
                )

                try:
                    output += self.resolve_handler_func(name)(child)
                except AttributeError:
                    if name.startswith("h"):  # XXX: Maybe H1, up to H6, is enough?
                        output += "#" * int(name[1:]) + " " + self.__parse(child) + "\n"
                        continue
                    output += self.handle_default(child)
        return output

    def handle_default(self, child: bs4.BeautifulSoup) -> str:
        """Whenever a tag isn't handled by one of these methods, this is called"""
        return str(child)

    def tag_div(self, child: bs4.BeautifulSoup) -> str:
        return self.__parse(child)

    def tag_p(self, child: bs4.BeautifulSoup) -> str:
        return self.__parse(child, escape=True)

    def tag_del(self, child: bs4.BeautifulSoup) -> str:
        return self.wrap(child, around_with="~~")

    def tag_pre(self, child: bs4.BeautifulSoup) -> str:
        return f"\n```{self.detect_language(child)}\n{child.code.get_text()}```\n"

    def tag_code(self, child: bs4.BeautifulSoup) -> str:
        return f"`{self.__parse(child)}`"

    def tag_hr(self, _: bs4.BeautifulSoup) -> str:
        return "\n---\n"

    def tag_td(self, child: bs4.BeautifulSoup) -> str:
        return self.__parse(child, escape=True)

    def tag_b(self, child: bs4.BeautifulSoup) -> str:
        return self.wrap(child, around_with="**")

    def tag_i(self, child: bs4.BeautifulSoup) -> str:
        return self.wrap(child, around_with="*")

    def tag_a(self, child: bs4.BeautifulSoup) -> str:
        return (
            f"[{self.__parse(child)}]({child['href']}"
            + (" " + repr(self.escape(child["title"])) if child.get("title") else "")
            + ")"
        )

    def tag_img(self, child: bs4.BeautifulSoup) -> str:
        try:
            tag = child.contents[0]
        except IndexError:
            tag = child
        try:
            tag_text = child.contents[-1]
        except IndexError:
            next_sib = tag.next_sibling
            tag_text = (
                next_sib.extract().strip() if next_sib else tag.get_text().strip()
            )
        return f"![{tag.get('alt') or tag_text}]({tag['src']})"

    def tag_ul(self, child: bs4.BeautifulSoup) -> str:
        return self._render_list(child, self.UNORDERED_FORMAT)

    def tag_ol(self, child: bs4.BeautifulSoup) -> str:
        return self._render_list(
            child,
            self.ORDERED_FORMAT,
            counter_initial_value=int(child.get("start", 1)),
        )

    def tag_li(self, child: bs4.BeautifulSoup) -> str:
        output = ""
        for elstr in child.children:
            if str(elstr) == elstr:
                output += str(elstr).rstrip(" ")
            else:
                output += textwrap.indent(
                    self.resolve_handler_func(elstr.name)(elstr), "    "
                )
        return output

    def tag_br(self, _: bs4.BeautifulSoup) -> str:
        return "\n\n"

    def tag_blockquote(self, child: bs4.BeautifulSoup) -> str:
        return ">" + self.__parse(child).strip() + "\n"

    def tag_q(self, child: bs4.BeautifulSoup) -> str:
        return self.wrap(child, around_with='"')

    def unmark(self, html: Union[str, bs4.BeautifulSoup]) -> str:
        """The main reverser method. Use this to convert HTML into markdown"""
        if type(html) != bs4.BeautifulSoup:
            assert isinstance(html, str)
            html = bs4.BeautifulSoup(html, "html.parser")
        assert isinstance(html, bs4.BeautifulSoup)
        if html.html is not None:  # Testing if not using "html.parser"
            html.html.unwrap()  # Maintaining lxml and html5lib compatibility
            if html.head is not None:  # html5lib compatibility... for the future
                html.head.decompose()
            if html.body is not None:  # lxml compatibility
                html.body.unwrap()
        return self.__parse(html).strip().replace("\u0000", "\uFFFD")

    def detect_language(
        self, html: bs4.BeautifulSoup
    ) -> str:  # XXX: Replace with info string
        """From a block of HTML, detect the language from the class attribute.

        Warning
        -------
        The default is very dumb and will return the first class.

        Parameters
        ----------
        html : bs4.BeautifulSoup
            The block of HTML to parse from `html`.

        Returns
        -------
        str
            The found language. If no language if found, return "".

        """
        classes = html.get("class") or html.code.get("class")
        return classes[0] or ""


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
            "snippet-code-js",
            "prettyprint-override",
        ):
            try:
                classes.remove(item)
            except ValueError:
                pass
        if len(classes) == 0:
            return ""
        output = classes[0]
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
        lang = classes[0]
        if lang.startswith("lang-"):
            lang = lang[5:]
        elif lang.startswith("language-"):
            lang = lang[9:]
        return lang
