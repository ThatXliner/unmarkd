# 🔄 Unmarkd
A markdown reverser.

## Why

This is created as a [StackSearch](http://github.com/ThatXliner/stacksearch) (one of my other projects) dependancy.

In order to create a better API, I needed a way to reverse HTML. So I created this.

## Installation

You know the drill

```bash
pip install unmarkd
```

## Documentation

Here's an example of basic usage

```python
import unmarkd
print(unmarkd.unmark("<b>I <i>love</i> markdown!</b>"))
# Output: **I *love* markdown!**
```

or something more complex:

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


     * Unordered lists, and:
     1. One
     2. Two
     3. Three
     * One
     * Two
     * Three
     * More
    > Blockquote

    And **bold**, *italics*, and even *italics and later bold*. Even ~~strikethrough~~. [A link](https://markdowntohtml.com) to somewhere.
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
    The end...

## Extending

TK.
