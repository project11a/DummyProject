''' Dummy Project Copyright J. Boss

/system/data/abc.py

Accelerated Bisectional Chains

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
seriuos calculation overheads. If we'd skip that entirely, a chain becomes as 
long as the entire list in the worst case. The Solution would be to track the 
number of nodes beyond a given one and the corresponding algorythm to process 
this data (basically cut a slice of the chain and add it reversedly to the
next node beyond that slice (which is easier if it's pointer is 0)).
The second is to define a maximum distance to the next node that is directly 
linked with a superior node (until node count is 1). This way, the calculation 
overhead reduces. One bad aspect of this approach is still the distance of a node.

A bad aspect of either approach is indexing. You're still able to easily get few 
results in their sorted order while beeing able to tell the actual index becomes complicated.
Anyway, why would someone use indexing on huge sorted indexes? Just start a query.

As you are probably reading this because of an interest in performance, the question
of maximum distance is obvious. It has also high impact on how many layers the
system will create. A high distance will keep the layers count very low, but this is
not the goal here. We'd like to reduce the time we need to get to a value. If the 
distance is high, but the layers got highly fragmented, that would have very bad impact.
If, however, the reverse is the case, almost no fragmention, that would boost performance
way further.
You may use this information to tweak some pieces for specific hardware (eg. align
the sparse allocations with the block device (if it is one) and keep using most of
it's capacity).
You'll like to see the docs for system.data.sparse and system.data.sparse.chain.
As the system optimizes most on the lowest layer, lowest fragmentation is desireable 
(what is limiting the maximum distance to a higher value). This has significant impact
on finding multiple results at once. If you'd like to align with 2KiB blocks, this would
give you space for 254 64bit values without having to allocate another block. Processing 
2KiB each time at once (when it changes) is maybe a bit too rough, 512B sounds more resonable.

map levels required: log(length, distance) 
map count changes dynamically
maximum addressable space with  64bits:  16 EiB (Quintilions/Trilions)
                                56bits:  64 PiB (Quadrilions/Biliards)
This is for the sparse          48bits: 256 TiB 
                                40bits:   1 TiB (Trilions/Bilions)
                                16bits:  64 KiB
                                 8bits: 256   B
the maximum file size may be increased if the underlying sparse controller is
being operated properly with the AddressModule (may also cause memory holes).
Choosing it too high will allow expansion.

The system will require 3 larger addresses in each map as well as the number of entries.
best resource usage approximates 1:1
48bits seems to be a resonable choice for most drives 

Map definition:
    [Previous] [Super] [Next] [Count] items...
    The first three fields have the address size, used to point around
    in sparse. Count is just 1 Byte to tell how many entries this map holds.
    Items have the address size for all layers except for the lowest which 
    holds an individual size. However, items are supposed to be numbers.

'''
from system.data import sparse
import mmap

class ABC(object):
    def __init__(self, sparse, asize=5, dist=99, isize=8, idist=62):
        ''' default values for 512 bytes blocks (512TiB) '''
        self.sparse = sparse
        self.asize = asize
        self.isize = isize
        self.dist = dist
        self.idist = idist
        self.hdr_end = asize*3+1
        self._al = b"\x00" * self.asize
        self._ah = b"\xff" * self.asize
        m = sparse.mmap(0, 1)
        self.layers = ord(m[0])
        self.map = [] # the uppermost map is here all the time
        off = 1
        while len(self.map) < dist:
            v = int.from_bytes(m[off:asize+off])
            if not v: 
                break
            self.map.append(v)
            off += asize
        m.close()
        
    ## API

    def find(self, fn):
        ''' reversed root finding algorythm '''
        l = self.layers
        s = [0, len(self.map)]
        while l > 0:
            while len(s) > 1:
                mid = (s[1]-s[0]) / 2 + s[0] # This is a bisection!
        
    def next(self, of, p):
        ''' returns the result as well as the map offset and position
            may move at most one map forward '''
        m = self.sparse.mmap(of, 1)
        v = p+1
        q = self._mapCount(m)
        if v >= q:
            v -= q
            of = self._mapNext(m)
            m.close()
            m = self.sparse.mmap(of, 1)
        ret = self._mapItem(m, v)
        m.close()
        return ret, of, v
        
    def prev(self, of, p):
        m = self.sparse.mmap(of, 1)
        if p == 0:
            of = self._mapPrev(m)
            m.close()
            m = self.sparse.mmap(of, 1)
            v = self._mapCount(m)-1
        else:
            v = p-1
        ret = self._mapItem(m, v)
        m.close()
        return ret, of, v
        
    ## Core
    
    def _mapItem(self, m, idx):
        off = self.hdr_end + idx * self.isize
        return int.from_bytes(m[off:off+self.isize])
    
    def _mapAddr(self, m, idx):
        off = self.hdr_end + idx * self.asize
        return int.from_bytes(m[off:off+self.asize])
                
    def _mapPrev(self, m):
        v = m[:self.asize]
        if v == self._al:
            raise RuntimeError("End of Chain")
        return int.from_bytes(v)
                
    def _mapSuper(self, m):
        return int.from_bytes(m[self.asize:self.asize*2])
                
    def _mapNext(self, m):
        v = m[self.asize*2:self.asize*3]
        if v == self._ah:
            raise RuntimeError("End of Chain")
        return int.from_bytes(v)
                
    def _mapCount(self, m):
        return int.from_bytes(m[self.asize*3:self.asize*3+1])
    
    def _mapDown(self, of, level):
        ''' Mapping down will bring you the very first item beyond that map '''
        m = self.sparse.mmap(of, 1)
        l = level
        while l > 0:
            m2 = self._mapAddr(m, 0)
            m.close()
            m = m2
        ret = self._mapItem(m, 0)
        m.close()
        return ret
