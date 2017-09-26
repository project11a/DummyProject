''' Dummy Project Copyright J. Boss

/system/data/abc.py

Situation:
In a statically indexed database-table (row number does never change),
sorting is a real issue. One might just add another table with the indexes
of the main one in sorted order. This would fix the issue, except for one point,
the sorted table may still be slow, depending on the file format 
(i rarely got to read those). My own is really not designed for this purpose,
even though it allows manipulations. Those are running entire blocks at once,
what is, for instance, aceptable in chunk indexes (to accelerate, this approach
does not seem to be scalable to me. Memory exhaustion may become a problem, 
even if translated to C code - speed might actually be okay). 
Doing hundreds of files is not okay here too.
With the following approach, I assume that the sorted table may just be a list 
in abstract, so we can exchange file systems.

The Idea is to provide bisectional acceleration to chained lists 
of sorted data (where chains optimize the write speeds).
Chains themselves are totally slow as soon as they grow a bit.
(May try to tweak some of it out, however, it is still the problem).
But chains are also a powerful way of memory allocation, they
provide a meaningful way to manipulate the list.
The solution is layering. And the problem. An individual layer 
does not provide anything relevant to the effective data that is 
being looked for.
There are two obvious aproaches in layering bisections:
The first is to use triple-pointers. On the supermost layer,
one pointer marks the middle of the entire sorted index,
the other two point the same for the two halves of the index.
But this is less obvious as it may seem at first. We'd still have to 
overcome the issue of slow changes as we'd need to adjust the indexes each time,
possibly even up to the root (and the root would be a log(length, 2) far away).
This would make sure that the supermost keeps pointing to the middle and cause
seriuos calculation overheads.

Mappings on Mappings
Fixed number of nodes per map
map levels required: log(length, number_of_nodes) 
total maps required: 
map count changes dynamically
map stats are to be kept just in time:
	when removing: fail
	when adding: 
'''
from system.data import sparse

class ABS(object):
  def __init__(self, sparse):
    self

class Map(object):
  def __init__(self, mgr, offset):
