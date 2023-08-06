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
from z3c.table.i18n import _
import zope.contentprovider.interfaces
import zope.interface
import zope.schema


class IValues(zope.interface.Interface):
    """Table value adapter."""

    values = zope.interface.Attribute('Iterable table row data sequence.')


class ITable(zope.contentprovider.interfaces.IContentProvider):
    """Table provider"""

    columnCounter = zope.schema.Int(
        title=_(u'Column counter'),
        description=_(u'Column counter'),
        default=0)

    columnIndexById = zope.interface.Attribute(
        'Dict of column index number by id')

    columnByName = zope.interface.Attribute('Dict of columns by name')

    columns = zope.interface.Attribute('Sequence of columns')

    rows = zope.interface.Attribute('Sequence of rows')

    selectedItems = zope.interface.Attribute('Sequence of selected items')

    # customize this part if needed
    prefix = zope.schema.BytesLine(
        title=_('Prefix'),
        description=_('The prefix of the table used to uniquely identify it.'),
        default=b'table')

    # css classes
    cssClasses = zope.interface.Attribute(
        'Dict of element name and CSS classes')

    # additional (row) css
    cssClassEven = zope.schema.TextLine(
        title=u'Even css row class',
        description=(u'CSS class for even rows.'),
        default=u'even',
        required=False)

    cssClassOdd = zope.schema.TextLine(
        title=u'Odd css row class',
        description=(u'CSS class for odd rows.'),
        default=u'odd',
        required=False)

    cssClassSelected = zope.schema.TextLine(
        title=u'Selected css row class',
        description=(u'CSS class for selected rows.'),
        default=u'selected',
        required=False)

    # sort attributes
    sortOn = zope.schema.Int(
        title=_(u'Sort on table index'),
        description=_(u'Sort on table index'),
        default=0)

    sortOrder = zope.schema.TextLine(
        title=_(u'Sort order'),
        description=_(u'Row sort order'),
        default=u'ascending')

    reverseSortOrderNames = zope.schema.List(
        title=u'Selected css row class',
        description=(u'CSS class for selected rows.'),
        value_type=zope.schema.TextLine(
            title=_(u'Reverse sort order name'),
            description=_(u'Reverse sort order name')
        ),
        default=[u'descending', u'reverse', u'down'],
        required=False)

    # batch attributes
    batchStart = zope.schema.Int(
        title=_(u'Batch start index'),
        description=_(u'Index the batch starts with'),
        default=0)

    batchSize = zope.schema.Int(
        title=_(u'Batch size'),
        description=_(u'The batch size'),
        default=50)

    startBatchingAt = zope.schema.Int(
        title=_(u'Batch start size'),
        description=_(u'The minimal size the batch starts to get used'),
        default=50)

    values = zope.interface.Attribute('Iterable table row data sequence.')

    def getCSSClass(element, cssClass=None):
        """Returns the css class if any or an empty string."""

    def setUpColumns():
        """Setup table column renderer."""

    def updateColumns():
        """Update columns."""

    def initColumns():
        """Initialize columns definitions used by the table"""

    def orderColumns():
        """Order columns."""

    def setUpRow(item):
        """Setup table row."""

    def setUpRows():
        """Setup table rows."""

    def getSortOn():
        """Returns sort on column id."""

    def getSortOrder():
        """Returns sort order criteria."""

    def sortRows():
        """Sort rows."""

    def getBatchSize():
        """Returns the batch size."""

    def getBatchStart():
        """Returns the batch start index."""

    def batchRows():
        """Batch rows."""

    def isSelectedRow(row):
        """Returns True for selected row."""

    def renderTable():
        """Render the table."""

    def renderHead():
        """Render the thead."""

    def renderHeadRow():
        """Render the table header rows."""

    def renderHeadCell(column):
        """Setup the table header rows."""

    def renderBody():
        """Render the table body."""

    def renderRows():
        """Render the table body rows."""

    def renderRow(row, cssClass=None):
        """Render the table body rows."""

    def renderCell(item, column, colspan=0):
        """Render a single table body cell."""

    def render():
        """Plain render method without keyword arguments."""


class ISequenceTable(ITable):
    """Sequence table adapts a sequence as context.

    This table can be used for adapting a z3c.indexer.search.ResultSet or
    z3c.batching.batch.Batch instance as context. Batch which wraps a
    ResultSet sequence.
    """


class IColumn(zope.interface.Interface):
    """Column provider"""

    id = zope.schema.TextLine(
        title = _(u'Id'),
        description = _(u'The column id'),
        default = None)

    # customize this part if needed
    colspan = zope.schema.Int(
        title = _(u'Colspan'),
        description = _(u'The colspan value'),
        default = 0)

    weight = zope.schema.Int(
        title = _(u'Weight'),
        description = _(u'The column weight'),
        default = 0)

    header = zope.schema.TextLine(
        title = _(u'Header name'),
        description = _(u'The header name'),
        default = u'')

    cssClasses = zope.interface.Attribute('Dict of element name and CSS classes')

    def getColspan(item):
        """Colspan value based on the given item."""

    def renderHeadCell():
        """Render the column header label."""

    def renderCell(item):
        """Render the column content."""


class INoneCell(IColumn):
    """None cell used for colspan."""


class IBatchProvider(zope.contentprovider.interfaces.IContentProvider):
    """Batch content provider"""

    def renderBatchLink(batch, cssClass=None):
        """Renders batch links."""

    def render():
        """Plain render method without keyword arguments."""


class IColumnHeader(zope.interface.Interface):
    """Multi-adapter for header rendering."""

    def update():
        """Override this method in subclasses if required"""

    def render():
        """Override this method in subclasses"""

    def getQueryStringArgs():
        """
        Because the header will most often be used to add links for sorting the
        columns it may also be necessary to collect other query arguments from
        the request.

        The initial use case here is to maintain a search term.
        """
