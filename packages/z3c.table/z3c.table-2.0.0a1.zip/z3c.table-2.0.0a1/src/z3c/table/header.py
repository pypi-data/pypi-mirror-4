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
$Id$
"""
__docformat__ = "reStructuredText"


from z3c.table.i18n import _
try:
    # Python 2
    from urllib import urlencode
except ImportError:
    # Python 3
    from urllib.parse import urlencode
import z3c.table.interfaces
import zope.i18n
import zope.interface


@zope.interface.implementer(z3c.table.interfaces.IColumnHeader)
class ColumnHeader(object):
    """ColumnHeader renderer provider"""
    _request_args = []

    def __init__(self, context, request, table, column):
        self.__parent__ = context
        self.context = context
        self.request = request
        self.table = table
        self.column = column

    def update(self):
        """Override this method in subclasses if required"""
        pass

    def render(self):
        """Override this method in subclasses"""
        return self.column.header

    def getQueryStringArgs(self):
        """
        Collect additional terms from the request and include in sorting column
        headers

        Perhaps this should be in separate interface only for sorting headers?

        """
        args = {}
        for key in self._request_args:
            value = self.request.get(key, None)
            if value:
                args.update({key: value})
        return args


class SortingColumnHeader(ColumnHeader):
    """Sorting column header."""

    def render(self):
        table = self.table
        prefix = table.prefix
        colID = self.column.id

        # this may return a string 'id-name-idx' if coming from request,
        # otherwise in Table class it is intialised as a integer string
        currentSortID = table.getSortOn()
        try:
            currentSortID = int(currentSortID)
        except ValueError:
            currentSortID = currentSortID.rsplit('-', 1)[-1]

        currentSortOrder = table.getSortOrder()

        sortID = colID.rsplit('-', 1)[-1]

        sortOrder = table.sortOrder
        if int(sortID) == int(currentSortID):
            # ordering the same column so we want to reverse the order
            if currentSortOrder in table.reverseSortOrderNames:
                sortOrder = 'ascending'
            elif currentSortOrder == 'ascending':
                sortOrder = table.reverseSortOrderNames[0]

        args = self.getQueryStringArgs()
        args.update({'%s-sortOn' % prefix: colID,
                     '%s-sortOrder' % prefix: sortOrder})
        queryString = '?%s' % (urlencode(sorted(args.items())))

        return '<a href="%s" title="%s">%s</a>' % (
            queryString,
            zope.i18n.translate(_('Sort'), context=self.request),
            zope.i18n.translate(self.column.header, context=self.request))
