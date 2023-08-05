Batching
--------

This module implements a simple batching mechanism that allows you to split a
large sequence into smaller batch. The batch API provides skip, limit and sort
similar then provided by pymongo cursor.

Batch on empty root:

  >>> from j01.pager.batch import Batch
  >>> batch = Batch([], size=3)
  >>> batch
  <Batch start=0, size=0, total=0>

  >>> len(batch)
  0

  >>> batch.start
  0

  >>> batch.end
  -1
  
  >>> batch.size
  0

  >>> batch[0]
  Traceback (most recent call last):
  ...
  IndexError: ...


  >>> sequence = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
  ...             'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen']

We can now create a batch for this sequence. Let's make our batch size 3.
The first argument to the batch is always the full sequence. If no start
element is specified, the batch starts at the first element:

  >>> batch = Batch(sequence, size=3)
  >>> batch
  <Batch start=0, size=3, total=13>

  >>> len(batch)
  3

  >>> batch.start
  0

  >>> batch.end
  2
  
  >>> batch.size
  3

  >>> list(batch)
  ['one', 'two', 'three']

The start index is commonly specified in the constructor though:

  >>> batch = Batch(sequence, start=6, size=3)
  >>> list(batch)
  ['seven', 'eight', 'nine']

Note that the start is an index and starts at zero. If the start index is
greater than the largest index of the sequence, we will adjust the start
to the end:

  >>> batch = Batch(sequence, start=15, size=3)
  >>> batch
  <Batch start=13, size=0, total=13>

A batch implements the finite sequence interface and thus supports some
standard methods. For example, you can ask the batch for its length:

  >>> len(batch)
  0

Note that the length returns the true size of the batch, not the size we asked
for. You can also get an element by index, which is relative to the batch:

  >>> batch = Batch(sequence, start=6, size=3)
  >>> batch[0]
  'seven'
  >>> batch[1]
  'eight'
  >>> batch[2]
  'nine'

Slicing:

  >>> batch[:1]
  ['seven']

  >>> batch[1:2]
  ['eight']

  >>> batch[1:]	
  ['eight', 'nine']

  >>> batch[:]
  ['seven', 'eight', 'nine']

  >>> batch[10:]
  []

If you ask for index that is out of range, an index error is raised:

  >>> batch[3]
  Traceback (most recent call last):
  ...
  IndexError: batch index out of range

You can also iterate through the batch:

  >>> iterator = iter(batch)
  >>> iterator.next()
  'seven'
  >>> iterator.next()
  'eight'
  >>> iterator.next()
  'nine'

Batch also implement some of IReadSequence interface:

  >>> 'eight' in batch
  True

  >>> 'ten' in batch
  False

  >>> batch == Batch(sequence, start=6, size=3)
  True

  >>> batch != Batch(sequence, start=6, size=3)
  False

  >>> batch != Batch(sequence, start=3, size=3)
  True

Besides all of those common API methods, there are several properties that were
designed to make your life simpler. The start and size are specified:

  >>> batch.start
  6
  >>> batch.size
  3

The end index of the batch is immediately computed:

  >>> batch.end
  8

The batch slo supports the toal number of items:

  >>> batch.total
  13

And the amoun to batched sequence items:

  >>> len(batch)
  3


sort
----

We can also sort the batch items:

  >>> batch = Batch(sequence, start=0, size=10)
  >>> len(batch)
  10

  >>> list(batch)
  ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']

If we use an iteger, we will sort with an itemgetter operator:

  >>> batch = batch.sort(0)
  >>> list(batch)
  ['eight', 'eleven', 'four', 'five', 'nine', 'one', 'six', 'seven', 'two', 'three']

We can also reverse the order:

  >>> batch = batch.sort(0, True)
  >>> list(batch)
  ['two', 'three', 'ten', 'twelve', 'thirteen', 'six', 'seven', 'one', 'nine', 'four']

Or we can only reverse the order without sorting. As you can see, our batch 
still contains the sequence but in the reverse order and batching is applied
the the new reversed order. This means the batch contains the values 4 - 13
and not 1 - 10:

  >>> batch = Batch(sequence, start=0, size=10)
  >>> batch = batch.sort(sortOrder=True)
  >>> list(batch)
  ['thirteen', 'twelve', 'eleven', 'ten', 'nine', 'eight', 'seven', 'six', 'five', 'four']
