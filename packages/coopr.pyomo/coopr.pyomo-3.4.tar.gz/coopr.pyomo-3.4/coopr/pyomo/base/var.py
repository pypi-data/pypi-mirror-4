#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Var', 'VarList', '_VarData']

import logging
import types
import sys
import weakref
from six import iteritems, iterkeys, itervalues

import pyutilib.math
import pyutilib.misc
from pyutilib.enum import Enum

from coopr.pyomo.base.numvalue import NumericValue, value, as_numeric, is_fixed
from coopr.pyomo.base.set_types import BooleanSet, IntegerSet, Reals
from coopr.pyomo.base.component import Component, ComponentData, register_component
from coopr.pyomo.base.indexed_component import IndexedComponent
from coopr.pyomo.base.misc import apply_indexed_rule
from coopr.pyomo.base.misc import create_name
from coopr.pyomo.base.sets import Set, _SetContainer
from coopr.pyomo.base.util import isfunctor

try:
    xrange = xrange
except:
    xrange = range

logger = logging.getLogger('coopr.pyomo')

class _VarData(ComponentData, NumericValue):
    """
    This class defines the data for a single variable.

    Constructor Arguments:
        name        The name of this variable.  Use None for a default value.
        domain      The domain of this variable.  Use None for a default value.
        component   The Var object that owns this data.

    Public Class Attributes:
        active      If True, then this variable is active in the model.
        domain      The domain of this variable.
        fixed       If True, then this variable is treated as a fixed constant in the model.
        initial     The default initial value for this variable.
        lb          A lower bound for this variable.  The lower bound can be either 
                        numeric constants, parameter values, expressions or any object that 
                        can be called with no arguments.
        ub          A upper bound for this variable.  The upper bound can be either 
                        numeric constants, parameter values, expressions or any object that 
                        can be called with no arguments.
        name        A text string that provides an easy-to-read representation of the
                        variable/index pair (e.g. var[x,y,z])
        stale       A Boolean indicating whether the value of this variable is legitimiate -
                    or, in other words, if it should be considered legitimate for purposes 
                    of reporting or other interrogation. 
        value       The numeric value of this variable.
    """

    __pickle_slots__ = ('value','domain','initial','active','lb','ub','fixed','stale')
    __slots__ = __pickle_slots__ + ( '__weakref__', )

    def __init__(self, component, domain):
        """
        Constructor
        """
        ComponentData.__init__(self, component)
        # The following three lines are equivalent to calling the
        # basic NumericValue constructor, i.e., as follows:
        # NumericValue.__init__(self, name, domain, None, False)
        self.domain = domain
        self.value = None
        #
        self.active = True
        self.fixed = False
        self.initial = None
        # IMPT: The type of the lower and upper bound attributes can either be atomic numeric types
        #       in Python, expressions, etc. Basically, they can be anything that passes an "is_fixed" test.
        self.lb = None
        self.ub = None

        self.stale = True


    def __getstate__(self):
        """
        This method must be defined because this class uses slots.
        """
        result = super(_VarData, self).__getstate__()
        for i in _VarData.__pickle_slots__:
            result[i] = getattr(self, i)
        return result

    # Note: because NONE of the slots on this class need to be edited,
    # we don't need to implement a specialized __setstate__ method, and
    # can quietly rely on the super() class's implementation.
    # def __setstate__(self, state):
    #     pass

    def __call__(self, exception=True):
        """Return the value of this object."""
        return self.value

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False

    def setlb(self, value):
        if value is None:
            self.lb = None
        else:
            if is_fixed(value):
                self.lb = value
            else:
                raise ValueError(
                    "Non-fixed input of type '%s' supplied as variable lower "
                    "bound - legal types must be fixed expressions or variables."
                    % (type(value),) )

    def setub(self, value):
        if value is None:
            self.ub = None
        else:
            if is_fixed(value):
                    self.ub = value
            else:
                raise ValueError(
                    "Non-fixed input of type '%s' supplied as variable upper "
                    "bound - legal types are fixed expressions or variables."
                    "parameters"
                    % (type(value),) )

    def is_fixed(self):
        if self.fixed:
            return True
        return False

    def is_constant(self):
        return False

    def polynomial_degree(self):
        if self.fixed:
            return 0
        return 1

    def is_binary(self):
        return self.component().is_binary(self.index())

    def is_integer(self):
        return self.component().is_integer(self.index())

    def is_continuous(self):
        return self.component().is_continuous(self.index())

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        ostream.write(str(self))

    def set_value(self, val):
        """Set the value of this numeric object, after validating its value."""
        if self._valid_value(val):
            self.value=val

    def _valid_value(self, value, use_exception=True):
        """
        Validate the value.  If use_exception is True, then raise an
        exception.
        """
        ans = value is None or self.domain is None or value in self.domain
        if not ans and use_exception:
            raise ValueError("Numeric value `%s` is not in domain %s"
                             % (value, self.domain))
        return ans

