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

import datetime
import zope.interface
import zope.component
import zope.traversing.testing
from zope.container import btree, ordered
from zope.dublincore.interfaces import IZopeDublinCore
from zope.security import checker
from zope.site.testing import siteSetUp, siteTearDown

from z3c.table import column, table
import z3c.table.value


class TitleColumn(column.Column):

    weight = 10
    header = u'Title'

    def renderCell(self, item):
        return u'Title: %s' % item.title


class NumberColumn(column.Column):

    header = u'Number'
    weight = 20

    def getSortKey(self, item):
        return item.number

    def renderCell(self, item):
        return 'number: %s' % item.number


class Container(btree.BTreeContainer):
    """Sample container."""
    __name__ = u'container'


class OrderedContainer(ordered.OrderedContainer):
    """Sample container."""
    __name__ = u'container'


class Content(object):
    """Sample content."""

    def __init__(self, title, number):
        self.title = title
        self.number = number


class SimpleTable(table.Table):

    def setUpColumns(self):
        return [
            column.addColumn(self, TitleColumn, u'title',
                             cellRenderer=cellRenderer,
                             headCellRenderer=headCellRenderer,
                             weight=1),
            column.addColumn(self, NumberColumn, name=u'number',
                             weight=2, header=u'Number')]


def headCellRenderer():
    return u'My items'


def cellRenderer(item):
    return u'%s item' % item.title


@zope.interface.implementer(IZopeDublinCore)
@zope.component.adapter(zope.interface.Interface)
class DublinCoreAdapterStub(object):
    """Dublin core adapter stub."""

    __Security_checker__ = checker.Checker(
        {"created": "zope.Public",
         "modified": "zope.Public",
         "title": "zope.Public",
         },
        {"title": "zope.app.dublincore.change"})

    def __init__(self, context):
        pass
    title = 'faux title'
    size = 1024
    created = datetime.datetime(2001, 1, 1, 1, 1, 1)
    modified = datetime.datetime(2002, 2, 2, 2, 2, 2)


def setUpAdapters():
    zope.component.provideAdapter(z3c.table.value.ValuesForContainer)
    zope.component.provideAdapter(z3c.table.value.ValuesForSequence)


def setUp(test):
    test.globs['root'] = siteSetUp(True)
    zope.traversing.testing.setUp()
    zope.component.provideAdapter(DublinCoreAdapterStub)
    setUpAdapters()


def tearDown(test):
    siteTearDown()
