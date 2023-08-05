======
README
======

wrapText
--------

Text wrapper which knows how to wrap text but don't break words.

  >>> from p01.util.text import wrapText
  >>> txt = 'Here comes some text with some words.'

We use 'xxx' as postfix since '...' has another function in doctests.

  >>> postfix = ' xxx'
  >>> wrapText(txt, 10, postfix)
  'Here xxx'

Let's show how it will keep the text still below the given legnth:

  >>> wrapText(txt, 23, postfix)
  'Here comes some xxx'

  >>> wrapText(txt, 24, postfix)
  'Here comes some text xxx'

  >>> wrapText(txt, 25, postfix)
  'Here comes some text xxx'

  >>> wrapText(txt, 26, postfix)
  'Here comes some text xxx'

  >>> wrapText(txt, 27, postfix)
  'Here comes some text xxx'

  >>> wrapText(txt, 28, postfix)
  'Here comes some text xxx'

As you can see, if there is space for more words it will get used:

  >>> wrapText(txt, 29, postfix)
  'Here comes some text with xxx'

We can also allow to wrap words:

  >>> wrapText(txt, 27, postfix, True)
  'Here comes some text with s xxx'

Let's skip the empty space in front of the prefix. Note we still use 'xxx'
since '...' is reserved for internal use in doc tests.

  >>> wrapText(txt, 28, 'xxx', True)
  'Here comes some text with soxxx'

Not that we only append a postfix if the lenght of the result is shorter then
the given text:

  >>> wrapText('no', 10, 'xxx', True)
  'no'


wrapHTML
--------

Same as wrapText but first strips HTML tags out of given text:

  >>> from p01.util.text import wrapHTML

Note: we use 'xxx' as postfix since '...' has another function in doctests.

  >>> postfix = ' xxx'
  >>> html = '<html><body>some <!-- comment -->&nbsp;content</body></html>'

  >>> wrapHTML(html, 999, postfix)
  'some content'

  >>> bad = '<html><br>&nbsp;some <!--comment -->&nbsp;&nbsp;content</body></html>'
  >>> wrapHTML(bad, 999, postfix)
  'some content'

  >>> wrapHTML(html, 7, postfix)
  ''

  >>> wrapHTML(html, 7, postfix, True)
  'some co xxx'

  >>> wrapHTML(html, 5, postfix, True)
  'some xxx'

  >>> wrapHTML(html, 4, postfix, True)
  'some xxx'
