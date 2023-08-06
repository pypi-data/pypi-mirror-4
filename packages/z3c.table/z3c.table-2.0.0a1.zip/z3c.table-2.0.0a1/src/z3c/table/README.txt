=========
z3c Table
=========

.. contents::

The goal of this package is to offer a modular table rendering library. We use
the content provider pattern and the column are implemented as adapters which
will give us a powerful base concept.

Some important concepts we use
------------------------------

- separate implementation in update render parts, This allows to manipulate
  data after update call and before we render them.

- allow to use page templates if needed. By default all is done in python.

- allow to use the rendered batch outside the existing table HTML part.

No skins
--------

This package does not provide any kind of template or skin support. Most the
time if you need to render a table, you will use your own skin concept. This means
you can render the table or batch within your own templates. This will ensure
that we have as few dependencies as possible in this package and the package
can get reused with any skin concept.

Note
----

As you probably know, batching is only possible after sorting columns. This is
a nightmare if it comes to performance. The reason is, all data need to get
sorted before the batch can start at the given position. And sorting can most
of the time only be done by touching each object. This means you have to be careful
if you are using a large set of data, even if you use batching.

Sample data setup
-----------------

Let's create a sample container which we can use as our iterable context:

  >>> from zope.container import btree
  >>> class Container(btree.BTreeContainer):
  ...     """Sample container."""
  ...     __name__ = u'container'
  >>> container = Container()

and set a parent for the container:

  >>> root['container'] = container

and create a sample content object which we use as container item:

  >>> class Content(object):
  ...     """Sample content."""
  ...     def __init__(self, title, number):
  ...         self.title = title
  ...         self.number = number

Now setup some items:

  >>> container[u'first'] = Content('First', 1)
  >>> container[u'second'] = Content('Second', 2)
  >>> container[u'third'] = Content('Third', 3)


Table
-----

Create a test request and represent the table:

  >>> from zope.publisher.browser import TestRequest
  >>> from z3c.table import table
  >>> request = TestRequest()
  >>> plainTable = table.Table(container, request)
  >>> plainTable.cssClassSortedOn = None

Now we can update and render the table. As you can see with an empty container
we will not get anything that looks like a table. We just get an empty string:

  >>> plainTable.update()
  >>> plainTable.render()
  u''


Column Adapter
--------------

We can create a column for our table:

  >>> import zope.component
  >>> from z3c.table import interfaces
  >>> from z3c.table import column

  >>> class TitleColumn(column.Column):
  ...
  ...     weight = 10
  ...     header = u'Title'
  ...
  ...     def renderCell(self, item):
  ...         return u'Title: %s' % item.title

Now we can register the column:

  >>> zope.component.provideAdapter(TitleColumn,
  ...     (None, None, interfaces.ITable), provides=interfaces.IColumn,
  ...      name='firstColumn')

Now we can render the table again:

  >>> plainTable.update()
  >>> print(plainTable.render())
  <table>
    <thead>
      <tr>
        <th>Title</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Title: First</td>
      </tr>
      <tr>
        <td>Title: Second</td>
      </tr>
      <tr>
        <td>Title: Third</td>
      </tr>
    </tbody>
  </table>

We can also use the predefined name column:

  >>> zope.component.provideAdapter(column.NameColumn,
  ...     (None, None, interfaces.ITable), provides=interfaces.IColumn,
  ...      name='secondColumn')

Now we will get an additional column:

  >>> plainTable.update()
  >>> print(plainTable.render())
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Title</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>first</td>
        <td>Title: First</td>
      </tr>
      <tr>
        <td>second</td>
        <td>Title: Second</td>
      </tr>
      <tr>
        <td>third</td>
        <td>Title: Third</td>
      </tr>
    </tbody>
  </table>


Colspan
-------

Now let's show how we can define a colspan condition of 2 for a column:

  >>> class ColspanColumn(column.NameColumn):
  ...
  ...     weight = 999
  ...
  ...     def getColspan(self, item):
  ...         # colspan condition
  ...         if item.__name__ == 'first':
  ...             return 2
  ...         else:
  ...             return 0
  ...
  ...     def renderHeadCell(self):
  ...         return u'Colspan'
  ...
  ...     def renderCell(self, item):
  ...         return u'colspan: %s' % item.title

