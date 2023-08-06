#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = [
  '_VirtualSet', '_AnySet', 'RealSet', 'IntegerSet', 'BooleanSet', 'Any',
  'Reals', 'PositiveReals', 'NonPositiveReals', 'NegativeReals',
  'NonNegativeReals', 'PercentFraction', 'Integers', 'PositiveIntegers',
  'NonPositiveIntegers', 'NegativeIntegers', 'NonNegativeIntegers', 'Boolean',
  'Binary'
]

import sys
import weakref
from six import iteritems

import pyutilib.component.core

from coopr.pyomo.base.sets import _SetContainer
from coopr.pyomo.base.plugin import *

try:
    long
    numlist = (int, float, long)
except:
    numlist = (int, float)


_virtual_sets = []

class _VirtualSet(_SetContainer, pyutilib.component.core.Plugin):
    """
    A set that does not contain elements, but instead overrides the
       __contains__ method to define set membership.
    """

    pyutilib.component.core.implements(IPyomoSet)

    def __init__(self,*args,**kwds):
        if "name" in kwds:
            pyutilib.component.core.Plugin.__init__(self,name=kwds["name"])
        else:
            pyutilib.component.core.Plugin.__init__(self)
        self._class_override=False
        _SetContainer.__init__(self,*args,**kwds)
        self.virtual=True
        self.concrete=False
        
        global _virtual_sets
        _virtual_sets.append(self)

    def __getstate__(self):
        # TBD: JDS: Is this test needed???
        if '_parent' in self.__dict__.keys() and self._parent is not None and type(self._parent) == weakref.ref:
            self._parent = self._parent()
        return self.__dict__
    
    def __setstate__(self, state):
        for (slot_name, value) in iteritems(state):
            self.__dict__[slot_name] = value


class _AnySet(_VirtualSet):
    """A virutal set that allows any value"""

    def __init__(self,*args,**kwds):
        """Constructor"""
        _VirtualSet.__init__(self,*args,**kwds)

    def __contains__(self, element):
        if element is None:
            return False
        return True


class RealSet(_VirtualSet):
    """A virutal set that represents real values"""

    def __init__(self,*args,**kwds):
        """Constructor"""
        if not 'bounds' in kwds:
            kwds['bounds'] = (None,None)
        _VirtualSet.__init__(self,*args,**kwds)


    def __contains__(self, element):
        """Report whether an element is an 'int', 'long' or 'float' value.

        (Called in response to the expression 'element in self'.)
        """
        return _VirtualSet.__contains__(self, element)                        \
                     and ( type(element) in numlist)


class IntegerSet(_VirtualSet):
    """A set that represents integer values"""

    def __init__(self,*args,**kwds):
        """Constructor"""
        if not 'bounds' in kwds:
            kwds['bounds'] = (None,None)
        _VirtualSet.__init__(self,*args,**kwds)

    def __contains__(self, element):
        """Report whether an element is an 'int'.

        (Called in response to the expression 'element in self'.)
        """
        return _VirtualSet.__contains__(self, element)                        \
                   and ( type(element) in (int,) )


class BooleanSet(_VirtualSet):
    """A set that represents boolean values"""

    def __init__(self,*args,**kwds):
        """Construct the set of booleans, which contains no explicit values"""
        kwds['bounds'] = (0,1)
        _VirtualSet.__init__(self,*args,**kwds)

    def __contains__(self, element):
        """Report whether an element is a boolean.

        (Called in response to the expression 'element in self'.)
        """
        return _VirtualSet.__contains__(self, element) \
               and ( type(element) in (bool,int,str) ) \
               and ( element in (0, 1, True, False, 'True', 'False', 'T', 'F') )

#
# Concrete instances of the standard sets
#
Any=_AnySet(name="Any", doc="A set of any data")

Reals=RealSet(name="Reals", doc="A set of real values")
def validate_PositiveValues(model,x):    return x >  0
def validate_NonPositiveValues(model,x): return x <= 0
def validate_NegativeValues(model,x):    return x <  0
def validate_NonNegativeValues(model,x): return x >= 0
def validate_PercentFraction(model,x):   return x >= 0 and x <= 1.0

PositiveReals    = RealSet(
  name="PositiveReals",
  validate=validate_PositiveValues,
  doc="A set of positive real values",
  bounds=(0, None)
)
NonPositiveReals = RealSet(
  name="NonPositiveReals",
  validate=validate_NonPositiveValues,
  doc="A set of non-positive real values",
  bounds=(None, 0)
)
NegativeReals    = RealSet(
  name="NegativeReals",
  validate=validate_NegativeValues,
  doc="A set of negative real values",
  bounds=(None, 0)
)
NonNegativeReals = RealSet(
  name="NonNegativeReals",
  validate=validate_NonNegativeValues,
  doc="A set of non-negative real values",
  bounds=(0, None)
)

PercentFraction = RealSet(
  name="PercentFraction",
  validate=validate_PercentFraction,
  doc="A set of real values in the interval [0,1]",
  bounds=(0.0,1.0)
)

Integers            = IntegerSet(
  name="Integers",
  doc="A set of integer values"
)
PositiveIntegers    = IntegerSet(
  name="PositiveIntegers",
  validate=validate_PositiveValues,
  doc="A set of positive integer values",
  bounds=(1, None)
)
NonPositiveIntegers = IntegerSet(
  name="NonPositiveIntegers",
  validate=validate_NonPositiveValues,
  doc="A set of non-positive integer values",
  bounds=(None, 0)
)
NegativeIntegers    = IntegerSet(
  name="NegativeIntegers",
  validate=validate_NegativeValues,
  doc="A set of negative integer values",
  bounds=(None, -1)
)
NonNegativeIntegers = IntegerSet(
  name="NonNegativeIntegers",
  validate=validate_NonNegativeValues,
  doc="A set of non-negative integer values",
  bounds=(0, None)
)

Boolean = BooleanSet( name="Boolean", doc="A set of boolean values")
Binary  = BooleanSet( name="Binary",  doc="A set of boolean values")
