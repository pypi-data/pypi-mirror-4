# -*- coding:utf-8 -*-

"""
Only bbcode is supported so far.
"""

from .constants import MARKUP_BBCODE, MARKUP_MARKDOWN, MARKUP_TEXTILE
from .constants import MARKUP_RST, MARKUP_HTML

import textile
import markdown
import postmarkup
from docutils.core import publish_parts

import html5lib
from html5lib import sanitizer

html_sanitizer = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)

def render_markup(markup, text):
    if text is None:
        return None

    if markup == MARKUP_BBCODE:
        return postmarkup.render_bbcode(text)
    elif markup == MARKUP_MARKDOWN:
        return markdown.markdown(text)
    elif markup == MARKUP_TEXTILE:
        return textile.textile(text)
    elif markup == MARKUP_RST:
        return publish_parts(text, writer_name='html')['fragment']
    elif markup == MARKUP_HTML:
        return html_sanitizer.parse(text)
    return text