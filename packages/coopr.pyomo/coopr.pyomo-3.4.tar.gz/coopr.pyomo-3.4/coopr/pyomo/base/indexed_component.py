#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['IndexedComponent']

from six import iterkeys, itervalues, iteritems

from coopr.pyomo.base.component import Component
from coopr.pyomo.base.sets import Set


def process_setarg(arg):
    """
    Process argument and return an associated set object.
    """
    if isinstance(arg,Set):
        # Argument is a Set instance
        return arg
    elif isinstance(arg,Component):
        raise TypeError("Cannot index a component with a non-set component")
    else:
        try:
            # Argument has set_options attribute, which is used to initialize the set
            options = getattr(arg,'set_options')
            options['initialize'] = arg
            return Set(**options)
        except:
            pass
    # Argument is assumed to be an initialization function
    return Set(initialize=arg)


class IndexedComponent(Component):
    """
    This is the base class for all indexed modeling components.

    Constructor arguments:
        ctype       The class type for the derived subclass
        doc         A text string describing this component

    Private class attributes:
        _data       A dictionary from the index set to component data objects
        _index      The set of valid indices
        _index_set  A tuple of set objects that represents the index set
        _ndim       The dimension of the index set
    """

    def __init__(self, *args, **kwds):
        Component.__init__(self, **kwds)
        #
        self._data = {}
        #
        if args == ():
            #
            # If no indexing sets are provided, generate a dummy index
            #
            self._index = {None:None}
            self._index_set = None
            self._ndim = 0
        elif len(args) == 1:
            #
            # If a single argument is provided, the define the index using that
            # argument
            #
            self._index = process_setarg(args[0])
            self._index_set = None
            #
            # Compute the dimension of the indexing sets
            #
            self._compute_dim()
        else:
            #
            # If multiple arguments are provided, define _index_set with a tuple
            # of set objects
            #
            self._index = {}
            self._index_set=tuple( process_setarg(arg) for arg in args )
            #
            # Compute the dimension of the indexing sets
            #
            self._compute_dim()

    def clear(self):
        """Clear the data in this component"""
        self._data = {}

    def __len__(self):
        return len(self._data)

    def __contains__(self, ndx):
        return ndx in self._data

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __iter__(self):
        return self._data.__iter__()

    def iteritems(self):
        return iteritems(self._data)

    def iterkeys(self):
        return iterkeys(self._data)

    def itervalues(self):
        return itervalues(self._data)

    def __getitem__(self, ndx):
        """
        This method returns the data corresponding to the given index.
        """
        if ndx in self._data:
            return self._data[ndx]
        raise KeyError("Unknown index in component '%s': %s" % ( self.name, str(ndx) ))

    def index_set(self):
        """Return the index set"""
        return self._index

    def is_indexed(self):
        """Return true if this component is indexed"""
        return self._ndim > 0

    def dim(self):
        """Return the dimension of the index"""
        return self._ndim

    def _compute_dim(self):
        """Compute the dimension of the set"""
        if self._index_set is None:
            # A single index set
            #if type(self._index) is dict:
            #    # If the index set is dictionary, then the argument list was empty
            #    self._ndim = 0
            #else:
            #    # If the index set is Pyomo Set, then use its dimen attribute
            self._ndim = self._index.dimen
        else:
            # A multi-set index
            self._ndim = 0
            for iset in self._index_set:
                # Each index set is a Pyomo Set, so use its dimen attribute
                self._ndim += iset.dimen

