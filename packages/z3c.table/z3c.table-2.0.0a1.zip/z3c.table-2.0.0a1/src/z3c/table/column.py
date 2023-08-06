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

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from z3c.table import interfaces
from zope.dublincore.interfaces import IZopeDublinCore
from zope.security.interfaces import Unauthorized
from zope.traversing import api
from zope.traversing.browser import absoluteURL
import zope.i18n
import zope.i18nmessageid
import zope.interface
import zope.location

_ = zope.i18nmessageid.MessageFactory('z3c')


def addColumn(self, class_, name, cellRenderer=None, headCellRenderer=None,
    colspan=None, weight=None, header=None, cssClasses=None, **kws):
    if not interfaces.IColumn.implementedBy(class_):
        raise ValueError('class_ %s must implement IColumn.' % class_)
    column = class_(self.context, self.request, self)
    column.__parent__ = self
    column.__name__ = name
    if cellRenderer is not None:
        # overload method
        column.renderCell = cellRenderer
    if headCellRenderer is not None:
        # overload method
        column.renderHeadCell = headCellRenderer
    if colspan is not None:
        column.colspan = colspan
    if weight is not None:
        column.weight = weight
    if header is not None:
        column.header = header
    if cssClasses is not None:
        column.cssClasses = cssClasses
    for name, value in kws.items():
        setattr(column, name, value)
    return column


def getName(item):
    # probably not IPhysicallyLocatable but still could have a __name__
    try:
        return api.getName(item)
    except TypeError as e:
        return item.__name__


def safeGetAttr(obj, attr, default):
    try:
        return getattr(obj, attr, default)
    except Unauthorized:
        return default


@zope.interface.implementer(interfaces.IColumn)
class Column(zope.location.Location):
    """Column provider."""


    # variables will be set by table
    id = None

    # customize this part if needed
    colspan = 0
    weight = 0
    header = u''
    cssClasses = {}

    def __init__(self, context, request, table):
        self.__parent__ = context
        self.context = context
        self.request = request
        self.table = table

    def update(self):
        pass

    def getColspan(self, item):
        """Returns the colspan value."""
        return self.colspan

    def getSortKey(self, item):
        """Returns the sort key used for column sorting."""
        return self.renderCell(item)

    def renderHeadCell(self):
        """Header cell content."""
        header = zope.component.queryMultiAdapter((self.context,
            self.request, self.table, self), interfaces.IColumnHeader)
        if header:
            header.update()
            return header.render()
        return zope.i18n.translate(self.header, context=self.request)

    def renderCell(self, item):
        """Cell content."""
        raise NotImplementedError('Subclass must implement renderCell')

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


@zope.interface.implementer(interfaces.INoneCell)
class NoneCell(Column):
    """None cell is used for mark a previous colspan."""

    def getColspan(self, item):
        return 0

    def renderHeadCell(self):
        return u''

    def renderCell(self, item):
        return u''


# predefined columns
class NameColumn(Column):
    """Name column."""

    header = _('Name')

    def renderCell(self, item):
        return getName(item)


try:
    apply
except NameError:
    def apply(f, *a):
        return f(*a)

class RadioColumn(Column):
    """Radio column."""

    header = _('X')

    @apply
    def selectedItem():
        # use the items form the table
        def get(self):
            if len(self.table.selectedItems):
                return list(self.table.selectedItems).pop()
        def set(self, value):
            self.table.selectedItems = [value]
        return property(get, set)

    def getSortKey(self, item):
        return getName(item)

    def getItemKey(self, item):
        return '%s-selectedItem' % self.id

    def getItemValue(self, item):
        return getName(item)

    def update(self):
        items = [item for item in self.table.values
                 if self.getItemValue(item) in self.request.get(
                     self.getItemKey(item), [])]
        if len(items):
            self.selectedItem = items.pop()

    def renderCell(self, item):
        selected = u''
        if item == self.selectedItem:
            selected='checked="checked"'
        return u'<input type="radio" class="%s" name="%s" value="%s" %s />' %(
            'radio-widget', self.getItemKey(item), self.getItemValue(item),
            selected)


class CheckBoxColumn(Column):
    """Checkbox column."""

    header = _('X')
    weight = 10

    @apply
    def selectedItems():
        # use the items form the table
        def get(self):
            return self.table.selectedItems
        def set(self, values):
            self.table.selectedItems = values
        return property(get, set)

    def getSortKey(self, item):
        return getName(item)

    def getItemKey(self, item):
        return '%s-selectedItems' % self.id

    def getItemValue(self, item):
        return getName(item)

    def isSelected(self, item):
        v = self.request.get(self.getItemKey(item), [])
        if not isinstance(v, list):
            # ensure that we have a list which prevents to compare strings
            v = [v]
        if self.getItemValue(item) in v:
            return True
        return False

    def update(self):
        self.selectedItems = [item for item in self.table.values
                              if self.isSelected(item)]

    def renderCell(self, item):
        selected = u''
        if item in self.selectedItems:
            selected = 'checked="checked"'
        return u'<input type="checkbox" class="%s" name="%s" value="%s" %s />' \
            % ('checkbox-widget', self.getItemKey(item), self.getItemValue(item),
            selected)


class GetAttrColumn(Column):
    """Get attribute column."""

    attrName = None
    defaultValue = u''

    def getValue(self, obj):
        if obj is not None and self.attrName is not None:
            return safeGetAttr(obj, self.attrName, self.defaultValue)
        return self.defaultValue

    def renderCell(self, item):
        return self.getValue(item)