Now we register this column adapter as colspanColumn:

  >>> zope.component.provideAdapter(ColspanColumn,
  ...     (None, None, interfaces.ITable), provides=interfaces.IColumn,
  ...      name='colspanColumn')

Now you can see that the colspan of the ColspanAdapter is larger than the table.
This will raise a ValueError:

  >>> plainTable.update()
  Traceback (most recent call last):
  ...
  ValueError: Colspan for column '<ColspanColumn u'colspanColumn'>' is larger than the table.

But if we set the column as first row, it will render the colspan correctly:

  >>> class CorrectColspanColumn(ColspanColumn):
  ...     """Colspan with correct weight."""
  ...
  ...     weight = -1  # NameColumn is 0

Register and render the table again:

  >>> zope.component.provideAdapter(CorrectColspanColumn,
  ...     (None, None, interfaces.ITable), provides=interfaces.IColumn,
  ...      name='colspanColumn')

  >>> plainTable.update()
  >>> print(plainTable.render())
  <table>
    <thead>
      <tr>
        <th>Colspan</th>
        <th>Name</th>
        <th>Title</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td colspan="2">colspan: First</td>
        <td>Title: First</td>
      </tr>
      <tr>
        <td>colspan: Second</td>
        <td>second</td>
        <td>Title: Second</td>
      </tr>
      <tr>
        <td>colspan: Third</td>
        <td>third</td>
        <td>Title: Third</td>
      </tr>
    </tbody>
  </table>

Setup columns
-------------

The existing implementation allows us to define a table in a class without
using the modular adapter pattern for columns.

First we need to define a column which can render a value for our items:

  >>> class SimpleColumn(column.Column):
  ...
  ...     weight = 0
  ...
  ...     def renderCell(self, item):
  ...         return item.title

Let's define our table which defines the columns explicitly. you can also see
that we do not return the columns in the correct order:

  >>> class PrivateTable(table.Table):
  ...     cssClassSortedOn = None
  ...
  ...     def setUpColumns(self):
  ...         firstColumn = TitleColumn(self.context, self.request, self)
  ...         firstColumn.__name__ = u'title'
  ...         firstColumn.weight = 1
  ...         secondColumn = SimpleColumn(self.context, self.request, self)
  ...         secondColumn.__name__ = u'simple'
  ...         secondColumn.weight = 2
  ...         secondColumn.header = u'The second column'
  ...         return [secondColumn, firstColumn]

Now we can create, update and render the table and see that this renders a nice
table too:

  >>> privateTable = PrivateTable(container, request)
  >>> privateTable.update()
  >>> print(privateTable.render())
  <table>
    <thead>
      <tr>
        <th>Title</th>
        <th>The second column</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Title: First</td>
        <td>First</td>
      </tr>
      <tr>
        <td>Title: Second</td>
        <td>Second</td>
      </tr>
      <tr>
        <td>Title: Third</td>
        <td>Third</td>
      </tr>
    </tbody>
  </table>


Cascading Style Sheet
---------------------

Our table and column implementation supports css class assignment. Let's define
a table and columns with some css class values:

  >>> class CSSTable(table.Table):
  ...
  ...     cssClasses = {'table': 'table',
  ...                   'thead': 'thead',
  ...                   'tbody': 'tbody',
  ...                   'th': 'th',
  ...                   'tr': 'tr',
  ...                   'td': 'td'}
  ...     cssClassSortedOn = None
  ...
  ...     def setUpColumns(self):
  ...         firstColumn = TitleColumn(self.context, self.request, self)
  ...         firstColumn.__name__ = u'title'
  ...         firstColumn.__parent__ = self
  ...         firstColumn.weight = 1
  ...         firstColumn.cssClasses = {'th':'thCol', 'td':'tdCol'}
  ...         secondColumn = SimpleColumn(self.context, self.request, self)
  ...         secondColumn.__name__ = u'simple'
  ...         secondColumn.__parent__ = self
  ...         secondColumn.weight = 2
  ...         secondColumn.header = u'The second column'
  ...         return [secondColumn, firstColumn]

