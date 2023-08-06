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
"""ReStructured Text Renderer Classes
"""
__docformat__ = 'restructuredtext'

import docutils.core

from zope.component import adapts
from zope.interface import implementer
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces.browser import IBrowserRequest

from zope.renderer.i18n import ZopeMessageFactory as _
from zope.renderer.interfaces import ISource, IHTMLRenderer
from zope.renderer import SourceFactory


class IReStructuredTextSource(ISource):
    """Marker interface for a restructured text source. Note that an
    implementation of this interface should always derive from unicode or
    behave like a unicode class."""


ReStructuredTextSourceFactory = SourceFactory(
    IReStructuredTextSource, _("ReStructured Text (ReST)"),
    _("ReStructured Text (ReST) Source"))

@implementer(IHTMLRenderer)
class ReStructuredTextToHTMLRenderer(BrowserView):
    r"""An Adapter to convert from Restructured Text to HTML.

    Examples::

      >>> from zope.publisher.browser import TestRequest
      >>> source = ReStructuredTextSourceFactory(u'''
      ... This is source.
      ...
      ... Header 3
      ... --------
      ... This is more source.
      ... ''')
      >>> renderer = ReStructuredTextToHTMLRenderer(source, TestRequest())
      >>> print(renderer.render().strip())
      <p>This is source.</p>
      <div class="section" id="header-3">
      <h3>Header 3</h3>
      <p>This is more source.</p>
      </div>
    """
    adapts(IReStructuredTextSource, IBrowserRequest)

    def render(self, settings_overrides={}):
        """See zope.app.interfaces.renderer.IHTMLRenderer

        Let's make sure that inputted unicode stays as unicode:

        >>> renderer = ReStructuredTextToHTMLRenderer(u'b\xc3h', None)
        >>> renderer.render() == u'<p>b\\xc3h</p>\\n'
        True

        >>> text = u'''
        ... =========
        ... Heading 1
        ... =========
        ...
        ... hello world
        ...
        ... Heading 2
        ... ========='''
        >>> overrides = {'initial_header_level': 2,
        ...              'doctitle_xform': 0 }
        >>> renderer = ReStructuredTextToHTMLRenderer(text, None)
        >>> print(renderer.render(overrides))
        <div class="section" id="heading-1">
        <h2>Heading 1</h2>
        <p>hello world</p>
        <div class="section" id="heading-2">
        <h3>Heading 2</h3>
        </div>
        </div>
        <BLANKLINE>
        """
        # default settings for the renderer
        overrides = {
            'halt_level': 6,
            'input_encoding': 'unicode',
            'output_encoding': 'unicode',
            'initial_header_level': 3,
            }
        overrides.update(settings_overrides)
        parts = docutils.core.publish_parts(
            self.context,
            writer_name='html',
            settings_overrides=overrides,
            )
        return u''.join(
            (parts['body_pre_docinfo'], parts['docinfo'], parts['body']))
