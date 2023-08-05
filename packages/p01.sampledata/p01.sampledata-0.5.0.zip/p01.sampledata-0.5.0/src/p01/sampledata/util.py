###############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""

import types


class EventlessOrderedContainer(object):
    """Eventless container maintains entries' order as added
    
    This container is only used as sampledata storage and allows to use integer
    or anything else as keys.
    """

    def __init__(self):
        self._data = {}
        self._order = []

    def keys(self):
        """ See `IOrderedContainer`."""
        return self._order[:]

    def __iter__(self):
        """ See `IOrderedContainer`."""
        return iter(self.keys())

    def __getitem__(self, key):
        """ See `IOrderedContainer`."""
        return self._data[key]

    def get(self, key, default=None):
        """ See `IOrderedContainer`."""
        return self._data.get(key, default)

    def values(self):
        """ See `IOrderedContainer`."""
        return [self._data[i] for i in self._order]

    def __len__(self):
        """ See `IOrderedContainer`."""
        return len(self._data)

    def items(self):
        """ See `IOrderedContainer`."""
        return [(i, self._data[i]) for i in self._order]

    def __contains__(self, key):
        """ See `IOrderedContainer`."""
        return self._data.has_key(key)

    has_key = __contains__

    def add(self, obj):
        assert obj.__name__ is not None
        self[obj.__name__] = obj

    def __setitem__(self, key, obj):
        """ See `IOrderedContainer`."""
        # We have to first update the order, so that the item is available,
        # otherwise most API functions will lie about their available values.
        if not self._data.has_key(key):
            self._order.append(key)

        self._data[key] = obj
        # only set __name__ if not given, this allows to use a different
        # key as the given __name__
        if hasattr(obj, '__name__') and obj.__name__ is None:
            obj.__name__ = key

        return key

    def __delitem__(self, key):
        """ See `IOrderedContainer`."""
        del self._data[key]
        self._order.remove(key)

    def updateOrder(self, order):
        """ See `IOrderedContainer`."""

        if not isinstance(order, types.ListType) and \
            not isinstance(order, types.TupleType):
            raise TypeError('order must be a tuple or a list.')

        if len(order) != len(self._order):
            raise ValueError("Incompatible key set.")

        was_dict = {}
        will_be_dict = {}
        new_order = []

        for i in range(len(order)):
            was_dict[self._order[i]] = 1
            will_be_dict[order[i]] = 1
            new_order.append(order[i])

        if will_be_dict != was_dict:
            raise ValueError("Incompatible key set.")

        self._order = new_order
