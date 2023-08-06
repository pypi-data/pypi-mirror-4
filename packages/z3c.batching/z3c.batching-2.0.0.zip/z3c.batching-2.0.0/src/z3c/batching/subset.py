##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Batching Implementation for subsets. Sometimes subsets
can have pre batched values"""
from z3c.batching.batch import Batch, Batches


class EmptyBatch(Batch):

    def __init__(self, length, start, size, batches):
        self.update(length, start, size)
        self.batches = batches

    def __eq__(self, other):
        return ((self.size, self.start, self._length) ==
                (other.size, other.start, other._length))

    @property
    def firstElement(self):
        raise ValueError("EmptyBatch holds no item")

    @property
    def lastElement(self):
        raise ValueError("EmptyBatch holds no item")

    def __getitem__(self, key):
        raise ValueError("EmptyBatch holds no item")

    def __iter__(self):
        raise ValueError("EmptyBatch holds no item")


class SubsetBatches(Batches):

    def __init__(self, batch):
        super(SubsetBatches, self).__init__(batch)
        self.length = batch._length

    def __getitem__(self, key):
        if key not in self._batches:
            if key < 0:
                key = self.total + key

            batch = EmptyBatch(
                self.length, key * self.size, self.size, self)
            self._batches[batch.index] = batch

        try:
            return self._batches[key]
        except KeyError:
            raise IndexError(key)


class SubsetBatch(Batch):

    def __init__(self, sequence, length, start=0, size=20, batches=None):
        self.sequence = sequence
        self.update(length, start, size)
        self.updateBatches(batches)

    def updateBatches(self, batches):
        if batches is None:
            batches = SubsetBatches(self)

        self.batches = batches

    @property
    def firstElement(self):
        """See interfaces.IBatch"""
        return self.sequence[0]

    @property
    def lastElement(self):
        """See interfaces.IBatch"""
        return self.sequence[-1]

    def __getitem__(self, key):
        """See zope.interface.common.sequence.IMinimalSequence"""
        if isinstance(key, slice):
            return self.__getslice__(key.start, key.stop)
        if key >= self._trueSize:
            raise IndexError('batch index out of range')
        return self.sequence[key]

    def __iter__(self):
        """See zope.interface.common.sequence.IMinimalSequence"""
        return iter(self.sequence)

    def __eq__(self, other):
        return ((self.size, self.start, self._length) ==
                (other.size, other.start, other._length))
