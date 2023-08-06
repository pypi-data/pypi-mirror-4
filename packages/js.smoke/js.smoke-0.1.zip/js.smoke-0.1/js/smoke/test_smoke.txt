How to use?
===========

You can import smoke_js from ``js.smoke`` and ``need`` it where you want
these resources to be included on a page::

  >>> from js.smoke import smoke_js
  >>> smoke_js.need()

You can optionally specify which theme you want to use, where the default
theme is included when you do not specify a theme::

  >>> from js.smoke import smoke_js, css, theme_100s, theme_dark, theme_tiger
  >>> smoke_js.need() # use default theme
  >>> smoke_js.need({css: theme_100s})
  >>> smoke_js.need({css: theme_dark})
  >>> smoke_js.need({css: theme_tiger})

.. _`fanstatic`: http://fanstatic.org