Now let's see if we got the css class assigned which we defined in the table and
column. Note that the ``th`` and ``td`` got CSS declarations from the table and
from the column:

  >>> cssTable = CSSTable(container, request)
  >>> cssTable.update()
  >>> print(cssTable.render())
  <table class="table">
    <thead class="thead">
      <tr class="tr">
        <th class="thCol th">Title</th>
        <th class="th">The second column</th>
      </tr>
    </thead>
    <tbody class="tbody">
      <tr class="tr">
        <td class="tdCol td">Title: First</td>
        <td class="td">First</td>
      </tr>
      <tr class="tr">
        <td class="tdCol td">Title: Second</td>
        <td class="td">Second</td>
      </tr>
      <tr class="tr">
        <td class="tdCol td">Title: Third</td>
        <td class="td">Third</td>
      </tr>
    </tbody>
  </table>


Alternating table
-----------------

We offer built in support for alternating table rows based on even and odd CSS
classes. Let's define a table including other CSS classes. For even/odd support,
we only need to define the ``cssClassEven`` and ``cssClassOdd`` CSS classes:

  >>> class AlternatingTable(table.Table):
  ...
  ...     cssClasses = {'table': 'table',
  ...                   'thead': 'thead',
  ...                   'tbody': 'tbody',
  ...                   'th': 'th',
  ...                   'tr': 'tr',
  ...                   'td': 'td'}
  ...
  ...     cssClassEven = u'even'
  ...     cssClassOdd = u'odd'
  ...     cssClassSortedOn = None
  ...
  ...     def setUpColumns(self):
  ...         firstColumn = TitleColumn(self.context, self.request, self)
  ...         firstColumn.__name__ = u'title'
  ...         firstColumn.__parent__ = self
  ...         firstColumn.weight = 1
  ...         firstColumn.cssClasses = {'th':'thCol', 'td':'tdCol'}
  ...         secondColumn = SimpleColumn(self.context, self.request, self)
  ...         secondColumn.__name__ = u'simple'
  ...         secondColumn.__parent__ = self
  ...         secondColumn.weight = 2
  ...         secondColumn.header = u'The second column'
  ...         return [secondColumn, firstColumn]

Now update and render the new table. As you can see the given ``tr`` class is
added to the even and odd classes:

  >>> alternatingTable = AlternatingTable(container, request)
  >>> alternatingTable.update()
  >>> print(alternatingTable.render())
  <table class="table">
    <thead class="thead">
      <tr class="tr">
        <th class="thCol th">Title</th>
        <th class="th">The second column</th>
      </tr>
    </thead>
    <tbody class="tbody">
      <tr class="even tr">
        <td class="tdCol td">Title: First</td>
        <td class="td">First</td>
      </tr>
      <tr class="odd tr">
        <td class="tdCol td">Title: Second</td>
        <td class="td">Second</td>
      </tr>
      <tr class="even tr">
        <td class="tdCol td">Title: Third</td>
        <td class="td">Third</td>
      </tr>
    </tbody>
  </table>


Class based Table setup
-----------------------

There is a more elegant way to define table rows at class level. We offer
a method which you can use if you need to define some columns called
``addColumn``. Before we define the table. let's define some cell renderer:

  >>> def headCellRenderer():
  ...     return u'My items'

  >>> def cellRenderer(item):
  ...     return u'%s item' % item.title

Now we can define our table and use the custom cell renderer:

  >>> class AddColumnTable(table.Table):
  ...
  ...     cssClasses = {'table': 'table',
  ...                   'thead': 'thead',
  ...                   'tbody': 'tbody',
  ...                   'th': 'th',
  ...                   'tr': 'tr',
  ...                   'td': 'td'}
  ...
  ...     cssClassEven = u'even'
  ...     cssClassOdd = u'odd'
  ...     cssClassSortedOn = None
  ...
  ...     def setUpColumns(self):
  ...         return [
  ...             column.addColumn(self, TitleColumn, u'title',
  ...                              cellRenderer=cellRenderer,
  ...                              headCellRenderer=headCellRenderer,
  ...                              weight=1, colspan=0),
  ...             column.addColumn(self, SimpleColumn, name=u'simple',
  ...                              weight=2, header=u'The second column',
  ...                              cssClasses = {'th':'thCol', 'td':'tdCol'})
  ...             ]

