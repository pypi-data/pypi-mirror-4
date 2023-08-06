SequenceTable
-------------

A sequence table can be used if we need to provide a table for a sequence
of items instead of a mapping. Define the same sequence of items we used before
we added the other 1000 items:

  >>> from z3c.table.testing import Content
  >>> dataSequence = []
  >>> dataSequence.append(Content('Zero', 0))
  >>> dataSequence.append(Content('First', 1))
  >>> dataSequence.append(Content('Second', 2))
  >>> dataSequence.append(Content('Third', 3))
  >>> dataSequence.append(Content('Fourth', 4))
  >>> dataSequence.append(Content('Fifth', 5))
  >>> dataSequence.append(Content('Sixth', 6))
  >>> dataSequence.append(Content('Seventh', 7))
  >>> dataSequence.append(Content('Eighth', 8))
  >>> dataSequence.append(Content('Ninth', 9))
  >>> dataSequence.append(Content('Tenth', 10))
  >>> dataSequence.append(Content('Eleventh', 11))
  >>> dataSequence.append(Content('Twelfth', 12))
  >>> dataSequence.append(Content('Thirteenth', 13))
  >>> dataSequence.append(Content('Fourteenth', 14))
  >>> dataSequence.append(Content('Fifteenth', 15))
  >>> dataSequence.append(Content('Sixteenth', 16))
  >>> dataSequence.append(Content('Seventeenth', 17))
  >>> dataSequence.append(Content('Eighteenth', 18))
  >>> dataSequence.append(Content('Nineteenth', 19))
  >>> dataSequence.append(Content('Twentieth', 20))

Now let's define a new SequenceTable:

  >>> from z3c.table import table, column
  >>> from z3c.table.testing import (TitleColumn, NumberColumn, cellRenderer,
  ...                                headCellRenderer)
  >>> class SequenceTable(table.SequenceTable):
  ...
  ...     def setUpColumns(self):
  ...         return [
  ...             column.addColumn(self, TitleColumn, u'title',
  ...                              cellRenderer=cellRenderer,
  ...                              headCellRenderer=headCellRenderer,
  ...                              weight=1),
  ...             column.addColumn(self, NumberColumn, name=u'number',
  ...                              weight=2, header=u'Number')
  ...             ]

Now we can create our table adapting our sequence:

  >>> from zope.publisher.browser import TestRequest
  >>> sequenceRequest = TestRequest(form={'table-batchStart': '0',
  ...                                     'table-sortOn': 'table-number-1'})
  >>> sequenceTable = SequenceTable(dataSequence, sequenceRequest)
  >>> sequenceTable.cssClassSortedOn = None

We also need to give the table a location and a name like we normally setup
in traversing:

  >>> from z3c.table.testing import Container
  >>> container = Container()
  >>> root['container-1'] = container
  >>> sequenceTable.__parent__ = container
  >>> sequenceTable.__name__ = u'sequenceTable.html'

We need to configure our batch provider for the next step first. See the
section ``BatchProvider`` below for more infos about batch rendering:

  >>> from zope.configuration.xmlconfig import XMLConfig
  >>> import z3c.table
  >>> import zope.component
  >>> XMLConfig('meta.zcml', zope.component)()
  >>> XMLConfig('configure.zcml', z3c.table)()

And update and render the sequence table:

  >>> sequenceTable.update()
  >>> print(sequenceTable.render())
  <table>
    <thead>
      <tr>
        <th>My items</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Zero item</td>
        <td>number: 0</td>
      </tr>
      <tr>
        <td>First item</td>
        <td>number: 1</td>
      </tr>
      <tr>
        <td>Second item</td>
        <td>number: 2</td>
      </tr>
      <tr>
        <td>Third item</td>
        <td>number: 3</td>
      </tr>
      <tr>
        <td>Fourth item</td>
        <td>number: 4</td>
      </tr>
      <tr>
        <td>Fifth item</td>
        <td>number: 5</td>
      </tr>
      <tr>
        <td>Sixth item</td>
        <td>number: 6</td>
      </tr>
      <tr>
        <td>Seventh item</td>
        <td>number: 7</td>
      </tr>
      <tr>
        <td>Eighth item</td>
        <td>number: 8</td>
      </tr>
      <tr>
        <td>Ninth item</td>
        <td>number: 9</td>
      </tr>
      <tr>
        <td>Tenth item</td>
        <td>number: 10</td>
      </tr>
      <tr>
        <td>Eleventh item</td>
        <td>number: 11</td>
      </tr>
      <tr>
        <td>Twelfth item</td>
        <td>number: 12</td>
      </tr>
      <tr>
        <td>Thirteenth item</td>
        <td>number: 13</td>
      </tr>
      <tr>
        <td>Fourteenth item</td>
        <td>number: 14</td>
      </tr>
      <tr>
        <td>Fifteenth item</td>
        <td>number: 15</td>
      </tr>
      <tr>
        <td>Sixteenth item</td>
        <td>number: 16</td>
      </tr>
      <tr>
        <td>Seventeenth item</td>
        <td>number: 17</td>
      </tr>
      <tr>
        <td>Eighteenth item</td>
        <td>number: 18</td>
      </tr>
      <tr>
        <td>Nineteenth item</td>
        <td>number: 19</td>
      </tr>
      <tr>
        <td>Twentieth item</td>
        <td>number: 20</td>
      </tr>
    </tbody>
  </table>

As you can see, the items get rendered based on a data sequence. Now we set
the ``start batch at`` size to ``5``:

  >>> sequenceTable.startBatchingAt = 5

And the ``batchSize`` to ``5``:

  >>> sequenceTable.batchSize = 5

Now we can update and render the table again. But you will see that we only get
a table size of 5 rows:

  >>> sequenceTable.update()
  >>> print(sequenceTable.render())
  <table>
    <thead>
      <tr>
        <th>My items</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Zero item</td>
        <td>number: 0</td>
      </tr>
      <tr>
        <td>First item</td>
        <td>number: 1</td>
      </tr>
      <tr>
        <td>Second item</td>
        <td>number: 2</td>
      </tr>
      <tr>
        <td>Third item</td>
        <td>number: 3</td>
      </tr>
      <tr>
        <td>Fourth item</td>
        <td>number: 4</td>
      </tr>
    </tbody>
  </table>

And we set the sort order to ``reverse`` even if we use batching:

  >>> sequenceTable.sortOrder = u'reverse'
  >>> sequenceTable.update()
  >>> print(sequenceTable.render())
  <table>
    <thead>
      <tr>
        <th>My items</th>
        <th>Number</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Twentieth item</td>
        <td>number: 20</td>
      </tr>
      <tr>
        <td>Nineteenth item</td>
        <td>number: 19</td>
      </tr>
      <tr>
        <td>Eighteenth item</td>
        <td>number: 18</td>
      </tr>
      <tr>
        <td>Seventeenth item</td>
        <td>number: 17</td>
      </tr>
      <tr>
        <td>Sixteenth item</td>
        <td>number: 16</td>
      </tr>
    </tbody>
  </table>
