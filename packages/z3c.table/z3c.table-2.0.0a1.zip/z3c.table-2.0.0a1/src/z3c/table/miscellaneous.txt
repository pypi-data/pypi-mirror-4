Miscellaneous
-------------

Make coverage report happy and test different things.

Test if the getWeight method returns 0 (zero) on AttributeError:

  >>> from z3c.table.table import getWeight
  >>> getWeight(None)
  0

Create a container:

  >>> from z3c.table.testing import Container
  >>> container = Container()

Try to call a simple table and call renderBatch which should return an empty
string:

  >>> from z3c.table import table
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> simpleTable = table.Table(container, request)
  >>> simpleTable.renderBatch()
  u''

Try to render an empty table adapting an empty mapping:

  >>> simpleTable = table.Table({}, request)
  >>> simpleTable.cssClassSortedOn = None
  >>> simpleTable.render()
  u''

Since we register an adapter for IColumn on None (IOW on an empty mapping).

  >>> from zope.component import provideAdapter
  >>> from z3c.table import column
  >>> from z3c.table import interfaces
  >>> provideAdapter(column.NameColumn,
  ...     (None, None, interfaces.ITable), provides=interfaces.IColumn,
  ...      name='secondColumn')

Initializing rows definitions for the empty table initializes the columns
attribute list.

  >>> simpleTable.columns

  >>> simpleTable.initColumns()
  >>> simpleTable.columns
  [<NameColumn u'secondColumn'>]

Rendering the empty table now return the string:

  >>> print(simpleTable.render())
  <table>
    <thead>
      <tr>
        <th>Name</th>
      </tr>
    </thead>
    <tbody>
    </tbody>
  </table>


Let's see if the addColumn raises a ValueError if there is no Column class:

  >>> column.addColumn(simpleTable, column.Column, u'dummy')
  <Column u'dummy'>

  >>> column.addColumn(simpleTable, None, u'dummy')
  Traceback (most recent call last):
  ...
  ValueError: class_ None must implement IColumn.

Test if we can set additional kws in addColumn:

  >>> simpleColumn = column.addColumn(simpleTable, column.Column, u'dummy',
  ...     foo='foo value', bar=u'something else', counter=99)
  >>> simpleColumn.foo
  'foo value'

  >>> simpleColumn.bar
  u'something else'

  >>> simpleColumn.counter
  99

The NoneCell class provides some methods which never get called. But these
are defined in the interface. Let's test the default values
and make coverage report happy.

Let's get an container item first:

  >>> from z3c.table.testing import Content
  >>> firstItem = Content('First', 1)
  >>> noneCellColumn = column.addColumn(simpleTable, column.NoneCell, u'none')
  >>> noneCellColumn.renderCell(firstItem)
  u''

  >>> noneCellColumn.getColspan(firstItem)
  0

  >>> noneCellColumn.renderHeadCell()
  u''

  >>> noneCellColumn.renderCell(firstItem)
  u''

The default ``Column`` implementation raises an NotImplementedError if we
do not override the renderCell method:

  >>> defaultColumn = column.addColumn(simpleTable, column.Column, u'default')
  >>> defaultColumn.renderCell(firstItem)
  Traceback (most recent call last):
  ...
  NotImplementedError: Subclass must implement renderCell