class GetItemColumn(Column):
    """Get value from item index/key column."""

    idx = None
    defaultValue = u''

    def getValue(self, obj):
        if obj is not None and self.idx is not None:
            try:
                return obj[self.idx]
            except (KeyError, IndexError, Unauthorized):
                return self.defaultValue
        return self.defaultValue

    def renderCell(self, item):
        return self.getValue(item)


class I18nGetAttrColumn(GetAttrColumn):
    """GetAttrColumn which translates its content."""

    def renderCell(self, item):
        return zope.i18n.translate(self.getValue(item), context=self.request)


class FormatterColumn(Column):
    """Formatter column."""

    formatterCategory = u'dateTime'
    formatterLength = u'medium'
    formatterName = None
    formatterCalendar = u'gregorian'

    def getFormatter(self):
        return self.request.locale.dates.getFormatter(
            self.formatterCategory, self.formatterLength, self.formatterName,
            self.formatterCalendar)


class GetAttrFormatterColumn(FormatterColumn, GetAttrColumn):
    """Get attribute and formatter column."""

    def renderCell(self, item):
        formatter = self.getFormatter()
        value = self.getValue(item)
        if value:
            value = formatter.format(value)
        return value


class CreatedColumn(FormatterColumn, GetAttrColumn):
    """Created date column."""

    header = _('Created')
    weight = 100

    formatterCategory = u'dateTime'
    formatterLength = u'short'
    attrName = 'created'

    def renderCell(self, item):
        formatter = self.getFormatter()
        dc = IZopeDublinCore(item, None)
        value = self.getValue(dc)
        if value:
            value = formatter.format(value)
        return value


class ModifiedColumn(FormatterColumn, GetAttrColumn):
    """Created date column."""

    header = _('Modified')
    weight = 110

    formatterCategory = u'dateTime'
    formatterLength = u'short'
    attrName = 'modified'

    def renderCell(self, item):
        formatter = self.getFormatter()
        dc = IZopeDublinCore(item, None)
        value = self.getValue(dc)
        if value:
            value = formatter.format(value)
        return value


class LinkColumn(Column):
    """Name column."""

    header = _('Name')
    linkName = None
    linkTarget = None
    linkContent = None
    linkCSS = None

    def getLinkURL(self, item):
        """Setup link url."""
        if self.linkName is not None:
            return '%s/%s' % (absoluteURL(item, self.request), self.linkName)
        return absoluteURL(item, self.request)

    def getLinkCSS(self, item):
        """Setup link css."""
        return self.linkCSS and ' class="%s"' % self.linkCSS or ''

    def getLinkTarget(self, item):
        """Setup link css."""
        return self.linkTarget and ' target="%s"' % self.linkTarget or ''

    def getLinkContent(self, item):
        """Setup link content."""
        if self.linkContent:
            return zope.i18n.translate(self.linkContent, context=self.request)
        return getName(item)

    def renderCell(self, item):
        # setup a tag
        return '<a href="%s"%s%s>%s</a>' % (self.getLinkURL(item),
            self.getLinkTarget(item), self.getLinkCSS(item),
            self.getLinkContent(item))


class EMailColumn(LinkColumn, GetAttrColumn):
    "Column to display mailto links."

    header = _(u'E-Mail')
    attrName = None # attribute name which contains the mail address
    defaultValue = u'' # value which is rendered when no value is found
    linkContent = None

    def getLinkURL(self, item):
        return 'mailto:%s' % self.getValue(item)

    def getLinkContent(self, item):
        if self.linkContent:
            return zope.i18n.translate(self.linkContent, context=self.request)
        return self.getValue(item)

    def renderCell(self, item):
        value = self.getValue(item)
        if value is self.defaultValue or value is None:
            return self.defaultValue
        return super(EMailColumn, self).renderCell(item)

def ensureList(item):
    if not isinstance(item, (list, tuple)):
        return [item]
    return item

class SelectedItemColumn(LinkColumn):
    """Link which can set an item."""

    selectedItem = None

    @property
    def viewURL(self):
        return '%s/%s' % (absoluteURL(self.context, self.request),
            self.table.__name__)

    def getItemKey(self, item):
        return '%s-selectedItems' % self.id

    def getItemValue(self, item):
        return getName(item)

    def getSortKey(self, item):
        """Returns the sort key used for column sorting."""
        return self.getLinkContent(item)

    def getLinkContent(self, item):
        """Setup link content."""
        return self.linkContent or getName(item)

    def getLinkURL(self, item):
        """Setup link url."""
        return '%s?%s' % (self.viewURL,
            urlencode({self.getItemKey(item): self.getItemValue(item)}))

    def update(self):
        items = [item for item in self.table.values
                 if self.getItemValue(item) in ensureList(self.request.get(
                     self.getItemKey(item), []))]
        if len(items):
            self.selectedItem = items.pop()
            self.table.selectedItems = [self.selectedItem]


class ContentsLinkColumn(LinkColumn):
    """Link pointing to contents.html."""

    linkName = 'contents.html'


class IndexLinkColumn(LinkColumn):
    """Link pointing to index.html."""

    linkName = 'index.html'


class EditLinkColumn(LinkColumn):
    """Link pointing to edit.html."""

    linkName = 'edit.html'
