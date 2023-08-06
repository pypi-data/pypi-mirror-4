#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['RangeSet']

import math
import itertools

from coopr.pyomo.base.sets import _SetContainer
from coopr.pyomo.base.expr import Expression
from coopr.pyomo.base.set_types import Integers, Reals
from coopr.pyomo.base.misc import apply_indexed_rule
from coopr.pyomo.base.numvalue import value
from coopr.pyomo.base.component import register_component

try:
    xrange = xrange
except:
    xrange = range


def count(start=0, step=1):
    n = start
    while True:
        yield n
        n += step


class RangeSetValidator(object):

    def __init__(self, start, end, step):
        self.start=start
        self.end=end
        self.step=step

    def __call__(self, model, val):
        if not type(val) in [int, float, long]:
            return False
        if val + 1e-7 < self.start:
            return False
        if val > self.end+1e-7:
            return False
        if type(self.start) is int and type(self.end) is int and type(self.step) is int and (val-self.start)%self.step != 0:
            return False
        return True


class RangeSet(_SetContainer):
    """A set that represents a list of numeric values"""

    def __init__(self,*args,**kwds):
        """Construct a list of integers"""
        tmp=()
        _SetContainer.__init__(self,*tmp,**kwds)
        if len(args) == 0:
            raise RuntimeError("Attempting to construct a RangeSet object with no arguments!")

        self._type=RangeSet
        if len(args) == 1:
            self._start=1
            self._end=args[0]
            self._step=1
        elif len(args) == 2:
            self._start=args[0]
            self._end=args[1]
            self._step=1
        else:
            self._start=args[0]
            self._end=args[1]
            self._step=args[2]
        self.ordered=True
        self.value = None
        self.virtual = True
        self.concrete = True
        self._len = 0

    def construct(self, values=None):
        if self._constructed:
            return
        self._constructed=True
        if isinstance(self._start,Expression):
            self._start_val = self._start()
        else:
            self._start_val = value(self._start)

        if isinstance(self._end,Expression):
            self._end_val = self._end()
        else:
            self._end_val = value(self._end)

        if isinstance(self._step,Expression):
            self._step_val = self._step()
        else:
            self._step_val = value(self._step)

        if type(self._start_val) is int and type(self._step) is int and type(self._end_val) is int:
            self.domain = Integers
        else:
            self.domain = Reals
        lb = self._start_val

        if self.filter is None and self.validate is None:
            self._len = int(math.floor((self._end_val-self._start_val+self._step_val+1e-7)//self._step_val))
            ub = self._start_val + (self._len-1)*self._step_val
        else:
            ub = self._start_val
            ctr=0
            for i in self:
                ub = i
                ctr += 1
            self._len = ctr
        self._bounds = (lb,ub)

    def __len__(self):
        return self._len

    def __iter__(self):
        if not self._constructed:
            raise RuntimeError("A RangeSet class must be initialized before a user can iterate over its elements.")
        if self.filter is None and self.validate is None:
            #for i in itertools.islice(count(), (self._end_val-self._start_val+self._step_val+1e-7)//self._step_val):
            for i in xrange(int((self._end_val-self._start_val+self._step_val+1e-7)//self._step_val)):
                yield self._start_val + i*self._step_val
        else:
            #for i in itertools.islice(count(), (self._end_val-self._start_val+self._step_val+1e-7)//self._step_val):
            for i in xrange(int((self._end_val-self._start_val+self._step_val+1e-7)//self._step_val)):
                val = self._start_val + i*self._step_val
                if not self.filter is None and not apply_indexed_rule(self, self.filter, self._parent(), val):
                    continue
                if not self.validate is None and not apply_indexed_rule(self, self.validate, self._parent(), val):
                    continue
                yield val

    def data(self):
        """The underlying set data."""
        return set(self)

    def first(self):
        return self._bounds[0]

    def last(self):
        return self._bounds[1]

    def member(self, key):
        if key >= 1:
            if key > self._len:
                raise IndexError("Cannot index a RangeSet past the last element")
            return self._start_val + (key-1)*self._step_val
        elif key < 0:
            if self._len+key < 0:
                raise IndexError("Cannot index a RangeSet past the first element")
            return self._start_val + (self._len+key)*self._step_val
        else:
            raise IndexError("Valid index values for sets are 1 .. len(set) or -1 .. -len(set)")

    def __eq__(self, other):
        """ Equality comparison """
        if other is None:
            return False
        other = self._set_repn(other)
        if self.dimen != other.dimen:
            return False
        ctr = 0
        for i in other:
            if not i in self:
                return False
            ctr += 1
        return ctr == len(self)

    def _set_contains(self, element):
        # As the test for type -- or conversion to float -- is
        # expensive, we will work on the assumption that folks will "do
        # the right thing"... and let system exceptions handle the case
        # where they do not.
        
        #if not type(element) in [int,float]:
        #    return False
        try:
            x = element - self._start_val
            if x % self._step_val != 0:
                # If we are doing floating-point arithmetic, there is a
                # chance that we are seeing roundoff error...
                if math.fabs((x + 1e-7) % self._step_val) > 2e-7:
                    return False
            if element < self._bounds[0] or element > self._bounds[1]:
                return False
        except:
            return False
        if self.filter is not None and not self.filter(element):
            return False
        if self.validate is not None and not self.validate(self, element):
            return False
        return True


register_component(RangeSet, "A sequence of numeric values.  RangeSet(start,end,step) is a sequence starting a value 'start', and increasing in values by 'step' until a value greater than or equal to 'end' is reached.")