Add some more content::

  >>> container[u'fourth'] = Content('Fourth', 4)
  >>> container[u'zero'] = Content('Zero', 0)

  >>> addColumnTable = AddColumnTable(container, request)
  >>> addColumnTable.update()
  >>> print(addColumnTable.render())
  <table class="table">
    <thead class="thead">
      <tr class="tr">
        <th class="th">My items</th>
        <th class="thCol th">The second column</th>
      </tr>
    </thead>
    <tbody class="tbody">
      <tr class="even tr">
        <td class="td">First item</td>
        <td class="tdCol td">First</td>
      </tr>
      <tr class="odd tr">
        <td class="td">Fourth item</td>
        <td class="tdCol td">Fourth</td>
      </tr>
      <tr class="even tr">
        <td class="td">Second item</td>
        <td class="tdCol td">Second</td>
      </tr>
      <tr class="odd tr">
        <td class="td">Third item</td>
        <td class="tdCol td">Third</td>
      </tr>
      <tr class="even tr">
        <td class="td">Zero item</td>
        <td class="tdCol td">Zero</td>
      </tr>
    </tbody>
  </table>

As you can see the table columns provide all attributes we set in the addColumn
method:

  >>> titleColumn = addColumnTable.rows[0][0][1]
  >>> titleColumn
  <TitleColumn u'title'>

  >>> titleColumn.__name__
  u'title'

  >>> titleColumn.__parent__
  <AddColumnTable None>

  >>> titleColumn.colspan
  0

  >>> titleColumn.weight
  1

  >>> titleColumn.header
  u'Title'

  >>> titleColumn.cssClasses
  {}

and the second column:

  >>> simpleColumn = addColumnTable.rows[0][1][1]
  >>> simpleColumn
  <SimpleColumn u'simple'>

  >>> simpleColumn.__name__
  u'simple'

  >>> simpleColumn.__parent__
  <AddColumnTable None>

  >>> simpleColumn.colspan
  0

  >>> simpleColumn.weight
  2

  >>> simpleColumn.header
  u'The second column'

  >>> sorted(simpleColumn.cssClasses.items())
  [('td', 'tdCol'), ('th', 'thCol')]


Headers
-------

We can change the rendering of the header of, e.g, the Title column by
registering a IHeaderColumn adapter. This may be useful for adding links to
column headers for an existing table implementation.

We'll use a fresh almost empty container.:

  >>> container = Container()
  >>> root['container-1'] = container
  >>> container[u'first'] = Content('First', 1)
  >>> container[u'second'] = Content('Second', 2)
  >>> container[u'third'] = Content('Third', 3)

  >>> class myTableClass(table.Table):
  ...     cssClassSortedOn = None

  >>> myTable = myTableClass(container, request)

  >>> class TitleColumn(column.Column):
  ...
  ...     header = u'Title'
  ...     weight = -2
  ...
  ...     def renderCell(self, item):
  ...         return item.title

Now we can register a column adapter directly to our table class:

  >>> zope.component.provideAdapter(TitleColumn,
  ...     (None, None, myTableClass), provides=interfaces.IColumn,
  ...      name='titleColumn')

And add a registration for a column header - we'll use here the provided generic
sorting header implementation:

  >>> from z3c.table.header import SortingColumnHeader
  >>> zope.component.provideAdapter(SortingColumnHeader,
  ...     (None, None, interfaces.ITable, interfaces.IColumn),
  ...     provides=interfaces.IColumnHeader)

Now we can render the table and we shall see a link in the header. Note that it
is set to switch to descending as the table initially will display the first
column as ascending:

  >>> myTable.update()
  >>> print(myTable.render())
  <table>
   <thead>
    <tr>
     <th><a
      href="?table-sortOn=table-titleColumn-0&table-sortOrder=descending"
      title="Sort">Title</a></th>
  ...
  </table>

If the table is initially set to descending, the link should allow to switch to
ascending again:

  >>> myTable.sortOrder = 'descending'
  >>> print(myTable.render())
  <table>
   <thead>
    <tr>
     <th><a
      href="?table-sortOn=table-titleColumn-0&table-sortOrder=ascending"
      title="Sort">Title</a></th>
  ...
  </table>

If the table is ascending but the request was descending,
the link should allow to switch again to ascending:

  >>> descendingRequest = TestRequest(form={'table-sortOn': 'table-titleColumn-0',
  ...                                   'table-sortOrder':'descending'})
  >>> myTable = myTableClass(container, descendingRequest)
  >>> myTable.sortOrder = 'ascending'
  >>> myTable.update()
  >>> print(myTable.render())
  <table>
   <thead>
    <tr>
     <th><a
      href="?table-sortOn=table-titleColumn-0&table-sortOrder=ascending"
      title="Sort">Title</a></th>
  ...
  </table>
