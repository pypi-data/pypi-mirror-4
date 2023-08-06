#!/usr/bin/env python
""" Partitioning of a constant list of four members.

References:

[PartOfASet_WP]: Wikipedia entry Partition_of_a_set at
    http://en.wikipedia.org/wiki/Partition_of_a_set

"""

from __future__ import print_function
from partitionsets import ordered_set
from partitionsets import partition

A_LIST = 'red green yellow blue'.split(" ")
AN_OSET = ordered_set.OrderedSet(A_LIST)
A_PARTITION = partition.Partition(AN_OSET)
for a_part in A_PARTITION:
    print (a_part)
