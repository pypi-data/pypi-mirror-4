Subset Batching
---------------

  >>> from z3c.batching.subset import SubsetBatch

Sometimes (for performance reasons), even though the user needs
a batched UI, we want to limit the computation to the
subset of values actually shown to the user.

Because we initialize the batch with a subset of data, we also
need to provide explicitly the length of the full data set.

Let's create a subset of data::

  >>> data = range(20, 30)

We use it as part of a longer data set::

  >>> batch = SubsetBatch(data, length=50, start=20, size=10)

Full API check::

  >>> batch.firstElement
  20
  >>> batch.lastElement
  29
  >>> batch.index
  2
  >>> batch.number
  3
  >>> batch.total
  5
  >>> batch[2]
  22
  >>> len(batch)
  10
  >>> batch[-1] == batch.lastElement
  True
  >>> [item for item in batch]
  [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]

  >>> batch.next
  <EmptyBatch start=30, size=10>
  >>> batch.previous
  <EmptyBatch start=10, size=10>
  >>> batch.next.previous == batch
  True
  >>> 22 in batch
  True
  >>> 10 in batch
  False
  >>> batch[5:8]
  [25, 26, 27]

You have seen above that the contiguous batches are instances of
the ``EmptyBatch`` class. As those instances hold no data, we raise errors to ensure that no batch provider tries to display item data::

  >>> empty = batch.next
  >>> empty
  <EmptyBatch start=30, size=10>
  >>> empty.firstElement
  Traceback (most recent call last):
  ...
  ValueError: EmptyBatch holds no item
  >>> empty.lastElement
  Traceback (most recent call last):
  ...
  ValueError: EmptyBatch holds no item
  >>> empty[0]
  Traceback (most recent call last):
  ...
  ValueError: EmptyBatch holds no item
  >>> [item for item in empty]
  Traceback (most recent call last):
  ...
  ValueError: EmptyBatch holds no item
