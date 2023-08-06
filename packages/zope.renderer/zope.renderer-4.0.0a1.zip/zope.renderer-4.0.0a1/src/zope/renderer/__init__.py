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
from zope.component.interfaces import IFactory
from zope.interface import implementer, directlyProvides, Declaration
from zope.renderer._compat import unicode

class Source(unicode):
    __provides__ = None


@implementer(IFactory)
class SourceFactory(object):
    """Creates an ISource object."""

    def __init__(self, iface, title='', description=''):
        self._iface = iface
        self.title = title
        self.description = description

    def getInterfaces(self):
        return Declaration(self._iface).flattened()

    def __call__(self, ustr):
        source = Source(ustr)
        directlyProvides(source, self._iface)
        return source
