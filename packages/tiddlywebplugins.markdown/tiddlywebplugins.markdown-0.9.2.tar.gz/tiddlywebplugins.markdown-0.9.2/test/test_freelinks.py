import pytest
from tiddlywebplugins.markdown import render
from tiddlyweb.model.tiddler import Tiddler


def test_simple_freelinks():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[Foo]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '<a href="Foo">' in output
    assert '>Foo</a>' in output
    assert '[[Foo]]' not in output
    assert output == '<p>lorem <a href="Foo">Foo</a> ipsum</p>\n'

    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[Foo [] Bar]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[Foo [] Bar]]' not in output
    assert '<a href="Foo [] Bar">Foo [] Bar</a>' in output
    assert output == '<p>lorem <a href="Foo [] Bar">Foo [] Bar</a> ipsum</p>\n'


def test_labeled_freelinks():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[hello world|Foo]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '<a href="Foo">' in output
    assert '>hello world</a>' in output
    assert '[[hello world|Foo]]' not in output
    assert output == '<p>lorem <a href="Foo">hello world</a> ipsum</p>\n'

    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[hello [] world|Foo]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[hello [] world|Foo]]' not in output
    assert '<a href="Foo">hello [] world</a>' in output
    assert output == '<p>lorem <a href="Foo">hello [] world</a> ipsum</p>\n'


def test_precedence():
    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[hello FooBar world]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[hello FooBar world]]' not in output
    assert '<a href="FooBar">FooBar</a>' not in output
    assert '<a href="hello FooBar world">hello FooBar world</a>' in output
    assert output == '<p>lorem <a href="hello FooBar world">hello FooBar world</a> ipsum</p>\n'

    tiddler = Tiddler('Foo')
    tiddler.text = 'lorem [[...|hello FooBar world]] ipsum'

    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    output = render(tiddler, environ)

    assert '[[...|hello FooBar world]]' not in output
    assert '<a href="FooBar">FooBar</a>' not in output
    assert '<a href="hello FooBar world">...</a>' in output
    assert output == '<p>lorem <a href="hello FooBar world">...</a> ipsum</p>\n'

@pytest.mark.xfail
def test_precedence_in_markdown_link():
    tiddler = Tiddler('Foo')
    environ = { 'tiddlyweb.config': { 'markdown.wiki_link_base': '' } }
    tiddler.text = 'I see [foo LoremIpsum bar](http://example.org) you'
    output = render(tiddler, environ)
    assert output == '<p>I see <a href="http://example.org">foo LoremIpsum bar</a>you</p>'

