##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.table import interfaces

@zope.interface.implementer(interfaces.IValues)
class ValuesMixin(object):
    """Mixin for different value adapters."""

    def __init__(self, context, request, table):
        self.context = context
        self.request = request
        self.table = table


@zope.component.adapter(zope.interface.Interface, IBrowserRequest,
                        interfaces.ITable)
class ValuesForContainer(ValuesMixin):
    """Values from a simple IContainer."""

    @property
    def values(self):
        return self.context.values()


@zope.component.adapter(zope.interface.Interface, IBrowserRequest,
                        interfaces.ISequenceTable)
class ValuesForSequence(ValuesMixin):
    """Values from a simple IContainer."""

    @property
    def values(self):
        return self.context
