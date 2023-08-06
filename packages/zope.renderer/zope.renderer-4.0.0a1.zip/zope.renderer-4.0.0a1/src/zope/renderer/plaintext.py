##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Plain Text Renderer Classes
"""
__docformat__ = 'restructuredtext'

import cgi

from zope.component import adapts
from zope.interface import implementer
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.renderer.i18n import ZopeMessageFactory as _
from zope.renderer.interfaces import ISource, IHTMLRenderer
from zope.renderer import SourceFactory

class IPlainTextSource(ISource):
    """Marker interface for a plain text source. Note that an implementation
    of this interface should always derive from unicode or behave like a
    unicode class."""

PlainTextSourceFactory = SourceFactory(
    IPlainTextSource, _("Plain Text"), _("Plain Text Source"))


@implementer(IHTMLRenderer)
class PlainTextToHTMLRenderer(BrowserView):
    r"""A view to convert from Plain Text to HTML.

    Example::

      >>> from zope.publisher.browser import TestRequest
      >>> source = PlainTextSourceFactory(u'I hear that 1 > 2.\n')
      >>> renderer = PlainTextToHTMLRenderer(source, TestRequest())
      >>> renderer.render()
      u'I hear that 1 &gt; 2.<br />\n'
    """
    adapts(IPlainTextSource, IBrowserRequest)

    def render(self):
        "See zope.app.interfaces.renderer.IHTMLRenderer"
        return cgi.escape(self.context).replace('\n', '<br />\n')