#
# Variable attributes:
#
# Single variable:
#
# x = Var()
# x.fixed = True
# x.domain = Reals
# x.name = "x"
# x.setlb(-1.0)
# x.setub(1.0)
# x.initial = 0.0
# x = -0.4
#
# Array of variables:
#
# y = Var(set1,set2,...,setn)
# y.fixed = True (fixes all variables)
# y.domain = Reals
# y.name = "y"
# y[i,j,...,k] (returns value of a given index)
#
# y[i,j,...,k].fixed
# y[i,j,...,k].lb()
# y[i,j,...,k].ub()
# y[i,j,...,k].initial
#

class Var(IndexedComponent):
    """A numeric variable, which may be defined over a index"""

    """
    Constructor Arguments:
        name        The name of this variable
        index       The index set that defines the distinct variables.
                        By default, this is None, indicating that there
                        is a single variable.
        domain      A set that defines the type of values that
                        each variable must be.
        default     A set that defines default values for this
                        variable.
        bounds      A rule for defining bounds values for this
                        variable.
        rule        A rule for setting up this variable with
                        existing model data
    """

    def __new__(cls, *args, **kwds):
        if cls != Var:
            return super(Var, cls).__new__(cls)
        if args == ():
            return _VarElement.__new__(_VarElement)
        else:
            return _VarArray.__new__(_VarArray)

    def __init__(self, *args, **kwd):
        # Default keyword values
        self._initialize = kwd.pop('initialize', None )
        self.domain = kwd.pop('within', Reals )
        self.domain = kwd.pop('domain', self.domain )
        self.bounds = kwd.pop('bounds', None )

        self._defer_domain = False

        #Handle within=not_pyomo_object 
        if not getattr(self.domain, 'virtual', False):
            if self.domain == [] or self.domain == set([]):
                raise ValueError("Attempting to set a variable's domain to an empty set")
            else: 
                from coopr.pyomo.base.rangeset import RangeSet
                if type(self.domain) is RangeSet:
                    self.bounds = (self.domain._start,self.domain._end)
                    domain_name = self.domain.name
                    self.domain = IntegerSet()
                    self.domain.name = domain_name
                elif type(self.domain) is _SetContainer:
                    if self.domain.initialize is None:
                        self._defer_domain = True
                    elif self.domain.initialize == []:
                        raise ValueError("Attempting to set a variable's domain to an empty Set")
                    else:
                        self._defer_domain = False
                        domain_name = self.domain.name
                        self.domain = self.domain.initialize
                        self.domain.sort()
                        if len(self.domain) != self.domain[-1] - self.domain[0] + 1:
                            raise ValueError("Attempting to set a variable's domain to an improperly formatted Set " \
                                           + "-- elements are missing or duplicates exist: {0}".format(self.domain))
                        elif not all(type(elt) is int for elt in self.domain):
                            raise ValueError("Attempting to set a veriable's domain to a Set with noninteger elements: {0}".format(self.domain))
                        else:
                            self.bounds = (self.domain[0],self.domain[-1])
                            self.domain = IntegerSet()
                            self.domain.name = domain_name
                elif type(self.domain) is list:
                    self.domain.sort()
                    if len(self.domain) != self.domain[-1] - self.domain[0] + 1:
                        raise ValueError("Attempting to set a variable's domain to an improperly formatted set " \
                                       + "-- elements are missing or duplicates exist: {0}".format(self.domain))
                    elif not all(type(elt) is int for elt in self.domain):
                        raise ValueError("Attempting to set a veriable's domain to a set with noninteger elements: {0}".format(self.domain))
                    else:
                        self.bounds = (self.domain[0],self.domain[-1])
                        domain_name = "[{0}..{1}]".format(self.domain[0],self.domain[-1])
                        self.domain = IntegerSet()
                        self.domain.name = domain_name
                elif type(self.domain) is set:
                    self.domain = list(self.domain) 
                    self.domain.sort()
                    if len(self.domain) != self.domain[-1] - self.domain[0] + 1:
                        raise ValueError("Attempting to set a variable's domain to an improperly formatted set " \
                                       + "-- elements are missing or duplicates exist: {0}".format(self.domain))
                    elif not all(type(elt) is int for elt in self.domain):
                        raise ValueError("Attempting to set a veriable's domain to a set with noninteger elements: {0}".format(self.domain))
                    else:
                        self.bounds = (self.domain[0],self.domain[-1])
                        domain_name = "[{0}..{1}]".format(self.domain[0],self.domain[-1])
                        self.domain = IntegerSet()
                        self.domain.name = domain_name
                elif type(self.domain) is xrange:
                    self.bounds = (self.domain[0],self.domain[-1])
                    domain_name = "[{0}..{1}]".format(self.bounds[0],self.bounds[-1])
                    self.domain = IntegerSet()
                    self.domain.name = domain_name

        kwd.setdefault('ctype', Var)

        IndexedComponent.__init__(self, *args, **kwd)

        # check to see if domains for individual _VarData objects are specified via a rule.
        if isfunctor(self.domain):
            self._domain_rule = self.domain
            self.domain = None # there is no general domain for the collection of variables.
        else:
            self._domain_rule = None # there is no domain rule!

        # cached for efficiency purposes - isinstance is not cheap. 
        # only truly valid if there is no domain rule specified.
        if self.domain is not None:
            self._is_binary = isinstance(self.domain, BooleanSet)
            # second case is required in the case of deferred domains (the set may not be constructed yet, so hasn't been translated to an IntegerSet)
            self._is_integer = isinstance(self.domain, IntegerSet) or (type(self.domain) is _SetContainer)
            self._is_continuous = not (self._is_binary or self._is_integer)
        else:
            self._is_binary = None
            self._is_integer = None
            self._is_continuous = None

        # the following are only applicable if a domain rule *has* been specified.
        self._binary_keys = []
        self._integer_keys = []
        self._continuous_keys = []

    def as_numeric(self):
        if None in self._data:
            return self._data[None]
        return self

    def is_indexed(self):
        return self._ndim > 0

    def is_expression(self):
        return False

    def is_relational(self):
        return False

    def keys(self):
        return self._data.keys()

    # sets the "stale" attribute of every var index to True.
    def flag_as_stale(self):
        for var_data in itervalues(self._data):
            var_data.stale = True

    # returns a dictionary of index-value pairs.
    def extract_values(self):
        ans = {}
        for index, varval in iteritems(self._data):
            ans[index] = varval.value
        return ans

    # takes as input a dictionary of index-value pairs.
    def store_values(self, new_values):
        for index, varval in iteritems(self._data):
            varval.value = new_values[index]
            varval.stale = False

    def is_binary(self, index):
        if self._domain_rule is None:
            return self._is_binary
        else:
            return index in self._binary_keys

    def is_integer(self, index):
        if self._domain_rule is None:
            return self._is_integer
        else:
            return index in self._integer_keys

    def is_continuous(self, index):
        if self._domain_rule is None:
            return self._is_continuous
        else:
            return index in self._continuous_keys

    def binary_keys(self):
        """ Returns the keys of all binary variables """
        if self._domain_rule is None:
            if self._is_binary:
                return self._data.keys()
            else:
                return []
        else:
            return self._binary_keys

    def integer_keys(self):
        """ Returns the keys of all integer variables """
        if self._domain_rule is None:
            if self._is_integer:
                return self._data.keys()
            else:
                return []
        else:
            return self._integer_keys

    def continuous_keys(self):
        """ Returns the keys of all continuous variables """
        if self._domain_rule is None:
            if self._is_continuous:
                return self._data.keys()
            else:
                return []
        else:
            return self._continuous_keys

    def __iter__(self):
        return iterkeys(self._data)

    def iterkeys(self):
        return iterkeys(self._data)

    def itervalues(self):
        return itervalues(self._data)

    def iteritems(self):
        return iteritems(self._data)

    def __contains__(self, ndx):
        return ndx in self._data

    def dim(self):
        return self._ndim

    def reset(self):
        for value in itervalues(self._data):
            value.set_value(value.initial)

    def __len__(self):
        return len(self._data)

    def __setitem__(self,ndx,val):
        if (len(self._index) == 1) and (None in self._index) and (ndx is not None): # a somewhat gory way to see if you have a singleton - the len()=1 check is needed to avoid "None" being passed illegally into set membership validation rules.
            # allow for None indexing if this is truly a singleton
            msg = "Cannot set an array value in singleton variable '%s'"
            raise KeyError(msg % self.cname())

        if ndx not in self._index:
            msg = "Cannot set the value of array variable '%s' with invalid " \
                  "index '%s'"
            raise KeyError(msg % ( self.cname(), str(ndx) ))

        if not self._valid_value(val,False):
            msg = "Cannot set variable '%s[%s]' with invalid value: %s"
            raise ValueError(msg % ( self.cname(), str(ndx), str(val) ))
        self._data[ndx].value = val
        self._data[ndx].stale = False

    def __getitem__(self,ndx):
        """This method returns a _VarData object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        try:
            return self._data[ndx]
        except KeyError: # thrown if the supplied index is hashable, but not defined.
            msg = "Unknown index '%s' in variable %s;" % (str(ndx), self.cname())
            if (isinstance(ndx, (tuple, list)) and len(ndx) != self.dim()):
                msg += "    Expecting %i-dimensional indices" % self.dim()
            else:
                msg += "    Make sure the correct index sets were used.\n"
                msg += "    Is the ordering of the indices correct?"
            raise KeyError(msg)
        except TypeError: # thrown if the supplied index is not hashable
            msg = sys.exc_info()[1]
            msg2 = "Unable to index variable %s using supplied index with " % self.cname()
            msg2 += str(msg)
            raise TypeError(msg2)

    def _add_indexed_member(self, ndx):
        # Check for domain rules
        if self._domain_rule is not None:
            domain = apply_indexed_rule( self, self._domain_rule,
                                         self._parent(), ndx )
            if isinstance(domain, BooleanSet):
                self._binary_keys.append(ndx)
            elif isinstance(domain, IntegerSet):
                self._integer_keys.append(ndx)
            else:
                self._continuous_keys.append(ndx)
        else:
            domain = self.domain

        self._data[ndx] = _VarData(self, domain)


    def construct(self, data=None):
        if __debug__:   #pragma:nocover
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Variable, name=%s, from data=%s", self.cname(), str(data))
        if self._constructed:
            return
        self._constructed=True
        #
        # Construct _VarData objects for all index values
        #
        if self._ndim > 0:

            for ndx in self._index:
                # Ignore a None index.  This occurs when an empty VarList is
                # created;  the empty implicit set has the None index.
                if ndx is not None: 
                    self._add_indexed_member(ndx)


        #
        # Define the _XXX_keys objects if domain isn't a rule;
        # they were defined individually above in the case of
        # a rule
        #
        if self._domain_rule is None:
            # **NOTE: In Py3k dict.keys() returns a dict_keys set-like object
            #         that can _NOT_ be pickled. 
            if isinstance(self.domain, BooleanSet):
                self._binary_keys = list(self._data.keys())
            elif isinstance(self.domain, IntegerSet):
                self._integer_keys = list(self._data.keys())
            else:
                self._continuous_keys = list(self._data.keys())

        #
        # Initialize values with a dictionary if provided
        #
        if self._initialize is not None:
            #
            # Initialize values with the _rule function if provided
            #
            if self._initialize.__class__ is types.FunctionType:
                for key in self._data:
                    if key is None:
                        val = self._initialize(self._parent())
                    else:
                        val = apply_indexed_rule( self, self._initialize,
                                                  self._parent(), key )
                    val = value(val)
                    self._valid_value(val, True)
                    self._data[key].value = self._data[key].initial = val
                    self._data[key].stale = False
            elif self._initialize.__class__ is dict:
                for key in self._initialize:
                    val = self._initialize[key]
                    self._valid_value(val, True)
                    self._data[key].value = self._data[key].initial = val
                    self._data[key].stale = False
            
            # BLN: The following is kind of a hack that John wrote
            # that allows you to initialize a variable with an object
            # which can be called. This is useful when you want to
            # initialize a variable using something like a map. It was
            # originally meant for the case of variables being indexed
            # by a differential set where you want to map any index in
            # the differential set to the appropriate finite
            # element. I dont currently use this anywhere but I
            # thought I'd commit it in case someone wanted to do
            # something similar in the future or make it less of a
            # hack. An example of the intended use is below:
            ########################
            #class mapToFE(object):
            #    def __init__(self, dataSource, diffSet, init=None, scale=1):
            #        self.dataSrc = dataSource
            #        self.diffSet = diffSet
            #        self.init = init
            #        self.scale = scale
            #    def __call__(self, model, point):
            #        if point == 0 and self.init is not None:
            #            ans = self.init
            #        else:
            #            ans = self.dataSrc[self.diffSet.get_upper_element_boundary(point)]
            #        return value(self.scale) * value(ans)
            #########################
            # elif hasattr(self._initialize, '__call__'):
            #     try:
            #         for key in self._data:
            #             if key is None:
            #                 val = self._initialize(self._parent())
            #             else:
            #                 val = apply_indexed_rule( self, self._initialize,
            #                                           self._parent(), key )
            #             val = value(val)
            #             self._valid_value(val, True)
            #             self._data[key].value = self._data[key].initial = val
            #             self._data[key].stale = False
            #     except:
            #         for key in self._data:
            #             val = self._initialize(self._parent())
            #             val = value(val)
            #             self._valid_value(val, True)
            #             self._data[key].value = self._data[key].initial = val
            #             self._data[key].stale = False
            else:
                for key in self._index:
                    val = self._initialize
                    self._valid_value(val, True)
                    self._data[key].value = self._data[key].initial = val
                    self._data[key].stale = False                    
        #
        # Initialize bounds with the bounds function if provided
        #
        if self.bounds is not None:

            if type(self.bounds) is tuple:

                # bounds are specified via a tuple - same lower and upper bounds for all var values!

                (lb, ub) = self.bounds

                # do some simple validation that the bounds are actually finite - otherwise, set them to None.
                if (lb is not None) and (not pyutilib.math.is_finite(value(lb))):
                    lb = None
                if (ub is not None) and (not pyutilib.math.is_finite(value(ub))):
                    ub = None

                for key,varval in iteritems(self._data):
                    if lb is not None:
                        varval.setlb(lb)
                    if ub is not None:
                        varval.setub(ub)

            else:

                # bounds are specified via a function

                for index, varval in iteritems(self._data):
                    if index is None:
                        (lb, ub) = self.bounds(self._parent())
                    else:
                        (lb, ub) = apply_indexed_rule( self, self.bounds,
                                                       self._parent(), index )
                    varval.setlb(lb)
                    varval.setub(ub)

                for varval in itervalues(self._data):
                    if varval.lb is not None and not pyutilib.math.is_finite(value(varval.lb)):
                        varval.setlb(None)
                    if varval.ub is not None and not pyutilib.math.is_finite(value(varval.ub)):
                        varval.setub(None)
        #
        # Iterate through all variables, and tighten the bounds based on
        # the domain bounds information.
        #
        # Only done if self.domain is not a rule. If it is, _VarArray level
        # bounds become meaningless, since the individual _VarElement objects
        # likely have more restricted domains.
        #
        if self._domain_rule is None:
            dbounds = self.domain.bounds()
            if not dbounds is None and dbounds != (None,None):
                for varval in itervalues(self._data):
                    if not dbounds[0] is None:
                        if varval.lb is None or                     \
                           dbounds[0] > value(varval.lb):
                            varval.setlb(dbounds[0])

                    if not dbounds[1] is None:
                        if varval.ub is None or                     \
                            dbounds[1] < value(varval.ub):
                            varval.setub(dbounds[1])

    def fix_all(self):
        for key in self:
            self[key].fixed = True

    def unfix_all(self):
        for key in self:
            self[key].fixed = False

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:
            ostream = sys.stdout
        ostream.write("   "+self.cname()+" : ")
        if not self.doc is None:
            ostream.write(self.doc+'\n')
            ostream.write("  ")
        ostream.write("\tSize="+str(len(self))+" ")
        if self.domain is not None:
            ostream.write("\tDomain="+self.domain.name+"\n")
        else:
            ostream.write("\tDomain=None\n")
        if self._index_set is not None:
            ostream.write("\tIndicies:  ")
            for idx in self._index_set:
                ostream.write(str(idx.name)+",  ")
            ostream.write('\n')
        if None in self._data:
            ostream.write("\tInitial Value : Lower Bound : Upper Bound : "  \
                             "Current Value: Fixed: Stale\n")
            lb_value = None
            if self._data[None].lb is not None:
                lb_value = value(self._data[None].lb)
            ub_value = None
            if self._data[None].ub is not None:
                ub_value = value(self._data[None].ub)

            ostream.write("\t %s : %s : %s : %s : %s : %s\n" % (
              str(self._data[None].initial),
              str(lb_value),
              str(ub_value),
              str(self._data[None].value),
              str(self._data[None].fixed),
              str(self._data[None].stale)
            ))
        else:
            ostream.write("\tKey : Initial Value : Lower Bound : "          \
                             "Upper Bound : Current Value: Fixed: Stale\n")
            for key in sorted(self._data.keys()):
                initial_val = self._data[key].initial
                lb_value = None
                if self._data[key].lb is not None:
                    lb_value = value(self._data[key].lb)
                ub_value = None
                if self._data[key].ub is not None:
                    ub_value = value(self._data[key].ub)

                ostream.write("\t%s : %s : %s : %s : %s : %s : %s\n" % (
                  str(key),
                  str(initial_val),
                  str(lb_value),
                  str(ub_value),
                  str(value(self._data[key].value)),
                  str(value(self._data[key].fixed)),
                  str(self._data[key].stale)
                ))

    def display(self, prefix="", ostream=None):
        if ostream is None:
            ostream = sys.stdout
        ostream.write(prefix+"Variable "+self.cname()+" : ")
        ostream.write("Size="+str(len(self))+' ')
        ostream.write("Domain="+self.domain.name+'\n')
        if None in self._data:
            ostream.write("%s  Value=%s\n" % (
              prefix,
              pyutilib.misc.format_io(self._data[None].value)
            ))
        else:
            for key in self._data:
                val = self._data[key].value
                ostream.write(prefix+"  "+str(key)+" : "+str(val)+'\n')

# a _VarElement is the implementation representing a "singleton" or non-indexed variable.
# NOTE: this class derives from both a "slot"ized base class (_VarData) and a normal
#       class with a dictionary (Var) - beware (although I believe the __getstate__
#       implementation should be attribute-independent).

class _VarElement(Var, _VarData):

    def __init__(self, *args, **kwd):
        _VarData.__init__( self, self,
                           kwd.get('within', kwd.get('domain', Reals)) )
        Var.__init__(self, *args, **kwd)
        self._data[None] = self

    def __call__(self, exception=True):
        if None in self._data:
            return self._data[None].value
        return None

    # Since this class derives from Component and Component.__getstate__
    # just packs up the entire __dict__ into the state dict, there s
    # nothng special that we need to do here.  We will just defer to the
    # super() get/set state.  Since all of our get/set state methods
    # rely on super() to traverse the MRO, this will automatically pick
    # up both the Component and Data base classes.
    #
    #def __getstate__(self):
    #    pass
    #
    #def __setstate__(self, state):
    #    pass

    def is_constant(self):
        return _VarData.is_constant(self)

# a _VarArray is the implementation representing an indexed variable.

class _VarArray(Var):
    
    def __init__(self, *args, **kwds):
        Var.__init__(self, *args, **kwds)
        self._dummy_val = _VarData(
            self, kwds.get('within', kwds.get('domain', Reals)) )

    def __float__(self):
        raise TypeError("Cannot access the value of array variable "+self.cname())

    def __int__(self):
        raise TypeError("Cannot access the value of array variable "+self.cname())

    def _valid_value(self,value,use_exception=True):
        return self._dummy_val._valid_value(value, use_exception)

    def set_value(self, value):
        msg = "Cannot specify the value of array variable '%s'"
        raise ValueError(msg % self.cname())


class VarList(_VarArray):
    """
    Variable-length indexed variable objects used to construct Pyomo models.
    """

    End = ( 1003, )

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            raise ValueError("Cannot specify indices for a VarList object")
        # Construct parents...
        self._hidden_index = Set()
        _VarArray.__init__(self, self._hidden_index, **kwargs)
        self._ndim = 1
        self._nvars = 0

    def is_fixed(self):
        if self._nvars == 0:
            return False
        for idx in xrange(self._nvars):
            if not self[idx].is_fixed():
                return False
        return True

    def is_constant(self):
        return False

    def polynomial_degree(self):
        if self.is_fixed():
            return 0
        return 1

    def construct(self, data=None):
        if __debug__:
            logger.debug("Constructing variable list %s",self.cname())
        self._hidden_index.construct()
        _VarArray.construct(self, data)

    def add(self):
        self._hidden_index.add(self._nvars)
        self._add_indexed_member(self._nvars)
        self._nvars += 1
        return self[self._nvars-1]


register_component(Var, "Decision variables in a model.")
register_component(VarList, "Variable-length list of decision variables in a model.")

