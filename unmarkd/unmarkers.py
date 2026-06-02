"""Generate markdown from messy HTML."""

import abc
import contextlib
import html as lib_html
import textwrap
from typing import Callable, Dict, Set, Union

import bs4

SoupElement = Union[bs4.PageElement, bs4.BeautifulSoup]


class BaseUnmarker(abc.ABC):
    """To customize the behavior of your reverser, inherit from this abstract class."""

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
        "#",
    }
    TAG_ALIASES: Dict[str, str] = {}
    DEFAULT_TAG_ALIASES: Dict[str, str] = {"em": "i", "strong": "b", "s": "del"}
    UNORDERED_FORMAT: str = "\n- {next_item}"
    ORDERED_FORMAT: str = "\n{number_index}. {next_item}"
    #: Indentation for continuation paragraphs in the current list item; set by
    #: _render_list to match the marker width.
    _li_indent: str = "  "

    # def parse_css(self: "BaseUnmarker", css: str) -> Dict[str, str]:

    def _render_list(
        self: "BaseUnmarker",
        element: bs4.Tag,
        item_format: str,
        counter_initial_value: int = 1,
    ) -> str:
        """Render a list of items according to a format.

        Made to reduce code duplication.
        """
        # A "loose" list (blank lines between items) renders each <li>'s
        # content inside a <p>; mirror that by separating items with a blank
        # line so the markdown round-trips back to a loose list.
        if any(
            isinstance(li, bs4.Tag)
            and li.name == "li"
            and li.find("p", recursive=False)
            for li in element.children
        ):
            item_format = "\n" + item_format

        output = ""
        counter = counter_initial_value
        for child in element.children:
            if non_tag_output := self.parse_non_tags(child):
                if non_tag_output.strip() == "":
                    continue
                output += non_tag_output
                continue
            if not isinstance(child, bs4.Tag):
                # Empty/whitespace string between <li> elements; skip it.
                continue
            # Continuation paragraphs inside the item indent to the width of the
            # marker ("- " is 2, "10. " is 4), so they stay part of the item.
            marker = item_format.format(next_item="", number_index=counter).strip("\n")
            self._li_indent = " " * len(marker)
            output += item_format.format(
                next_item=self.tag_li(child).rstrip(),
                number_index=counter,
            )
            counter += 1
        return output.lstrip("\n")

    def escape(self: "BaseUnmarker", string: str) -> str:
        """Escape a string to be markdown-safe."""
        return "".join(map(self.__escape_character, string))

    def __escape_character(self: "BaseUnmarker", char: str) -> str:
        """Escape a single character."""
        assert len(char) == 1
        if char in self.ESCAPABLES:
            return "\\" + char
        return lib_html.escape(char)

    def wrap(self: "BaseUnmarker", element: SoupElement, around_with: str) -> str:
        """Wrap an element in a markdown-safe manner.

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

    def handle_tag(self: "BaseUnmarker", tag: bs4.Tag) -> str:
        name = (
            self.DEFAULT_TAG_ALIASES.get(tag.name)
            or self.TAG_ALIASES.get(tag.name)
            or tag.name
        )
        try:
            return self.resolve_handler_func(name)(tag)
        except AttributeError:
            return self.handle_default(tag)

    def resolve_handler_func(
        self: "BaseUnmarker",
        name: str,
    ) -> Callable[[bs4.Tag], str]:
        return getattr(self, "tag_" + name)  # type: ignore[no-any-return]

    #: Tags that introduce their own block; a bare newline beside one separates
    #: blocks (``\n\n``) rather than acting as an inline soft break (``\n``).
    BLOCK_TAGS: Set[str] = {
        "p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li",
        "blockquote", "pre", "hr", "table", "header", "footer", "section",
        "article",
    }

    def handle_string(self: "BaseUnmarker", string: str) -> str:
        if string == "\n":
            # A bare newline between inline elements is a CommonMark soft break
            # (stays in the same block); between block elements it separates them.
            return "\n"
        return self.escape(string) if self._should_escape else string

    def _is_block_boundary(self: "BaseUnmarker", node: bs4.PageElement) -> bool:
        for neighbor in (node.previous_sibling, node.next_sibling):
            if isinstance(neighbor, bs4.Tag) and neighbor.name in self.BLOCK_TAGS:
                return True
        return False

    def handle_doctype(self: "BaseUnmarker", _: bs4.Doctype) -> str:
        return ""

    def handle_cdata(self: "BaseUnmarker", _: bs4.CData) -> str:
        return ""

    def handle_declaration(self: "BaseUnmarker", _: bs4.Declaration) -> str:
        return ""

    def handle_processing_instruction(
        self: "BaseUnmarker",
        _: bs4.ProcessingInstruction,
    ) -> str:
        return ""

    def handle_comment(self: "BaseUnmarker", child: bs4.Comment) -> str:
        """Self explanatory."""
        # Should not cause any escaping problems since
        # BeautifulSoup escapes the string contents
        # See also https://www.crummy.com/software/BeautifulSoup/bs4/doc/#output-formatters
        return f"<!--{child}-->"

    def parse_non_tags(self: "BaseUnmarker", child: bs4.PageElement) -> str:
        # Function generated via ChatGPT
        def pascal_to_snake(pascal_string: str) -> str:
            snake_string = ""
            for i, char in enumerate(pascal_string):
                if i > 0 and char.isupper():
                    snake_string += "_"
                snake_string += char.lower()
            return snake_string

        if (
            issubclass(type(child), bs4.NavigableString)
            and type(child) is not bs4.NavigableString
        ):
            try:
                return getattr(  # type: ignore[no-any-return]
                    self,
                    f"handle_{pascal_to_snake(type(child).__name__)}",
                )(
                    child,
                )
            except AttributeError as error:
                msg = "This should never happen"
                raise AssertionError(msg, type(child)) from error
        if isinstance(child, (str, bs4.NavigableString)):
            if (
                child == "\n"
                and isinstance(child, bs4.NavigableString)
                and self._is_block_boundary(child)
            ):
                return "\n\n"
            return self.handle_string(child)
        return ""  # To indicate that it is a tag

    def __parse(
        self: "BaseUnmarker",
        html: SoupElement,
        escape: bool = False,
    ) -> str:
        """Parse an HTML element into valid markdown."""
        output = ""
        if html is None:
            return ""
        for child in html.children:  # type: ignore[union-attr]
            if isinstance(child, bs4.Tag):
                output += self.handle_tag(child)
            else:
                # Re-assert the escaping mode for every text node: a nested tag
                # (e.g. <code>, <a>) runs its own __parse and would otherwise
                # leave the flag flipped for the following siblings.
                self._should_escape = escape
                output += self.parse_non_tags(child)
        return output

    def handle_default(self: "BaseUnmarker", child: bs4.PageElement) -> str:
        """Whenever a tag isn't handled by one of these methods, this is called."""
        return str(child)

    # fmt: off
    def tag_h1(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return "# " + self.__parse(child, escape=True) + "\n"
    def tag_h2(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return "## " + self.__parse(child, escape=True) + "\n"
    def tag_h3(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return "### " + self.__parse(child, escape=True) + "\n"
    def tag_h4(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return "#### " + self.__parse(child, escape=True) + "\n"
    def tag_h5(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return "##### " + self.__parse(child, escape=True) + "\n"
    def tag_h6(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return "###### " + self.__parse(child, escape=True) + "\n"
    # fmt: on

    def tag_div(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return self.__parse(child)

    def tag_p(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return self.__parse(child, escape=True)

    def tag_del(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return self.wrap(child, around_with="~~")

    def tag_pre(self: "BaseUnmarker", child: bs4.Tag) -> str:
        assert child.code is not None
        return f"\n```{self.detect_language(child)}\n{child.code.get_text()}```\n"

    def tag_code(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return f"`{self.__parse(child)}`"

    def tag_hr(self: "BaseUnmarker", _: bs4.BeautifulSoup) -> str:
        return "\n---\n"

    def tag_td(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return self.__parse(child, escape=True)

    #: Tags that produce emphasis; nesting two of them with the same delimiter
    #: character (``***``) is ambiguous, so we alternate by depth.
    _EMPHASIS_TAGS = frozenset({"b", "strong", "i", "em"})

    def _emphasis_alternates(self: "BaseUnmarker", child: bs4.Tag) -> bool:
        """Report whether an emphasis tag should use the alternate delimiter.

        Same-character emphasis delimiters collapse when nested (``***`` is
        ambiguous), so we alternate ``*``/``_`` by emphasis nesting depth: every
        emphasis ancestor flips the delimiter, keeping each boundary distinct.
        """
        depth = 0
        parent = child.parent
        while parent is not None and parent.name in self._EMPHASIS_TAGS:
            depth += 1
            parent = parent.parent
        return depth % 2 == 1

    def tag_b(self: "BaseUnmarker", child: bs4.Tag) -> str:
        delim = "__" if self._emphasis_alternates(child) else "**"
        return self.wrap(child, around_with=delim)

    def tag_i(self: "BaseUnmarker", child: bs4.Tag) -> str:
        delim = "_" if self._emphasis_alternates(child) else "*"
        return self.wrap(child, around_with=delim)

    @staticmethod
    def _format_title(title: str) -> str:
        r"""Quote a link/image title for CommonMark: ` "title"`.

        Only the quote char and backslash need escaping; using repr() here
        would mangle non-ASCII characters (e.g. ``\xa0``) into escape codes.
        """
        return ' "' + title.replace("\\", "\\\\").replace('"', '\\"') + '"'

    def tag_a(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return (
            f"[{self.__parse(child)}]({child['href']}"
            + (
                self._format_title(child["title"])  # type: ignore[arg-type]
                if child.get("title")
                else ""
            )
            + ")"
        )

    def tag_img(self: "BaseUnmarker", img: bs4.Tag) -> str:
        img_text = ""
        if (parent := img.parent) is not None and (
            figcaption := parent.find("figcaption")
        ) is not None:
            img_text = figcaption.get_text()
        return f"![{img.get('alt') or img_text}]({img['src']})"

    def tag_ul(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return self._render_list(child, self.UNORDERED_FORMAT)

    def tag_ol(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return self._render_list(
            child,
            self.ORDERED_FORMAT,
            counter_initial_value=int(child.get("start", 1)),  # type: ignore[arg-type]
        )

    def tag_li(self: "BaseUnmarker", child: bs4.Tag) -> str:
        output = ""
        for element in child.children:
            # Direct text in a list item must be escaped like paragraph text, so
            # a literal "#"/">"/"-" at the start doesn't turn into a heading,
            # blockquote, or nested bullet on the round trip.
            self._should_escape = True
            non_tag_output = self.parse_non_tags(element)
            if non_tag_output:
                if non_tag_output.strip() == "":
                    # Whitespace between inline elements is significant; collapse
                    # it to a single space. But whitespace next to a nested list
                    # is just HTML indentation — the list supplies its own break.
                    sibling = element.next_sibling
                    if not (
                        isinstance(sibling, bs4.Tag) and sibling.name in ("ol", "ul")
                    ):
                        output += " "
                else:
                    output += non_tag_output
                continue
            if not isinstance(element, bs4.Tag):
                continue
            if element.name in ("ol", "ul"):
                # A nested list must start on its own line, indented under the
                # parent item.
                output = output.rstrip() + "\n" + textwrap.indent(
                    self.handle_tag(element),
                    "    ",
                )
            elif element.name == "p" and output.strip():
                # A loose item holds multiple <p> blocks. The first becomes the
                # item text; later ones are continuation paragraphs, separated by
                # a blank line and indented to line up under the marker (set by
                # _render_list, e.g. "  " for "- ", "    " for "10. ").
                output = (
                    output.rstrip()
                    + "\n\n"
                    + textwrap.indent(self.handle_tag(element), self._li_indent)
                )
            elif element.name == "pre":
                # A fenced code block inside an item must be indented to the
                # marker width, or it dedents and breaks out of the list.
                block = textwrap.indent(
                    self.handle_tag(element).strip("\n"),
                    self._li_indent,
                )
                output = (
                    (output.rstrip() + "\n\n" + block) if output.strip() else block
                )
            else:
                output += self.handle_tag(element)
        return output.strip()

    def tag_br(self: "BaseUnmarker", br: bs4.Tag) -> str:
        # A <br /> is a hard line break within a block, not a paragraph break.
        # The backslash form collides when the preceding text ends in a
        # backslash, so fall back to the two-space form in that case.
        previous = br.previous_sibling
        prefix = "\\"
        if isinstance(previous, bs4.NavigableString) and str(previous).endswith("\\"):
            prefix = "  "
        sibling = br.next_sibling
        if isinstance(sibling, bs4.NavigableString) and str(sibling).startswith("\n"):
            return prefix
        return prefix + "\n"

    def tag_blockquote(self: "BaseUnmarker", child: bs4.Tag) -> str:
        # Every line of quoted content needs its own "> " marker, and the text
        # is escaped so a literal block starter inside the quote doesn't reparse
        # as a new block once the markers are stripped.
        inner = self.__parse(child, escape=True).strip()
        quoted = "\n".join(
            f"> {line}" if line else ">" for line in inner.split("\n")
        )
        return quoted + "\n"

    def tag_q(self: "BaseUnmarker", child: bs4.Tag) -> str:
        return self.wrap(child, around_with='"')

    def unmark(self: "BaseUnmarker", html: Union[str, bs4.BeautifulSoup]) -> str:
        """Convert HTML into markdown."""
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
        self: "BaseUnmarker",
        html: bs4.Tag,
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
        classes = html.get("class") or html.code.get("class") if html.code else None
        if not classes:
            return ""
        return classes[0] or ""


class StackOverflowUnmarker(BaseUnmarker):
    """A specialized unmarker for HTML found on StackOverflow."""

    def detect_language(self: "BaseUnmarker", html: bs4.Tag) -> str:
        assert html.code is not None
        classes = html.get("class") or html.code.get("class")
        if classes is None:
            return ""
        assert isinstance(classes, list)
        for item in (
            "default",
            "s-code-block",
            "hljs",
            "snippet-code-js",
            "prettyprint-override",
        ):
            with contextlib.suppress(ValueError):
                classes.remove(item)

        if len(classes) == 0:
            return ""
        output = classes[0]
        if output.startswith("lang-"):
            return output[5:]
        if output.startswith("snippet-code-"):
            return output[13:]
        return output


StackExchangeUnmarker = StackOverflowUnmarker


class BasicUnmarker(BaseUnmarker):
    """The basic, generic unmarker."""

    def detect_language(self: "BaseUnmarker", html: bs4.Tag) -> str:
        classes = html.get("class") or (html.code.get("class") if html.code else None)
        if classes is None:
            return ""
        classes = classes[:]  # Copy it
        assert len(classes) == 1
        lang = classes[0]
        if lang.startswith("lang-"):
            return lang[5:]
        if lang.startswith("language-"):
            return lang[9:]
        return lang
