# 🔄 Unmarkd
[![codecov](https://codecov.io/gh/ThatXliner/unmarkd/branch/master/graph/badge.svg?token=PWVIERHTG3)](https://codecov.io/gh/ThatXliner/unmarkd)

> A markdown reverser.

---
Unmarkd is a [BeautifulSoup](https://github.com/ThatXliner/unmarkd/issues/4)-powered [Markdown](https://en.wikipedia.org/wiki/Markdown) reverser written in Python and for Python.

## Why

This is created as a [StackSearch](http://github.com/ThatXliner/stacksearch) (one of my other projects) dependancy. In order to create a better API, I needed a way to reverse HTML. So I created this.

There are [similar projects](https://github.com/xijo/reverse_markdown) (written in Ruby) but I have not found any written in Python (or for Python).

## Installation

You know the drill

```bash
pip install unmarkd
```

## Known issues

 - Nested lists are not properly indented ([#4](https://github.com/ThatXliner/unmarkd/issues/4))

## Documentation

Here's an example of basic usage

```python
import unmarkd
print(unmarkd.unmark("<b>I <i>love</i> markdown!</b>"))
# Output: **I *love* markdown!**
```

or something more complex (shamelessly taken from [here](https://markdowntohtml.com)):

```python
import unmarkd
html_doc = R"""<h1 id="sample-markdown">Sample Markdown</h1>
<p>This is some basic, sample markdown.</p>
<h2 id="second-heading">Second Heading</h2>
<ul>
<li>Unordered lists, and:<ol>
<li>One</li>
<li>Two</li>
<li>Three</li>
</ol>
</li>
<li>More</li>
</ul>
<blockquote>
<p>Blockquote</p>
</blockquote>
<p>And <strong>bold</strong>, <em>italics</em>, and even <em>italics and later <strong>bold</strong></em>. Even <del>strikethrough</del>. <a href="https://markdowntohtml.com">A link</a> to somewhere.</p>
<p>And code highlighting:</p>
<pre><code class="lang-js"><span class="hljs-keyword">var</span> foo = <span class="hljs-string">'bar'</span>;

<span class="hljs-function"><span class="hljs-keyword">function</span> <span class="hljs-title">baz</span><span class="hljs-params">(s)</span> </span>{
   <span class="hljs-keyword">return</span> foo + <span class="hljs-string">':'</span> + s;
}
</code></pre>
<p>Or inline code like <code>var foo = &#39;bar&#39;;</code>.</p>
<p>Or an image of bears</p>
<p><img src="http://placebear.com/200/200" alt="bears"></p>
<p>The end ...</p>
"""
print(unmarkd.unmark(html_doc))
```
and the output:

    # Sample Markdown


    This is some basic, sample markdown.

    ## Second Heading



    - Unordered lists, and:
     1. One
     2. Two
     3. Three
    - More

    >Blockquote


    And **bold**, *italics*, and even *italics and later **bold***. Even ~~strikethrough~~. [A link](https://markdowntohtml.com) to somewhere.

    And code highlighting:


    ```js
    var foo = 'bar';

    function baz(s) {
       return foo + ':' + s;
    }
    ```


    Or inline code like `var foo = 'bar';`.

    Or an image of bears

    ![bears](http://placebear.com/200/200)

    The end ...

### Extending

#### Brief Overview

Most functionality should be covered by the `BasicUnmarker` class defined in `unmarkd.unmarkers`.

If you need to reverse markdown from StackExchange (as in the case for my other project), you may use the `StackOverflowUnmarker` (or it's alias, `StackExchangeUnmarker`), which is also defined in `unmarkd.unmarkers`.

#### Customizing

If the above two classes do not suit your needs, you can subclass the `unmarkd.unmarkers.BaseUnmarker` abstract class.

Currently, you *must* define the following methods:

 - `detect_language` (parameters: **1**)
    - When a fenced code block is approached, this function is called with a parameter of type `bs4.BeautifulSoup` passed to it; this is the element the code block was detected from (i.e. `pre`).
    - This function is responsible for detecting the programming language (or returning `''` if none was detected) of the code block.


Currently, there are no methods you can *optionally* override.
