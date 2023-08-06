====
TODO
====

- implement nicer batch representation. Use div wrapper around batch links and
  give them the class rahter then set the CSS class in href tags.

- implement render methods for each batch status, e.g. renderFirstBatch,
  renderLastBatch.

- push the current sorted status to the Column objects/class
  it's just mad that we try to figure this at several places
  (SortingColumnHeader, Table.getCSSSortClass)
  possibly with different results ;-)