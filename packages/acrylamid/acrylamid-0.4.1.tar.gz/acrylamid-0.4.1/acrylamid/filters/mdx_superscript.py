# -*- encoding: utf-8 -*-
#
# Copyright (c) 2010, Shane Graber
#
# Superscipt extension for Markdown.
#
# To superscript something, place a carat symbol, '^', before and after the
# text that you would like in superscript: 6.02 x 10^23^
# The '23' in this example will be superscripted. See below.
#
# Examples:
#
# >>> import markdown
# >>> md = markdown.Markdown(extensions=['superscript'])
# >>> md.convert('This is a reference to a footnote^1^.')
# u'<p>This is a reference to a footnote<sup>1</sup>.</p>'
#
# >>> md.convert('This is scientific notation: 6.02 x 10^23^')
# u'<p>This is scientific notation: 6.02 x 10<sup>23</sup></p>'
#
# >>> md.convert('This is scientific notation: 6.02 x 10^23. Note lack of second carat.')
# u'<p>This is scientific notation: 6.02 x 10^23. Note lack of second carat.</p>'
#
# >>> md.convert('Scientific notation: 6.02 x 10^23. Add carat at end of sentence.^')
# u'<p>Scientific notation: 6.02 x 10<sup>23. Add a carat at the end of sentence.</sup>.</p>'
#
# Paragraph breaks will nullify superscripts across paragraphs. Line breaks
# within paragraphs will not.
#
# Modified to not superscript "HEAD^1. Also for HEAD^2".
#
# useful CSS rules:  sup, sub {
#                        vertical-align: baseline;
#                        position: relative;
#                        top: -0.4em;
#                    }
#                    sub { top: 0.4em; }

import markdown

match = ['superscript', 'sup']


class SuperscriptPattern(markdown.inlinepatterns.Pattern):
    """Return a superscript Element (`word^2^`)."""

    def handleMatch(self, m):

        text = m.group(3)

        if markdown.version_info < (2, 1, 0):
            el = markdown.etree.Element("sup")
            el.text = markdown.AtomicString(text)
        else:
            el = markdown.util.etree.Element("sup")
            el.text = markdown.util.AtomicString(text)

        return el


class SuperscriptExtension(markdown.Extension):
    """Superscript Extension for Python-Markdown."""

    def extendMarkdown(self, md, md_globals):
        """Replace superscript with SuperscriptPattern"""
        md.inlinePatterns['superscript'] = SuperscriptPattern(r'(\^)([^\s\^]+)\2', md)


def makeExtension(configs=None):
    return SuperscriptExtension(configs=configs)
